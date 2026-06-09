# -*- coding: utf-8 -*-
"""
Live Plotter - Monitoramento em Tempo Real (DSP)
Objetivo: Transformar deslocamento (µm) em Empuxo (mN) em tempo real.
"""
import sys
import os

# 1. Ajuste do Backend Gráfico
try:
    import matplotlib
    matplotlib.use('Qt5Agg') 
except:
    try:
        matplotlib.use('TkAgg')
    except:
        pass

# 2. Configuração de Caminhos
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..'))
if src_dir not in sys.path:
    sys.path.append(src_dir)

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from time import sleep
import numpy as np
from processing import apply_lowpass_filter 

# 3. Constantes de Calibração (Ajuste conforme sua bancada física)
K_TORQUE = 0.0125  # Constante elástica k (Nm/rad)
L_LVDT = 0.3       # Distância do LVDT ao pivô (m)
L_THRUST = 0.25    # Distância do Propulsor ao pivô (m)

# Definição do Arquivo de Dados
filename = os.path.abspath(os.path.join(current_dir, '..', 'Análises', 'data', 'carga_constante', 'P1_d1_4.txt'))

windowsize = 20 
Ns = 200        

print(f"Buscando dados em: {filename}")

# --- 1. ESPERA PELO ARQUIVO ---
while True:
    if os.path.isfile(filename) and os.path.getsize(filename) > 0:
        break
    print("Aguardando arquivo de dados...")
    sleep(0.5)

# --- 2. CÁLCULO INICIAL DE FREQUÊNCIA E OFFSET ---
while True:
    try:
        data = pd.read_csv(filename, sep="\t", header=None, decimal=',')
        Nb = len(data) - 1
        if Nb >= Ns:
            total_t = data[0].iloc[Nb-1] - data[0].iloc[0]
            sf = Nb / total_t
            print(f'Sampling frequency detectada: {sf:.2f} Hz')
            
            N = int(windowsize * sf) 
            av1 = np.average(data[1].iloc[:Ns] * 1000) 
            break
    except Exception as e:
        print(f"Erro na leitura inicial: {e}")
    sleep(0.5)

# --- 3. FUNÇÃO DE ANIMAÇÃO ---
def animate(i):
    try:
        data = pd.read_csv(filename, sep="\t", header=None, decimal=',')
        data_window = data.tail(N)
        
        time = data_window[0].values
        d_raw = data_window[1].values * 1000 # µm
        
        # Filtro Butterworth (0.3 Hz para manter dinâmica visível)
        if len(d_raw) > 30:
            d_filtered = apply_lowpass_filter(d_raw, fs=sf, cutoff_freq=0.5)
        else:
            d_filtered = d_raw - av1

        # --- CÁLCULO DSP: CONVERSÃO PARA EMPUXO (mN) ---
        # 1. Ângulo em radianos (d em metros / L em metros)
        theta = (d_filtered / 1e6) / L_LVDT 
        # 2. Torque (k * theta)
        torque = K_TORQUE * theta
        # 3. Força em milli-Newtons (Torque / L_thrust * 1000)
        thrust_mN = (torque / L_THRUST) * 1000

        plt.cla()
        # Plota o sinal de Empuxo em verde (padrão para força)
        plt.plot(time, thrust_mN, color='green', linewidth=1.5, label='Thrust Signal (mN)')
        
        plt.xlabel("Time (s)")
        plt.ylabel("Thrust (mN)")
        plt.title("Real-Time Thrust Monitoring (mN)")
        plt.grid(True, alpha=0.3)
        plt.legend(loc='upper right')
        
        if len(thrust_mN) > 0:
            plt.ylim(np.min(thrust_mN) - 0.05, np.max(thrust_mN) + 0.05)
            
    except Exception:
        pass

# --- 4. EXECUÇÃO ---
fig = plt.figure()
ani = FuncAnimation(fig, animate, interval=50, cache_frame_data=False)
plt.tight_layout()
plt.show()