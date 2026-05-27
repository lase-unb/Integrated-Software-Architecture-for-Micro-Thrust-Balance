# -*- coding: utf-8 -*-
"""
Módulo de Identificação de Pico (d_max)
Objetivo: Localizar o deslocamento máximo real para cálculo de empuxo.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from processing import apply_lowpass_filter # Importante para não pegar ruído como pico

# --- 1. CARREGAMENTO DOS DADOS ---
filename = os.path.abspath(os.path.join(current_dir, '..', 'Análises', 'data', 'carga_constante', 'P1_d1_4.txt'))
# Lendo com decimal=',' 
data = pd.read_csv(filename, sep="\t", header=None, decimal=',')

time = data[0].values
d_raw = data[1].values * 1000 # Converte para µm

# --- 2. PROCESSAMENTO (DSP) ---
# Calcula a frequência de amostragem para o filtro
N = len(d_raw)
fs = N / (time[-1] - time[0])

# Aplica o filtro antes de procurar o pico. 
# para garantir que o "X" marque o movimento da balança, não um ruído.
d_filtered = apply_lowpass_filter(d_raw, fs=fs, cutoff_freq=0.1)

# Procura o índice do valor máximo no sinal LIMPO
peak_idx = np.argmax(np.abs(d_filtered))
d_max = d_filtered[peak_idx]

print(f'--- Resultado da Análise ---')
print(f'Frequência de Amostragem: {fs:.2f} Hz')
print(f'Deslocamento Máximo (d_max): {d_max:.6f} µm')

# --- 3. VISUALIZAÇÃO ---
fig, ax = plt.subplots(figsize=(10, 5))

# Plota o sinal bruto em cinza ao fundo e o filtrado em azul
ax.plot(time, d_raw, color='lightgray', alpha=0.5, label='Sinal Bruto (LVDT)')
ax.plot(time, d_filtered, color='blue', linewidth=1.5, label='Sinal Filtrado (Butterworth)')

# Marcação do Pico Real
ax.plot(time[peak_idx], d_max, "x", color='red', markersize=10, 
        label=f'Pico Real: {d_max:.4f} µm')

ax.set_xlabel("Time (s)")
ax.set_ylabel("d (µm)")
ax.set_title(f"Identificação de Deslocamento Máximo - {filename}")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()