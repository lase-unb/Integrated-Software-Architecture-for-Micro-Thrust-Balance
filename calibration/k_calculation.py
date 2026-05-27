# -*- coding: utf-8 -*-
"""
Módulo de Calibração Estática
Objetivo: Determinar a constante de rigidez torcional (k) do sistema.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- 1. PARÂMETROS FÍSICOS ---
g = 9.81
l = 0.005  # Braço de aplicação da massa (m)
L = 0.3    # Braço de leitura do LVDT (m)

# --- 2. LEITURA DOS DADOS ---
# Usando pandas para consistência com o resto do projeto
df = pd.read_csv('data.csv') 

# Convertendo colunas para arrays numpy
M = df['M'].values        # Massas (kg)
d = df['d'].values        # Deslocamento (m)
err_d = df['e'].values    # Erro de medição (m)

# --- 3. CÁLCULOS METROLÓGICOS ---
Mteq = M * g * l          # Torque aplicado (Nm)
Theta = d / L             # Deslocamento angular (rad)
err_theta = err_d / L     # Propagação de erro para o ângulo

# Ajuste Linear (y = kx + a)
# k é a constante elástica (Nm/rad)
k, a = np.polyfit(Theta, Mteq, deg=1)

# Cálculo do coeficiente de determinação (R²) para validar a calibração
y_pred = a + k * Theta
residuals = Mteq - y_pred
r_squared = 1 - (np.sum(residuals**2) / np.sum((Mteq - np.mean(Mteq))**2))

# --- 4. VISUALIZAÇÃO ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Gráfico 1: Dados Brutos (Massa vs Deslocamento)
ax1.scatter(d * 1000, M * 1000, color='blue', marker='x', label='Dados Experimentais')
ax1.set_xlabel('d (mm)')
ax1.set_ylabel('M (g)')
ax1.set_title('Resposta Primária do Sensor')
ax1.grid(True, alpha=0.3)

# Gráfico 2: Curva de Calibração (Torque vs Ângulo)
ax2.errorbar(Theta, Mteq, xerr=err_theta, fmt="o", color="red", label='Dados com Erro')
x_fit = np.linspace(min(Theta), max(Theta), 100)
ax2.plot(x_fit, a + k * x_fit, '--k', label=f'Ajuste: k={k:.5f} Nm/rad')
ax2.set_xlabel('Theta (rad)')
ax2.set_ylabel('Torque (Nm)')
ax2.set_title(f'Calibração Torcional (R² = {r_squared:.4f})')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print(f'--- RELATÓRIO DE CALIBRAÇÃO ---')
print(f'Constante Elástica (k): {k:.6f} Nm/rad')
print(f'Offset (a): {a:.6f} Nm/rad')
print(f'Qualidade do Ajuste (R²): {r_squared:.4f}')