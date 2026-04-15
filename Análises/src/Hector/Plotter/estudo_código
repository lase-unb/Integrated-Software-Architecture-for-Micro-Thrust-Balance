# -*- coding: utf-8 -*-  # Define a codificação do arquivo (permite caracteres como µ)


# Docstring informativa; não afeta a execução

# Imports das bibliotecas usadas para plot, cálculo numérico e tabelas:
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Cria listas vazias para armazenar os dados lidos do arquivo:
time = []  # lista para o eixo do tempo (s)
d = []     # lista para o deslocamento (aqui será convertido para µm)

# Lê o arquivo 'data.txt' separado por TAB (sem cabeçalho).
#    O pandas cria colunas numeradas (0, 1, ...). Assumimos:
#    coluna 0 = tempo; coluna 1 = deslocamento.
data = pd.read_csv('data.txt', sep="\t", header=None)

# Converte cada linha para float, trocando vírgula por ponto.
#    - tempo: string "1,234" -> "1.234" -> float
#    - deslocamento: idem, e multiplica por 1000 para converter unidade
#      (ex.: mm -> µm). Ajuste o fator se sua unidade original for outra.
for i in range(len(data[0])):
    time.append(float(data[0][i].replace(',', '.')))
    d.append(float(data[1][i].replace(',', '.')) * 1000)

# Acha o índice do maior valor em módulo do deslocamento (pico absoluto).
#    np.abs(d) calcula |d| e np.argmax retorna o índice do máximo.
peak = np.argmax(np.abs(d))

# Cria a figura e o eixo do gráfico 
fig, ax = plt.subplots()

# Plota a série temporal (tempo no eixo x, deslocamento no eixo y):
plt.plot(time, d)

# Marca o pico com um "x" vermelho e cria uma legenda com o valor de pico:
plt.plot(time[peak], d[peak], "x", color='r', label=f'dmax={d[peak]:.6f} µm')

# Rótulos dos eixos:
plt.xlabel("Time (s)")
plt.ylabel("d (µm)")

# Exibe a legenda (para aparecer o dmax):
plt.legend()

# Mostra a janela do gráfico:
plt.show()
