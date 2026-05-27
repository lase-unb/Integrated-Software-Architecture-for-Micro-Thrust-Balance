# -*- coding: utf-8 -*-
"""
Análise de Deflexão - Metrologia de Micro-Newton
Focado em: Automação e Processamento Digital de Sinais (DSP)
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
from scipy import signal

# --- 1. CONFIGURAÇÕES E PARÂMETROS ---
filename = '5.caldata_m4_l5_F9,725.txt'
time1 = [150, 280]  # Janela de baseline (antes da força)
time2 = [400, 600]  # Janela de patamar (durante a força)

# Parâmetros do Filtro Butterworth
cutoff_freq = 0.05  # Frequência de corte (Hz)
order = 5           # Ordem do filtro

# --- 2. CARREGAMENTO E TRATAMENTO DOS DADOS ---
# Lendo direto com decimal em vírgula para ganhar performance
data = pd.read_csv(filename, sep="\t", header=None, decimal=',')

time = data[0].values
d = data[1].values * 1000  # Convertendo para µm

# Cálculo da Frequência de Amostragem (fs)
N = len(d)
total_time = time[-1] - time[0]
fs = N / total_time

# --- 3. PROCESSAMENTO DIGITAL DE SINAIS (DSP) ---
# Criando e aplicando o filtro de fase zero (filtfilt)
b, a = signal.butter(order, cutoff_freq, btype='lowpass', fs=fs)
d_filtered = signal.filtfilt(b, a, d)

def get_stats(t_start, t_end):
    """Retorna o índice, média e desvio padrão para uma janela de tempo."""
    idx_range = (time >= t_start) & (time <= t_end)
    # Usamos o sinal FILTRADO para a média e desvio para evitar ruído espúrio
    window_data = d_filtered[idx_range]
    return window_data.mean(), window_data.std(), time[idx_range]

# --- 4. CÁLCULO DA DEFLEXÃO E INCERTEZA ---
av1, std1, t_win1 = get_stats(time1[0], time1[1])
av2, std2, t_win2 = get_stats(time2[0], time2[1])

diff = abs(av1 - av2)
# Propagação de erro (Incerteza combinada)
disp_std = math.sqrt((std1**2) + (std2**2))

print(f'--- RESULTADOS METROLÓGICOS ---')
print(f'Displacement (Delta d): {diff:.5f} µm')
print(f'Uncertainty (Std Dev): {disp_std:.5f} µm')

# --- 5. VISUALIZAÇÃO DOS RESULTADOS ---
fig, ax = plt.subplots(figsize=(10, 6))

# Sinal Bruto vs Sinal Filtrado
ax.plot(time, d, color='lightgray', linewidth=0.5, label='Sinal Bruto (LVDT)')
ax.plot(time, d_filtered, color='blue', linewidth=1.5, 
        label=f'Filtro Butterworth (Order={order}, Cutoff={cutoff_freq}Hz)')

# Marcações das médias (Linhas de patamar)
ax.hlines(av1, time1[0], time1[1], colors='black', linestyles='--', 
          label=f'Média 1: {av1:.2f}µm')
ax.hlines(av2, time2[0], time2[1], colors='black', linestyles='--', 
          label=f'Média 2: {av2:.2f}µm')

# Sombreado do Desvio Padrão (Fica muito profissional no artigo!)
ax.fill_between(t_win1, av1-std1, av1+std1, color='red', alpha=0.2, label='Incerteza (±σ)')
ax.fill_between(t_win2, av2-std2, av2+std2, color='red', alpha=0.2)

ax.set_xlabel('Time (s)')
ax.set_ylabel('Displacement (µm)')
ax.set_title(f'Análise de Deflexão - Arquivo: {filename}')
ax.grid(True, which='both', linestyle='--', alpha=0.5)
ax.legend(loc='best', fontsize='small')

plt.tight_layout()
plt.show()