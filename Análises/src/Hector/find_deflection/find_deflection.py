# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 15:23:44 2025

@author: Adm
"""
# O código transforma dados brutos de um sensor em uma resposta clara: 
# "A força aplicada causou um deslocamento de X micrômetros, com uma margem de erro de Y micrômetros". 


import matplotlib.pyplot as plt # plotagem de gráficos
import pandas as pd # leitura e manipulação de dados
import numpy as np # operações numéricas
import math
from scipy import signal # processamento de sinais (filtros)

# Parâmetros iniciais

Filename='5.caldata_m4_l5_F9,725.txt' # arquivo a ser analisado

time = [] 
d = []
#av=[]
std=[]
#av0=[]
#w=8000

find_diff=True
time1=[150,280]
time2=[400,600]


cutoff_freq=0.05
order=5



data = pd.read_csv(Filename,sep="\t", header=None)

for i in range(len(data[0])):
    time.append(float(data[0][i].replace(',', '.')))
    d.append(float(data[1][i].replace(',', '.'))*1000)

#fullav=np.average(d)

'''
for i in range(len(d)-w):
    ptval=[]
    for j in range(-int(w/2),int(w/2)):
        ptval.append(d[i+int(w/2)+j])
    av.append(np.average(ptval))
    std.append(np.std(ptval))
    #av0.append(np.average(d[i-int(w/2):i+int(w/2)]))
'''

N=len(d)
fs=N/(float(data[0][N-1].replace(',', '.'))-float(data[0][0].replace(',', '.')))
b, a = signal.butter(order, cutoff_freq, analog=False, btype='lowpass', fs=fs)
av = signal.filtfilt(b, a, d)

def find_nearest_index(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx

if find_diff==True:
    startime1, startindex1=find_nearest_index(time, time1[0])
    endtime1, endindex1=find_nearest_index(time, time1[1])
    d1=d[startindex1:endindex1]
    av1=np.average(d1)
    endindex1=endindex1#-int(w/2)
    std1=np.std(av[startindex1:endindex1])
    
    startime2, startindex2=find_nearest_index(time, time2[0])
    endtime2, endindex2=find_nearest_index(time, time2[1])
    d2=d[startindex2:endindex2]
    av2=np.average(d2)
    endindex2=endindex2#-int(w/2)
    std2=np.std(av[startindex2:endindex2])
        
    diff=abs(av1-av2)
    
    print(f'Displacement={diff:.5f}µm')
    
    disp_std=math.sqrt((std1**2)+(std2**2))

'''
Dplus=[]
for i in range(len(d)-w):
    Dplus.append(av[i]+std[i])
    
Dminus=[]
for i in range(len(d)-w):
    Dminus.append(av[i]-std[i])
    
'''
    
fig, ax = plt.subplots()
ax.plot(time, d, linewidth=0.5)
#ax.plot(time[int(w/2):-int(w/2)], av, label=f'Average over {w} points')
#ax.plot(time, av, label=f'Average over {w} points')
ax.plot(time, av, label=f'Average Butterwothfliter : order={order} , cutoff frequency={cutoff_freq}Hz')
#ax.plot(time[int(w/2):-int(w/2)], Dplus, 'y--', label='Standard Deviation for each point in average curve')
#ax.plot(time[int(w/2):-int(w/2)], Dminus, 'y--')

#ax.plot([time[0],time[0]], [fullav-(std_dev/2), fullav+(std_dev/2)], linewidth=5.0, label=f'Standard Deviation of {w} point average = {std_dev}')


if find_diff==True:
    ax.plot([startime1,endtime1], [av1, av1], 'k--', label=f'Average between {time1[0]} and {time1[1]}s = {av1:.5f}µm')
    ax.plot([startime1,endtime1], [av1+std1, av1+std1], 'r--', label=f'Standard Deviation of average between {time1[0]} and {time1[1]}s = {std1}µm')
    ax.plot([startime1,endtime1], [av1-std1, av1-std1], 'r--')
    
    
    ax.plot([startime2,endtime2], [av2, av2], 'k--', label=f'Average between {time2[0]} and {time2[1]}s = {av2:.5f}µm')
    ax.plot([startime2,endtime2], [av2+std2, av2+std2], 'r--', label=f'Standard Deviation of average between {time2[0]} and {time2[1]}s = {std2}µm')
    ax.plot([startime2,endtime2], [av2-std2, av2-std2], 'r--')
    
    
    ax.plot([time[-1],time[-1]], [av1, av2], linewidth=5.0, label=f'Displacement = {diff}µm ; Standard deviation={disp_std}µm')
    
ax.set(xlabel='Time (s)', ylabel='d (µm)')
ax.set_title('Displacement for Masse=736,7mg ; l=5,52mm ; L=367,5mm ; Feq=108,55µN')
ax.grid()
plt.legend()
plt.show()



