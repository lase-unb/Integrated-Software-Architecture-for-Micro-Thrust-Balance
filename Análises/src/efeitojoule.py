import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Entrada de Dados Brutos (Matrizes com os dados REAIS)
tempo_min = [0, 1, 2, 3, 4, 5]

# Cada linha é um instante de tempo (0 a 5 min).
# Cada coluna representa um dos 5 ensaios (Tabela 1, Tabela 2, Tabela 3, Tabela 4, Tabela 5).
corrente_bruta = np.array([
    [0.150, 0.147, 0.146, 0.144, 0.146], # Tempo 0
    [0.141, 0.138, 0.137, 0.136, 0.138], # Tempo 1
    [0.138, 0.135, 0.134, 0.133, 0.135], # Tempo 2
    [0.136, 0.133, 0.132, 0.131, 0.133], # Tempo 3
    [0.134, 0.132, 0.131, 0.130, 0.132], # Tempo 4
    [0.133, 0.131, 0.130, 0.129, 0.131]  # Tempo 5
])

potencia_bruta = np.array([
    [3.561, 3.510, 3.477, 3.420, 3.485], # Tempo 0
    [3.384, 3.280, 3.283, 3.254, 3.301], # Tempo 1
    [3.309, 3.237, 3.213, 3.186, 3.234], # Tempo 2
    [3.261, 3.195, 3.173, 3.149, 3.196], # Tempo 3
    [3.224, 3.163, 3.142, 3.125, 3.166], # Tempo 4
    [3.190, 3.135, 3.115, 3.100, 3.139]  # Tempo 5
])

df = pd.DataFrame({'Tempo_min': tempo_min})

# Calculando Média e Desvio Padrão automaticamente ao longo do eixo das colunas (axis=1)
# O parâmetro ddof=1 garante o cálculo do desvio padrão amostral
df['Corrente_A'] = np.mean(corrente_bruta, axis=1)
df['Potencia_W'] = np.mean(potencia_bruta, axis=1)
df['Std_Potencia_W'] = np.std(potencia_bruta, axis=1, ddof=1) 

# Parâmetros do sistema
V_nominal = 24.0  # Volts
alpha_cobre = 0.00393  # 1/°C

# 2. Cálculos Derivados Aplicados aos Dados Brutos
# Para precisão estatística, calcula-se a resistência e o Delta T para CADA ensaio
resistencia_bruta = V_nominal / corrente_bruta

# A resistência inicial (R_i) é a primeira linha da matriz para cada um dos 5 ensaios
resistencia_inicial = resistencia_bruta[0, :] 

# Variação de temperatura para CADA ensaio individualmente
delta_T_bruto = (resistencia_bruta - resistencia_inicial) / (resistencia_inicial * alpha_cobre)

# Agora extraímos a média e o desvio padrão da Variação de Temperatura
df['Resistencia_Ohm'] = np.mean(resistencia_bruta, axis=1)
df['Delta_T_C'] = np.mean(delta_T_bruto, axis=1)
df['Std_Delta_T_C'] = np.std(delta_T_bruto, axis=1, ddof=1)

# Energia Dissipada Real (Integral P dt) - Calculada sobre a média da potência
tempo_segundos = df['Tempo_min'] * 60
energia_acumulada = [0.0]

for i in range(1, len(df)):
    e_int = np.trapz(df['Potencia_W'].iloc[:i+1], tempo_segundos[:i+1])
    energia_acumulada.append(e_int)

df['Energia_Real_J'] = energia_acumulada

# 3. Geração dos Gráficos Acadêmicos
fig, ax1 = plt.subplots(figsize=(10, 6))

# Eixo Y esquerdo: Potência
color = 'tab:blue'
ax1.set_xlabel('Tempo (minutos)', fontsize=12)
ax1.set_ylabel('Potência Dissipada (W)', color=color, fontsize=12)
ax1.errorbar(df['Tempo_min'], df['Potencia_W'], yerr=df['Std_Potencia_W'], marker='o', color=color, label='Potência', capsize=4)
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, linestyle='--', alpha=0.6)

# Eixo Y direito: Variação de Temperatura
ax2 = ax1.twinx()  
color = 'tab:red'
ax2.set_ylabel('Variação de Temperatura Estimada ($\Delta T$ °C)', color=color, fontsize=12)
ax2.errorbar(df['Tempo_min'], df['Delta_T_C'], yerr=df['Std_Delta_T_C'], marker='o', linestyle='--', color=color, label='$\Delta T$ (Cobre)', capsize=4)
ax2.tick_params(axis='y', labelcolor=color)

fig.suptitle('Comportamento Térmico e Dissipação de Potência do Eletroímã', fontsize=14)
fig.tight_layout()
plt.show()

# Exibindo os dados consolidados com os desvios
print(df[['Tempo_min', 'Potencia_W', 'Std_Potencia_W', 'Delta_T_C', 'Std_Delta_T_C']].round(4))