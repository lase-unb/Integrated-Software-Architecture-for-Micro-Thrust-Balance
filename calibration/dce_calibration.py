# -*- coding: utf-8 -*-
"""
Calibração in situ via DCE (Dispositivo de Calibração Eletrostática).
Objetivo: varrer voltagens conhecidas no DCE, medir a deflexão resultante e
ajustar a rigidez torcional (kappa) por regressão, sem massas de calibração.
"""

import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hardware'))
from dce_power_supply import VOLT_MAX


def forca_dce(voltagem_V, k_ecd, de_mm):
    """
    Força eletrostática de placas paralelas: F(V) = k_ecd * (V/de)^2, em N.
    voltagem_V em volts, de_mm em milímetros. k_ecd é o mesmo parâmetro usado
    em interface/main.py (calcular_voltagem_dce), calibrado para retornar a
    força em µN -- por isso o resultado é convertido para N (fator 1e-6).
    """
    forca_uN = k_ecd * (np.asarray(voltagem_V, dtype=float) / de_mm) ** 2
    return forca_uN * 1e-6


def calibrar_via_dce(fonte, ler_deflexao_fn, voltagens_V, k_ecd, de_mm,
                      l_thrust, L_lvdt, canal="CH1", t_espera=0.5,
                      ambiente="ambiente"):
    """
    Executa a varredura de voltagem no DCE e ajusta kappa por regressão linear
    T(theta) = kappa*theta + a, reaproveitando o mesmo modelo de
    calibration/k_calculation.py -- só que a força vem do DCE, não de massas.

    fonte: objeto com set_voltage(canal, V), output(canal, bool), medir(canal)
           -- RigolDP932U (hardware/dce_power_supply.py) ou um substituto
           compatível (ex.: FontePowerSupplySimulada) para testes sem hardware.
    ler_deflexao_fn: callable() -> (deflexao_m, incerteza_m), chamada após o
           tempo de acomodação em cada degrau de voltagem.
    ambiente: rótulo da sessão de calibração ("ambiente" ou "vacuo"), para
           comparar as duas estimativas de kappa e isolar erros de atrito/ar.
    """
    voltagens_V = np.asarray(voltagens_V, dtype=float)
    if np.any(voltagens_V > VOLT_MAX) or np.any(voltagens_V < 0):
        raise ValueError(f"Voltagem fora da faixa segura (0-{VOLT_MAX} V).")

    deflexoes_m = []
    incertezas_m = []
    for v in voltagens_V:
        fonte.set_voltage(canal, float(v))
        fonte.output(canal, True)
        time.sleep(t_espera)
        d, err = ler_deflexao_fn()
        deflexoes_m.append(d)
        incertezas_m.append(err)
    fonte.output(canal, False)

    deflexoes_m = np.array(deflexoes_m)
    incertezas_m = np.array(incertezas_m)

    F = forca_dce(voltagens_V, k_ecd, de_mm)
    T = F * l_thrust
    theta = deflexoes_m / L_lvdt
    err_theta = incertezas_m / L_lvdt

    kappa, a_off = np.polyfit(theta, T, deg=1)
    y_pred = a_off + kappa * theta
    ss_res = np.sum((T - y_pred) ** 2)
    ss_tot = np.sum((T - np.mean(T)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0

    return {
        "kappa": float(kappa), "a_off": float(a_off), "r2": float(r2),
        "ambiente": ambiente, "voltagens_V": voltagens_V,
        "theta": theta, "T": T, "err_theta": err_theta,
    }


if __name__ == "__main__":
    """
    Demonstração de ponta a ponta SEM hardware: usa FontePowerSupplySimulada
    e um leitor de deflexão sintético (baseado num kappa "verdadeiro"
    conhecido) para validar que a rotina de varredura + regressão recupera
    o kappa correto antes de rodar contra o equipamento físico.
    """
    from dce_power_supply import FontePowerSupplySimulada

    KAPPA_REAL = 0.0125      # N*m/rad -- valor "verdadeiro" assumido pra simulação
    K_ECD = 0.45             # constante do DCE (mesma usada em interface/main.py)
    DE_MM = 1.0              # mm
    L_THRUST = 0.25          # m
    L_LVDT = 0.30            # m
    RUIDO_DEFLEXAO_M = 2e-7  # incerteza simulada do LVDT (m)

    fonte_sim = FontePowerSupplySimulada(ruido_v=0.005)

    def ler_deflexao_simulada():
        v = fonte_sim.ultimo_valor("CH1")
        F = forca_dce(v, K_ECD, DE_MM)
        theta = (F * L_THRUST) / KAPPA_REAL
        d = theta * L_LVDT
        d_ruido = d + np.random.normal(0, RUIDO_DEFLEXAO_M)
        return d_ruido, RUIDO_DEFLEXAO_M

    voltagens = np.linspace(5, 30, 8)  # V -- dentro da faixa da DP932U (CH1/CH2 até ~33,6 V)

    resultado = calibrar_via_dce(
        fonte_sim, ler_deflexao_simulada, voltagens,
        k_ecd=K_ECD, de_mm=DE_MM, l_thrust=L_THRUST, L_lvdt=L_LVDT,
        t_espera=0.0, ambiente="ambiente (simulado)",
    )

    erro_pct = abs(resultado["kappa"] - KAPPA_REAL) / KAPPA_REAL * 100
    print("--- Calibração via DCE (simulada) ---")
    print(f"kappa verdadeiro : {KAPPA_REAL:.6f} N*m/rad")
    print(f"kappa ajustado   : {resultado['kappa']:.6f} N*m/rad")
    print(f"erro relativo    : {erro_pct:.3f} %")
    print(f"R^2              : {resultado['r2']:.5f}")
