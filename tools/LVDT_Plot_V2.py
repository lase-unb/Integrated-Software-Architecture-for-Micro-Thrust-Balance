# -*- coding: utf-8 -*-
"""
Módulo de Identificação de Pico (d_max)
Objetivo: Localizar o deslocamento máximo real para cálculo de empuxo.
"""

import os
import sys

import numpy as np

_current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_current_dir, '..', 'signal_processing'))
from processing import apply_lowpass_filter  # Importante para não pegar ruído como pico


def detectar_xmax(d_um, fs, cutoff=0.1):
    """
    Identifica xmax (maior deflexão absoluta) no sinal filtrado, evitando
    que ruído seja confundido com o pico real de deslocamento.
    """
    d_filt = apply_lowpass_filter(d_um, fs=fs, cutoff_freq=cutoff)
    peak_idx = np.argmax(np.abs(d_filt))
    return float(d_filt[peak_idx]), peak_idx, d_filt


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import pandas as pd

    filename = os.path.abspath(os.path.join(
        _current_dir, '..', 'Análises', 'data', 'carga_constante', 'P1_d1_4.txt'
    ))
    data = pd.read_csv(filename, sep="\t", header=None, decimal=',')

    time = data[0].values
    d_raw = data[1].values * 1000  # Converte para µm

    fs = len(d_raw) / (time[-1] - time[0])
    d_max, peak_idx, d_filtered = detectar_xmax(d_raw, fs, cutoff=0.1)

    print('--- Resultado da Análise ---')
    print(f'Frequência de Amostragem: {fs:.2f} Hz')
    print(f'Deslocamento Máximo (d_max): {d_max:.6f} µm')

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(time, d_raw, color='lightgray', alpha=0.5, label='Sinal Bruto (LVDT)')
    ax.plot(time, d_filtered, color='blue', linewidth=1.5, label='Sinal Filtrado (Butterworth)')
    ax.plot(time[peak_idx], d_max, "x", color='red', markersize=10,
            label=f'Pico Real: {d_max:.4f} µm')
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("d (µm)")
    ax.set_title(f"Identificação de Deslocamento Máximo - {filename}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()
