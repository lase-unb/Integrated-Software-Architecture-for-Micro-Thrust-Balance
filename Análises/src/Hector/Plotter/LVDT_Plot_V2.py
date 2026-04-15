# -*- coding: utf-8 -*-
"""
Editor Spyder

Este é um arquivo de script temporário.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

time = [] 
d = []


data = pd.read_csv('data.txt',sep="\t", header=None)

for i in range(len(data[0])):
    time.append(float(data[0][i].replace(',', '.')))
    d.append(float(data[1][i].replace(',', '.'))*1000)
    
peak = np.argmax(np.abs(d))

fig, ax = plt.subplots()
plt.plot(time, d)
plt.plot(time[peak], d[peak], "x", color = 'r', label=f'dmax={d[peak]:.6f} µm')
plt.xlabel("Time (s)")
plt.ylabel("d (µm)")
plt.legend()
plt.show()

