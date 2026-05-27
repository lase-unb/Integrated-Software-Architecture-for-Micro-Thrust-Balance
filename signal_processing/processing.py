import numpy as np
from scipy import signal


def apply_kalman_filter(data, fn=0.25, fs=50.0, q=1e-4, r=1e-2):
    """
    Camada 2b — Filtro de Kalman sintonizado no Gêmeo Digital da balança.

    O modelo dinâmico é derivado do simulator.py: o pêndulo oscila em torno
    da frequência natural fn (Hz) com ruído estocástico gaussiano. O Kalman
    estima o estado real do sistema (posição do pêndulo) rejeitando os resíduos
    estocásticos que o Butterworth não eliminou.
    """
    if len(data) < 10:
        return data

    dt = 1.0 / fs
    omega_n = 2 * np.pi * fn

    A = np.array([
        [1.0,  dt],
        [-omega_n**2 * dt,  1.0]
    ])
    H = np.array([[1.0, 0.0]])
    Q = q * np.eye(2)
    R = np.array([[r]])

    n = len(data)
    x_est = np.zeros(n)
    x = np.array([data[0], 0.0])
    P = np.eye(2)

    for k in range(n):
        x_pred = A @ x
        P_pred = A @ P @ A.T + Q
        z = np.array([[data[k]]])
        S = H @ P_pred @ H.T + R
        K = P_pred @ H.T @ np.linalg.inv(S)
        x = x_pred + (K @ (z - H @ x_pred)).flatten()
        P = (np.eye(2) - K @ H) @ P_pred
        x_est[k] = float(x[0])

    return x_est


def apply_lowpass_filter(data, fs=100, cutoff_freq=0.3, order=5,
                         fn=0.25, use_kalman=True):
    """
    Camada 2 — Pipeline DSP completo: Butterworth (fase zero) → Kalman.

    Por padrão aplica os dois filtros em sequência. Todos os módulos que já
    chamavam apply_lowpass_filter ganham o Kalman automaticamente sem nenhuma
    alteração de código. Para usar só o Butterworth, passe use_kalman=False.
    """
    if len(data) < 30:
        return data

    nyquist = 0.5 * fs
    normal_cutoff = cutoff_freq / nyquist
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    butter_out = signal.filtfilt(b, a, data)

    if use_kalman:
        return apply_kalman_filter(butter_out, fn=fn, fs=fs)

    return butter_out


def apply_full_pipeline(data, fn=0.25, fs=50.0, cutoff_freq=0.3,
                        kalman_q=1e-4, kalman_r=1e-2):
    """
    Atalho explícito para o pipeline completo: Butterworth → Kalman.
    """
    return apply_lowpass_filter(data, fs=fs, cutoff_freq=cutoff_freq,
                                fn=fn, use_kalman=True)


def convert_to_mn(displacement_um, k_torque, l_thrust, l_lvdt):
    """
    Converte deslocamento (µm) para força de empuxo (mN).
    Baseado na mecânica da balança de pêndulo simples com pequenos ângulos.
    """
    displacement_m = displacement_um / 1_000_000.0
    theta = displacement_m / l_lvdt
    torque = k_torque * theta
    thrust_n = torque / l_thrust
    return thrust_n * 1000


def calculate_metrics(time, thrust_mn):
    """
    Extrai métricas estatísticas para o relatório final.
    Calcula bias (erro de zero), empuxo nominal e ruído RMS.
    """
    bias = np.mean(thrust_mn[:50]) if len(thrust_mn) > 50 else 0
    thrust_puro = thrust_mn - bias
    nominal_thrust = np.max(thrust_puro)

    return {
        "bias": bias,
        "nominal_thrust": nominal_thrust,
        "peak_value": np.max(thrust_mn),
        "rms_noise": np.std(thrust_mn[:50]) if len(thrust_mn) > 50 else 0
    }