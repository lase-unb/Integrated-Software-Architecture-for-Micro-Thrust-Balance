# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 14:06:21 2025

@author: Adm
"""

import pandas as pd
import matplotlib.pyplot as plt

filename = 'data.txt'

# Lê o arquivo completo (sem cabeçalho, separado por tabulação)
data = pd.read_csv(filename, sep='\t', header=None)

# Converte tempo e sinal, trocando vírgula por ponto e multiplicando por 1000 para deslocamento
time = [float(str(t).replace(',', '.')) for t in data[0]]
d = [float(str(val).replace(',', '.')) * 1000 for val in data[1]]

plt.figure(figsize=(10,6))
plt.plot(time, d, linewidth=0.8)
plt.xlabel('Tempo (s)')
plt.ylabel('Deslocamento (µm)')
plt.title('Gráfico Completo de Deslocamento')
plt.grid(True)

# Salva a figura
plt.savefig('grafico_completo.png', dpi=300)

plt.show()
