# -*- coding: utf-8 -*-  # Permite caracteres como 'ç', 'á', 'µ' no arquivo

"""
Created on Tue Feb 25 15:23:44 2025

@author: Adm
"""
# Objetivo: analisar vibrações e estimar a frequência natural do sistema
# (ex.: balança de microempuxo) + opção de filtrar o sinal para redução de ruído.

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq
import pandas as pd
from scipy import signal

# ======= Parâmetros de entrada e de filtragem =======
Filename='5.caldata_m4_l5_F9,725.txt'  # arquivo de dados a ser analisado (TAB-separado)
filtering=True                          # se True, aplica filtro passa-baixas
cutofffreq=0.02                         # frequência de corte do filtro (Hz)
order=5                                 # ordem do filtro Butterworth

MaxF=5  # frequência máxima (Hz) para exibir no gráfico de FFT (corta o espectro)

# ======= Leitura e pré-processamento =======
# Listas vazias para tempo (time) e deslocamento (d):
time = []
d = []

# Lê o arquivo como TAB-separated (sem cabeçalho)
data = pd.read_csv(Filename, sep="\t", header=None)

# Converte vírgula decimal -> ponto e transforma em float.
# Multiplica deslocamento por 1000 (ex.: mm -> µm). Ajuste se sua unidade original for outra.
for i in range(len(data[0])):
    time.append(float(data[0][i].replace(',', '.')))
    d.append(float(data[1][i].replace(',', '.')) * 1000)

# ======= Processamento do sinal =======
# Remove offset (média) do deslocamento para centralizar em 0 (remove componente DC):
av = np.average(d)
d = d - av

# Número total de amostras:
N = len(d)

# Frequência de amostragem (Hz) = N / duração total
# Usa o primeiro e o último tempo, após conversão de vírgula->ponto:
fs = N / (float(data[0][N-1].replace(',', '.')) - float(data[0][0].replace(',', '.')))
print('Sampling Freq =', fs, 'Hz')

# ======= Análise espectral (FFT de uma face / one-sided) =======
# rfft: FFT para sinais reais; normalização 2/N (aprox. amplitude de pico para componentes positivas)
yf = rfft(d) / N * 2
# Eixo de frequências correspondente:
xf = rfftfreq(N, 1/fs)

# Índice da frequência com maior amplitude (pico do espectro):
P = np.argmax(np.abs(yf))
print('Natural Freq =', xf[P], 'Hz')

# ======= Filtragem opcional (passa-baixas Butterworth) =======
if filtering == True:
    # Projeta filtro digital (passa-baixas) com frequência de corte 'cutofffreq' (em Hz) e ordem 'order'
    b, a = signal.butter(order, cutofffreq, analog=False, btype='lowpass', fs=fs)
    # Aplica filtfilt para não distorcer fase (aplica o filtro para frente e para trás):
    filtd = signal.filtfilt(b, a, d)
    # FFT do sinal filtrado (mesma normalização):
    filtyf = rfft(filtd) / N * 2
    filtxf = rfftfreq(N, 1/fs)

# ======= Visualização: tempo (topo) e frequência (embaixo) =======
fig, (ax1, ax2) = plt.subplots(2)

# Sinal no tempo (original):
ax1.plot(time, d)
ax1.set(xlabel='Time (s)', ylabel='d (µm)')
ax1.grid()

# Espectro de amplitude: recorte até MaxF Hz para facilitar a leitura
ax2.plot(xf[:int(MaxF*N/fs)], np.abs(yf[:int(MaxF*N/fs)]))
# Marca a frequência natural estimada:
ax2.plot(xf[P], np.abs(yf[P]), "x", color='r', label=f'Natural Frequency={xf[P]:.5f} Hz')

# Se filtrou, plota também o sinal e o espectro filtrados:
if filtering == True:
    ax1.plot(time, filtd, label='Filtered Signal')
    ax2.plot(filtxf[:int(MaxF*N/fs)], np.abs(filtyf[:int(MaxF*N/fs)]), label='Filtered Signal')

ax2.set(xlabel='freq', ylabel='Ampl')
plt.legend()
ax2.grid()
plt.show()


