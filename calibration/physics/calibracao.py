# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np

# 1. Dados fornecidos (com vírgulas adicionadas para formato de lista Python)
Feq = [167.1960, 219.7635, 324.3694, 481.8955, 486.3337, 634.9099, 808.3664]
deslocamento = [0.0015, 0.0021, 0.0027, 0.0050, 0.0047, 0.0060, 0.0074]
desvio_padrao = [0.000070711, 0.000148492, 0.000424264, 0.000113137, 0.000388909, 0.000226274, 0.000282843]

# 2. Ajuste Linear (Regressão)
k, a = np.polyfit(deslocamento, Feq, deg=1)

# Cria pontos para desenhar a reta teórica no gráfico
x_fit = np.linspace(min(deslocamento) - 0.0005, max(deslocamento) + 0.0005, 100)
y_fit = k * x_fit + a

# 3. Plotagem do Gráfico
plt.figure(figsize=(8, 6))

# Plota os pontos vermelhos com as barras de erro pretas horizontais (xerr)
plt.errorbar(deslocamento, Feq, xerr=desvio_padrao, fmt='o', color='red', 
             ecolor='black', capsize=4, elinewidth=1.5, markeredgecolor='black',
             label='Dados Experimentais ± Desvio Padrão')

# Plota a reta de ajuste (k) tracejada
plt.plot(x_fit, y_fit, '--k', alpha=0.7, label=f'Ajuste Linear (k = {k:.0f})')

# 4. Configurações Visuais
plt.xlabel('Deslocamento (µm)', fontsize=12)
plt.ylabel('Força Equivalente - Feq (µN)', fontsize=12)
plt.title('Curva de Calibração: Força Equivalente vs Deslocamento', fontsize=14)

# Adiciona grid, legenda e ajusta margens
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper left', fontsize=10)
plt.tight_layout()

# Exibe o gráfico na tela
plt.show()

# Imprime o valor da rigidez no terminal
print(f"Rigidez Calculada (k): {k:.2f} µN/µm")
print(f"Offset (a): {a:.2f} µN")