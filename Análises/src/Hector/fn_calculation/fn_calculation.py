# -*- coding: utf-8 -*-

# Este código tem um objetivo principal analisar vibrações de um sistema mecânico (como uma balança 
# de microempuxo) para descobrir sua frequência natural  de oscilação e limpar o sinal de interferências.

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq
import pandas as pd
from scipy import signal


Filename='5.caldata_m4_l5_F9,725.txt' # arquivo a ser analisado
filtering=True  # Flag para ativar/desativar filtragem
cutofffreq=0.02 # Frequência de corte do filtro (0.02 Hz)
order=5 # Ordem do filtro Butterworth (5ª ordem)

MaxF=5 #Max freq to display in fft plot

# Leitura e Pré-processamento dos dados (conversão de formato, remoção de offset)
# Cria listas vazias para tempo (time) e deslocamento (d)

time = [] 
d = []


data = pd.read_csv(Filename,sep="\t", header=None)

for i in range(len(data[0])):
    time.append(float(data[0][i].replace(',', '.')))
    d.append(float(data[1][i].replace(',', '.'))*1000)

# Processamento do Sinal

av=np.average(d)
d=d-av

N=len(d) # Calcula o número total de amostras
# Calcula a frequência de amostragem (Hz) como o número de amostras dividido pela duração total do sinal
fs=N/(float(data[0][N-1].replace(',', '.'))-float(data[0][0].replace(',', '.'))) 
print('Sampling Freq =', fs, 'Hz')

# Realiza análise espectral para encontrar frequência natural

yf = rfft(d)/N*2 # Calcula a Transformada Rápida de Fourier para sinais reais
xf = rfftfreq(N, 1/fs) # Gera o eixo de frequências correspondente

P=np.argmax(np.abs(yf)) # Identifica a frequência com maior amplitude (frequência natural)

print('Natural Freq =',xf[P], 'Hz')

# Opcionalmente aplica filtro passa-baixas

if filtering==True:
    # Projeta um filtro Butterworth passa-baixas com os parâmetros especificados
    b, a = signal.butter(order, cutofffreq, analog=False, btype='lowpass', fs=fs)
    filtd = signal.filtfilt(b, a, d) # Aplica o filtro sem distorção de fase
    filtyf = rfft(filtd)/N*2
    filtxf = rfftfreq(N, 1/fs)

# Visualiza os resultados no domínio do tempo e da frequência
# Gráfico superior: Sinal no domínio do tempo (original + filtrado se aplicável)
# Gráfico inferior: Espectro de frequência (com destaque para a frequência natural)

fig, (ax1, ax2) = plt.subplots(2)
ax1.plot(time, d)
ax1.set(xlabel='Time (s)', ylabel='d (µm)')
ax1.grid()

ax2.plot(xf[:int(MaxF*N/fs)], np.abs(yf[:int(MaxF*N/fs)]))    #fft plot croped to MaxF Hz
ax2.plot(xf[P], np.abs(yf[P]), "x", color = 'r',  label=f'Natural Frequency={xf[P]:.5f} Hz')
if filtering==True:
    ax1.plot(time, filtd, label='Filtered Signal')
    ax2.plot(filtxf[:int(MaxF*N/fs)], np.abs(filtyf[:int(MaxF*N/fs)]), label='Filtered Signal')   
ax2.set(xlabel='freq', ylabel='Ampl')
plt.legend()
ax2.grid()
plt.show()



