# -*- coding: utf-8 -*-  # Codificação do arquivo (permite caracteres como µ, ç etc.)

# Este código monitora em tempo real um arquivo "data.txt" com duas colunas (tempo e deslocamento),
# e plota continuamente o deslocamento (em µm) versus o tempo, como um "osciloscópio digital".

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from time import sleep
import numpy as np
import os.path

# ======= Parâmetros =======
filename='data.txt'   # arquivo observado em loop; deve ter 2 colunas separadas por TAB
windowsize=20         # largura da janela do gráfico (em segundos) a ser exibida
Ns=200                # nº mínimo de amostras para estimar a frequência de amostragem (fs)

# ======= Espera ativa até o arquivo existir e ter conteúdo =======
while True:  # aguarda o arquivo existir e não estar vazio
    if os.path.isfile(filename) == False:
        sleep(0.1)                    # não existe: espera 100 ms
    elif os.path.getsize(filename) == 0:
        sleep(0.1)                    # existe mas vazio: espera 100 ms
    else:
        break                         # existe e tem dados: segue

# buffers (armazenamento temporário de dados) auxiliares 
# (D guardará históricos; A será usado para média inicial)
D = []
A = []

# ======= Estima fs (frequência de amostragem) com os primeiros dados =======
while True:  # tenta até ter amostras suficientes
    data = pd.read_csv(filename, sep="\t", header=None)  # lê todo o arquivo (TAB-separated, sem cabeçalho)
    Nb = len(data) - 1                                   # último índice de linha válido
    if Nb >= Ns:                                         # se há amostras suficientes
        # fs = nº de amostras / duração (t_final - t_inicial)
        sf = Nb / (float(data[0][Nb-1].replace(',', '.')) - float(data[0][0].replace(',', '.')))
        print('Sampling freq', sf)
        # N = nº de amostras a exibir para alcançar a janela temporal desejada (windowsize)
        N = int(windowsize * sf)
        # Converte deslocamento do arquivo para µm e acumula em A para média inicial
        for j in range(len(data) - 1):  # percorre linhas 0..len(data)-2 (percorrer todas as linhas menos a última)
            A.append(float(data[1][j].replace(',', '.')) * 1000)
        av1 = np.average(A)             # média inicial (baseline) do deslocamento
        break
    else:
        sleep(0.1)                      # ainda não há Ns amostras: espera e tenta de novo

# ======= Função de animação: atualiza o gráfico continuamente =======
# Gráfico: deslocamento (µm) x tempo (s), oscilando em torno de 0 após remoção do offset
def animate(i):
    time = []
    d = []
    data = pd.read_csv(filename, sep="\t", header=None)  # relê o arquivo inteiro a cada frame
    startindex = max(0, len(data) - N - 1)              # recorta apenas as últimas N amostras
    endindex   = len(data) - 1
    # Converte fatia de dados para float (vírgula -> ponto) e aplica fator 1000 (ex.: mm -> µm)
    for i in range(startindex, endindex):
        time.append(float(data[0][i].replace(',', '.')))
        d.append(float(data[1][i].replace(',', '.')) * 1000)

    # Guarda histórico do sinal (cada frame adiciona uma "cópia" de d)
    D.append(d)
    if len(D) > 1000:
        # Após acumular muitos frames, usa média das últimas ~200 "janelas" como baseline
        av = np.average(D[-200:])
        d = d - av                      # remove baseline para oscilar em torno de 0
    else:
        d = d - av1                     # antes disso, usa baseline inicial

        # nível de referência do seu sinal — o “zero” correto. Sensores costumam ter um offset 
        # (ex.: parado, medem +2,3 µm). Se você subtrai a baseline, o sinal passa a oscilar em torno 
        # de 0 µm, ficando mais fácil de enxergar a vibração e evitando um pico forte em 0 Hz na FFT.

    # Limpa e redesenha
    plt.cla()
    plt.plot(time, d)
    plt.xlabel("Time (s)")
    plt.ylabel("d (µm)")

# Configura animação com atualização a cada 10 ms (aprox. 100 fps)
ani = FuncAnimation(plt.gcf(), animate, interval=10, cache_frame_data=False)

# Exibe a janela do gráfico
plt.show()
