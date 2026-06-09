# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 21:07:18 2025

@author: hecgi
"""

#Este código tem um objetivo principal: monitorar em tempo real um sinal de deslocamento (medido em micrômetros) 
# e exibi-lo dinamicamente em um gráfico, como um "osciloscópio digital".

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from time import sleep
import numpy as np
import os.path


filename='data.txt' # arquivo utilizado. fica em loop enquanto o arquivo existe e tem dados
windowsize=20 #window width in s
Ns=200

while True:                             #wait for file to exist and have data
    if os.path.isfile(filename)==False:
        sleep(0.1)
    elif os.path.getsize(filename)==0 :
        sleep(0.1)
    else : break


D = []
A = []

while True:                             #find sampling freq with first 500 samples
    data = pd.read_csv(filename,sep="\t", header=None)
    Nb=len(data)-1
    if Nb>=Ns :
        sf=Nb/(float(data[0][Nb-1].replace(',', '.'))-float(data[0][0].replace(',', '.')))
        print('Sampling freq',sf)
        N=int(windowsize*sf)            #number of samples to display to acheive set window size
        for j in range(len(data)-1):                   #get data from file an convert to float
            A.append(float(data[1][j].replace(',', '.'))*1000)
        av1=np.average(A)
        break
    else : sleep(0.1)

# grafico dinamico do deslocamento (µm) pelo tempo (s). flutuações em torno de 0

def animate(i):
    time = []
    d = []
    data = pd.read_csv(filename,sep="\t", header=None)
    startindex= max(0, len(data)-N-1)                       #Crop data to N samples
    endindex= len(data)-1
    for i in range(startindex, endindex):                   #get data from file an convert to float
        time.append(float(data[0][i].replace(',', '.')))
        d.append(float(data[1][i].replace(',', '.'))*1000)
 
   
    D.append(d)
    if len(D)>1000:
        av=np.average(D[-200:])
        d=d-av                                                  #average out the signal
    else: d=d-av1
   
    
    plt.cla()
    plt.plot(time, d)
    plt.xlabel("Time (s)")
    plt.ylabel("d (µm)")


ani = FuncAnimation(plt.gcf(), animate, interval=10, cache_frame_data=False)

plt.show()