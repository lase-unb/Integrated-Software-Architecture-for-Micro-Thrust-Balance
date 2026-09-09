# -*- coding: utf-8 -*-
"""
Análise de Deflexão - Metrologia de Micro-Newton
Focado em: Automação e Processamento Digital de Sinais (DSP)
"""

import math

import numpy as np
from scipy import signal


def calcular_deflexao(time_arr, d_um, t1_start, t1_end, t2_start, t2_end,
                       fs, cutoff=0.05, order=5):
    """
    Calcula a deflexão (Δd) entre uma janela de baseline e uma janela de
    patamar, com a incerteza combinada σ_c = sqrt(σ1² + σ2²) (GUM).

    time_arr, d_um: vetores de tempo (s) e deslocamento (µm).
    t1_start/t1_end: janela de baseline (repouso).
    t2_start/t2_end: janela de patamar (empuxo ativo).
    fs: frequência de amostragem (Hz).
    """
    b, a = signal.butter(order, cutoff, btype='lowpass', fs=fs)
    d_filtered = signal.filtfilt(b, a, d_um)

    def janela(t0, t1):
        idx = (time_arr >= t0) & (time_arr <= t1)
        w = d_filtered[idx]
        return w.mean(), w.std(), time_arr[idx]

    av1, std1, tw1 = janela(t1_start, t1_end)
    av2, std2, tw2 = janela(t2_start, t2_end)
    delta = abs(av2 - av1)
    incerteza = math.sqrt(std1 ** 2 + std2 ** 2)

    return {
        "delta_um": delta, "incerteza_um": incerteza,
        "av1": av1, "std1": std1, "tw1": tw1,
        "av2": av2, "std2": std2, "tw2": tw2,
        "d_filt": d_filtered,
    }


if __name__ == "__main__":
    import sys

    import matplotlib.pyplot as plt
    import pandas as pd

    filename = sys.argv[1] if len(sys.argv) > 1 else '5.caldata_m4_l5_F9,725.txt'
    time1 = [150, 280]  # Janela de baseline (antes da força)
    time2 = [400, 600]  # Janela de patamar (durante a força)
    cutoff_freq = 0.05

    data = pd.read_csv(filename, sep="\t", header=None, decimal=',')
    time = data[0].values
    d = data[1].values * 1000  # µm

    fs = len(d) / (time[-1] - time[0])
    res = calcular_deflexao(time, d, time1[0], time1[1], time2[0], time2[1],
                             fs, cutoff=cutoff_freq)

    print('--- RESULTADOS METROLÓGICOS ---')
    print(f'Displacement (Delta d): {res["delta_um"]:.5f} µm')
    print(f'Uncertainty (Std Dev): {res["incerteza_um"]:.5f} µm')

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time, d, color='lightgray', linewidth=0.5, label='Sinal Bruto (LVDT)')
    ax.plot(time, res["d_filt"], color='blue', linewidth=1.5,
            label=f'Filtro Butterworth (Order=5, Cutoff={cutoff_freq}Hz)')
    ax.hlines(res["av1"], time1[0], time1[1], colors='black', linestyles='--',
              label=f'Média 1: {res["av1"]:.2f}µm')
    ax.hlines(res["av2"], time2[0], time2[1], colors='black', linestyles='--',
              label=f'Média 2: {res["av2"]:.2f}µm')
    ax.fill_between(res["tw1"], res["av1"] - res["std1"], res["av1"] + res["std1"],
                     color='red', alpha=0.2, label='Incerteza (±σ)')
    ax.fill_between(res["tw2"], res["av2"] - res["std2"], res["av2"] + res["std2"],
                     color='red', alpha=0.2)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Displacement (µm)')
    ax.set_title(f'Análise de Deflexão - Arquivo: {filename}')
    ax.grid(True, which='both', linestyle='--', alpha=0.5)
    ax.legend(loc='best', fontsize='small')

    plt.tight_layout()
    plt.show()
