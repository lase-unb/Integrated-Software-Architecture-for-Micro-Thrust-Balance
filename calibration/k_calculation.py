# -*- coding: utf-8 -*-
"""
Módulo de Calibração Estática
Objetivo: Determinar a constante de rigidez torcional (k) do sistema.
"""

import numpy as np


def calibracao_estatica(massas_kg, desl_m, erros_m, g=9.81,
                         l_aplicacao=0.005, L_lvdt=0.3):
    """
    Regressão linear T(θ) = k·θ + a por mínimos quadrados (numpy.polyfit),
    com coeficiente de determinação R² para validar a calibração.

    massas_kg, desl_m, erros_m: massas de calibração (kg), deslocamento
    linear medido (m) e incerteza da medição (m).
    l_aplicacao: braço de aplicação da massa (m).
    L_lvdt: braço de leitura do sensor LVDT (m).
    """
    Mteq = massas_kg * g * l_aplicacao
    Theta = desl_m / L_lvdt
    err_theta = erros_m / L_lvdt

    k, a_off = np.polyfit(Theta, Mteq, deg=1)
    y_pred = a_off + k * Theta
    ss_res = np.sum((Mteq - y_pred) ** 2)
    ss_tot = np.sum((Mteq - np.mean(Mteq)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0

    return float(k), float(a_off), float(r2), Theta, Mteq, err_theta


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import pandas as pd

    l_aplicacao = 0.005  # Braço de aplicação da massa (m)
    L_lvdt = 0.3          # Braço de leitura do LVDT (m)

    df = pd.read_csv('data.csv')
    k, a_off, r_squared, Theta, Mteq, err_theta = calibracao_estatica(
        df['M'].values, df['d'].values, df['e'].values,
        l_aplicacao=l_aplicacao, L_lvdt=L_lvdt,
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.scatter(df['d'].values * 1000, df['M'].values * 1000, color='blue',
                marker='x', label='Dados Experimentais')
    ax1.set_xlabel('d (mm)')
    ax1.set_ylabel('M (g)')
    ax1.set_title('Resposta Primária do Sensor')
    ax1.grid(True, alpha=0.3)

    ax2.errorbar(Theta, Mteq, xerr=err_theta, fmt="o", color="red", label='Dados com Erro')
    x_fit = np.linspace(min(Theta), max(Theta), 100)
    ax2.plot(x_fit, a_off + k * x_fit, '--k', label=f'Ajuste: k={k:.5f} Nm/rad')
    ax2.set_xlabel('Theta (rad)')
    ax2.set_ylabel('Torque (Nm)')
    ax2.set_title(f'Calibração Torcional (R² = {r_squared:.4f})')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    print('--- RELATÓRIO DE CALIBRAÇÃO ---')
    print(f'Constante Elástica (k): {k:.6f} Nm/rad')
    print(f'Offset (a): {a_off:.6f} Nm/rad')
    print(f'Qualidade do Ajuste (R²): {r_squared:.4f}')
