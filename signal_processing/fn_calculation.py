# -*- coding: utf-8 -*-
"""
Análise de Frequência Natural (FFT + DSP)
Focado em: Identificação da dinâmica estrutural da balança.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq
import pandas as pd
from processing import apply_lowpass_filter 

# --- 1. CONFIGURAÇÕES ---
Filename = '5.caldata_m4_l5_F9,725.txt'
cutoff_freq = 0.5  # 0.5Hz para não cortar a Fn por engano
order = 5
MaxF = 2 # 2Hz para dar "zoom" no que importa 

# --- 2. CARREGAMENTO DOS DADOS ---
data = pd.read_csv(Filename, sep="\t", header=None, decimal=',')
time = data[0].values
d_raw = data[1].values * 1000

# Remoção de offset (Centraliza o sinal no zero para a FFT ser precisa)
d_centered = d_raw - np.mean(d_raw)

# Cálculo da Frequência de Amostragem (fs)
N = len(d_centered)
fs = N / (time[-1] - time[0])
print(f'Sampling Freq = {fs:.2f} Hz')

# --- 3. PROCESSAMENTO DIGITAL DE SINAIS (DSP) ---
# Filtra o sinal para limpar o espectro de frequências parasitas
d_filtered = apply_lowpass_filter(d_centered, fs=fs, cutoff_freq=cutoff_freq)

# FFT do sinal original e do sinal filtrado
yf_raw = rfft(d_centered) / N * 2
yf_filt = rfft(d_filtered) / N * 2
xf = rfftfreq(N, 1/fs)

# Identifica a Frequência Natural (Pico de maior amplitude no sinal filtrado)
P = np.argmax(np.abs(yf_filt))
fn = xf[P]
print(f'Natural Freq Detectada = {fn:.5f} Hz')

# --- 4. VISUALIZAÇÃO ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Gráfico 1: Domínio do Tempo
ax1.plot(time, d_centered, color='lightgray', alpha=0.7, label='Raw Signal')
ax1.plot(time, d_filtered, color='blue', label='Filtered (DSP)')
ax1.set_ylabel('Displacement (µm)')
ax1.set_title('Signal Decays / Vibrations')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Gráfico 2: Domínio da Frequência (FFT)
# Limitando o gráfico para ver apenas até MaxF Hz
mask = xf <= MaxF
ax2.plot(xf[mask], np.abs(yf_raw[mask]), color='lightgray', label='Raw Spectrum')
ax2.plot(xf[mask], np.abs(yf_filt[mask]), color='red', linewidth=1.5, label='Filtered Spectrum')

# Marcação da Frequência Natural
ax2.plot(fn, np.abs(yf_filt[P]), "x", color='black', markersize=10, 
         label=f'Natural Frequency: {fn:.4f} Hz')

ax2.set_xlabel('Frequency (Hz)')
ax2.set_ylabel('Magnitude')
ax2.set_title('Fast Fourier Transform (FFT) Analysis')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()