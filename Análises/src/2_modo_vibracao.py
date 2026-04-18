import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
from scipy.interpolate import interp1d
import os
import datetime

# ==========================================
# 1. CARREGAMENTO DOS DADOS
# ==========================================
caminho_arquivo = r"C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\data\carga_constante\17-04-26\P2_d3.txt" 
df = pd.read_csv(caminho_arquivo, sep='\s+', decimal=',', header=None, names=['tempo', 'deslocamento'])

tempo = df['tempo'].values
deslocamento = df['deslocamento'].values

# ==========================================
# 2. PRÉ-PROCESSAMENTO (INTERPOLAÇÃO PARA FFT)
# ==========================================
# A FFT exige amostragem uniforme. Vamos criar um novo vetor de tempo regular.
fs_estimada = 1.0 / np.mean(np.diff(tempo))  
tempo_uniforme = np.linspace(tempo.min(), tempo.max(), len(tempo))
dt = tempo_uniforme[1] - tempo_uniforme[0]
fs = 1.0 / dt

# Interpolação para garantir que os pontos estejam igualmente espaçados
f_interp = interp1d(tempo, deslocamento, kind='cubic') 
deslocamento_uniforme = f_interp(tempo_uniforme)

# Remoção do nível DC (média) para evitar um pico gigante em 0 Hz
deslocamento_centrado = deslocamento_uniforme - np.mean(deslocamento_uniforme)

# ==========================================
# 3. FFT TRADICIONAL E DETECÇÃO FISICAMENTE EMBASADA
# ==========================================
N = len(tempo_uniforme)
yf = fft(deslocamento_centrado)
xf = fftfreq(N, dt)

print(f"Número N de amostras: {N}")
print(f"Freqüência de amostragem estimada: {fs:.2f} Hz")

# Pegamos apenas a metade positiva do espectro
frequencias_hz = xf[:N//2] 
# Amplitude normalizada: (2/N) para converter para a unidade real do deslocamento
amplitude = (2.0 / N) * np.abs(yf[:N//2])

# --- LÓGICA DE DISTANCIAMENTO FÍSICO COERENTE ---
# 1. Qual é a resolução real da sua FFT? (Hertz por ponto)
resolucao_fft = 1.0 / (N * dt) 
print(f"Resolução da FFT: {resolucao_fft:.4f} Hz/ponto") 

# 2. Defina a distância física mínima coerente (Ex: Modos não podem estar a menos de 1 Hz de distância)
separacao_minima_hz = 1.0

# 3. Calcule quantos "índices" isso representa arredondando para o número inteiro mais próximo
distancia_indices = int(separacao_minima_hz / resolucao_fft)

print("--- PARÂMETROS DA FFT ---")
print(f"Resolução da FFT: {resolucao_fft:.4f} Hz/ponto")
print(f"Distância aplicada no filtro: {distancia_indices} pontos (Representando {separacao_minima_hz} Hz)\n")

# 4. Aplique no algoritmo (Limiar ajustado para 2% para detectar modos de alta dissipação)
picos_indices, _ = find_peaks(amplitude, height=np.max(amplitude)*0.02, distance=distancia_indices)
frequencias_modos = frequencias_hz[picos_indices]

# ==========================================
# 4. PLOTAGEM E SALVAMENTO DOS RESULTADOS
# ==========================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Gráfico 1: Domínio do Tempo
ax1.plot(tempo_uniforme, deslocamento_centrado, '-', color='tab:blue', label='Interpolado (Uniforme)')
ax1.set_title('Sinal no Domínio do Tempo')
ax1.set_xlabel('Tempo (s)')
ax1.set_ylabel('Deslocamento')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Gráfico 2: Espectro de Amplitude (FFT)
ax2.plot(frequencias_hz, amplitude, color='tab:red')
ax2.plot(frequencias_hz[picos_indices], amplitude[picos_indices], "x", color='black', markersize=10)
ax2.set_title('Espectro de Amplitude via FFT Tradicional')
ax2.set_xlabel('Frequência (Hz)')
ax2.set_ylabel('Amplitude (Unidade Original)')
ax2.set_xlim(0, fs/2) # Limite de Nyquist
ax2.grid(True, alpha=0.3)

# Anotando as frequências no gráfico
for freq in frequencias_modos:
    amp_pico = amplitude[np.where(frequencias_hz == freq)[0][0]]
    ax2.annotate(f'{freq:.3f} Hz', 
                 xy=(freq, amp_pico), 
                 xytext=(5, 10), textcoords='offset points', 
                 fontweight='bold')

plt.tight_layout()

# --- SALVANDO A IMAGEM ANTES DE MOSTRAR ---
pasta_resultados = r'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\2_modo_vibracao'
if not os.path.exists(pasta_resultados):
    os.makedirs(pasta_resultados)

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
nome_arquivo = os.path.join(pasta_resultados, f'fft_tradicional_{timestamp}.png')

fig.savefig(nome_arquivo, dpi=300, bbox_inches='tight')

plt.show()

# ==========================================
# 5. RESULTADOS NO TERMINAL
# ==========================================
print("\n--- RESULTADOS DA ANÁLISE FFT ---")
for i, freq in enumerate(frequencias_modos):
    amp = amplitude[picos_indices[i]]
    print(f"Modo {i+1}: Frequência = {freq:.4f} Hz | Amplitude = {amp:.8f}")