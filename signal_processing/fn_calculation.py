# -*- coding: utf-8 -*-
"""
Análise de Frequência Natural (FFT + DSP)
Focado em: Identificação da dinâmica estrutural da balança.
"""

import numpy as np
from scipy.fft import rfft, rfftfreq

from processing import apply_lowpass_filter


def calcular_fnat(d_um, fs, cutoff=0.5, max_freq=5.0):
    """
    FFT com remoção de offset — retorna (fnat, freqs, magnitudes_raw, magnitudes_filt).

    d_um: deslocamento bruto (µm). fs: frequência de amostragem (Hz).
    cutoff: corte do filtro passa-baixa usado para limpar o espectro.
    max_freq: limite superior de frequência considerado na busca do pico.
    """
    d_centered = d_um - np.mean(d_um)
    d_filt = apply_lowpass_filter(d_centered, fs=fs, cutoff_freq=cutoff)

    N = len(d_centered)
    yf_raw = rfft(d_centered) / N * 2
    yf_filt = rfft(d_filt) / N * 2
    xf = rfftfreq(N, 1.0 / fs)

    mask = (xf > 0.01) & (xf <= max_freq)
    xf_m = xf[mask]
    yr_m = np.abs(yf_raw[mask])
    yf_m = np.abs(yf_filt[mask])

    if len(yf_m) == 0:
        return 0.0, xf_m, yr_m, yf_m

    peak_idx = np.argmax(yf_m)
    fnat = xf_m[peak_idx]
    return float(fnat), xf_m, yr_m, yf_m


if __name__ == "__main__":
    import sys

    import matplotlib.pyplot as plt
    import pandas as pd

    Filename = sys.argv[1] if len(sys.argv) > 1 else '5.caldata_m4_l5_F9,725.txt'
    cutoff_freq = 0.5  # 0.5Hz para não cortar a Fn por engano
    MaxF = 2            # 2Hz para dar "zoom" no que importa

    data = pd.read_csv(Filename, sep="\t", header=None, decimal=',')
    time = data[0].values
    d_raw = data[1].values * 1000

    fs = len(d_raw) / (time[-1] - time[0])
    print(f'Sampling Freq = {fs:.2f} Hz')

    fn, xf, yr, yf = calcular_fnat(d_raw, fs, cutoff=cutoff_freq, max_freq=MaxF)
    print(f'Natural Freq Detectada = {fn:.5f} Hz')

    d_centered = d_raw - np.mean(d_raw)
    d_filtered = apply_lowpass_filter(d_centered, fs=fs, cutoff_freq=cutoff_freq)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    ax1.plot(time, d_centered, color='lightgray', alpha=0.7, label='Raw Signal')
    ax1.plot(time, d_filtered, color='blue', label='Filtered (DSP)')
    ax1.set_ylabel('Displacement (µm)')
    ax1.set_title('Signal Decays / Vibrations')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(xf, yr, color='lightgray', label='Raw Spectrum')
    ax2.plot(xf, yf, color='red', linewidth=1.5, label='Filtered Spectrum')
    ax2.plot(fn, yf[np.argmax(yf)] if len(yf) else 0, "x", color='black', markersize=10,
             label=f'Natural Frequency: {fn:.4f} Hz')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Magnitude')
    ax2.set_title('Fast Fourier Transform (FFT) Analysis')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()
