import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# =========================
# FUNÇÃO DO SISTEMA
# =========================
def pendulo_amortecido(t, y, g, l, gamma, modelo):
    theta = y[0]
    omega = y[1]
    
    if modelo == 'linear':
        dtheta = omega
        domega = -gamma * omega - (g / l) * theta
    elif modelo == 'nao_linear':
        dtheta = omega
        domega = -gamma * omega - (g / l) * np.sin(theta)
    else:
        raise ValueError("O modelo deve ser 'linear' ou 'nao_linear'")
        
    return [dtheta, domega]

# =========================
# ENTRADAS DO USUÁRIO
# =========================
g = 9.81           # gravidade (m/s^2)
l = 0.3675         # comprimento (m)
m = 0.5            # massa (kg)
b = 0.2            # coeficiente de amortecimento viscoso

theta0 = np.deg2rad(10)  # ângulo inicial
omega0 = 0.0            # velocidade inicial em rad/s

tspan = [0, 40]

modelo = 'nao_linear'   # escolher 'linear' ou 'nao_linear'

# =========================
# PARÂMETRO DERIVADO
# =========================
gamma = b / (m * l**2)

# =========================
# CONDIÇÃO INICIAL
# =========================
y0 = [theta0, omega0]

# =========================
# SOLUÇÃO NUMÉRICA
# =========================
# O ode45 ajusta os passos de tempo automaticamente. No Python, passamos 
# t_eval para garantir que o gráfico fique suave com pontos suficientes.
t_eval = np.linspace(tspan[0], tspan[1], 1000)

# O solve_ivp exige que a função tenha a assinatura f(t, y). 
# Usamos uma função lambda para repassar os parâmetros extras.
sol = solve_ivp(lambda t, y: pendulo_amortecido(t, y, g, l, gamma, modelo), 
                tspan, y0, t_eval=t_eval)

t = sol.t
theta = sol.y[0, :]
omega = sol.y[1, :]

# =========================
# PLOTS
# =========================
plt.figure(figsize=(8, 6))

plt.subplot(2, 1, 1)
plt.plot(t, theta, linewidth=1.5, color='tab:blue')
plt.ylabel(r'$\theta$ (rad)')
plt.title('Pêndulo com Amortecimento Viscoso')
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(t, omega, linewidth=1.5, color='tab:orange')
plt.ylabel(r'$\omega$ (rad/s)')
plt.xlabel('Tempo (s)')
plt.grid(True)

plt.tight_layout()
plt.show()