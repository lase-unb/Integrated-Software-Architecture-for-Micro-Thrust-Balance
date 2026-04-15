# -*- coding: utf-8 -*-  # Codificação do arquivo (permite caracteres como µ, ç etc.)
"""
Editor Spyder

Este é um arquivo de script temporário.
"""
import csv
import matplotlib.pyplot as plt
import numpy as np

# Objetivo: calibrar uma balança de torção (ou similar) para obter a constante elástica angular k
# a partir da relação entre massa aplicada e deslocamento (convertido para ângulo).

g = 9.81      # [m/s²] aceleração da gravidade
l = 0.005     # [m] distância horizontal da massa pendurada ao pivô (braço do torque)
L = 0.3       # [m] "comprimento efetivo" para converter deslocamento linear -> ângulo (Theta = d/L)

M = []        # massas aplicadas [kg]
d = []        # deslocamentos lineares medidos [m]
Mteq = []     # torque equivalente: M*g*l [N·m]
Theta = []    # ângulo estimado: d/L [rad]
err = []      # incerteza do deslocamento linear (mesma unidade de d)

filename = open('data.csv', 'r')           # abre arquivo .csv para leitura
file = csv.DictReader(filename)            # lê como dicionário, esperando colunas: 'M','d','e'

for row in file:                            # percorre linhas do CSV
    M.append(row['M'])                      # guarda strings (converte depois)
    d.append(row['d'])
    err.append(row['e'])
filename.close()                            # fecha o arquivo

for i in range(len(M)):                     # converte cada item para float
    M[i] = float(M[i])                      # massa [kg]
    d[i] = float(d[i])                      # deslocamento linear [m]
    err[i] = float(err[i])                  # erro de d [m]
    Mteq.append(M[i] * g * l)               # torque τ = (M*g) * l  [N·m]
    Theta.append(d[i] / L)                  # ângulo θ = d / L       [rad]

# Ajuste linear: Mteq ≈ k*Theta + a  (k = rigidez [N·m/rad], a = offset de torque [N·m])
k, a = np.polyfit(Theta, Mteq, deg=1)

# cria eixo x para a reta ajustada (entre primeiro e último θ da sua lista)
x = np.linspace(Theta[0], Theta[-1], num=10)

# ----- Gráfico 1: massa vs deslocamento linear (dados brutos) -----
fig, [ax1, ax2] = plt.subplots(1, 2)       # dois subplots lado a lado

ax1.plot(d, M, 'x')                         # marcações dos pontos medidos
ax1.set(xlabel='d [m]', ylabel='M [kg]')

# ----- Gráfico 2: torque vs ângulo com barras de erro e ajuste linear -----
ax2.errorbar(Theta, Mteq, xerr=err, fmt="o", color="r")   # barras de erro (xerr usa 'err' como se fosse erro de θ)
ax2.plot(x, a + k * x, '--k', label=f'k={k:.5f} Nm/rad')  # linha ajustada
ax2.set(xlabel='Theta [rad]', ylabel='Mteq [Nm]')
ax2.legend()
plt.show()

print('k=', k, 'Nm/rad')           # constante elástica angular
print('k zero error =', a, 'Nm/rad')  # OBS: 'a' é torque em θ=0 → unidade correta é N·m (ver versão melhorada)
