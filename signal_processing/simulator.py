import numpy as np
import time
import os

# Configurações da Simulação
filename = 'data.txt'
fs = 50.0  # Frequência de amostragem (Hz)
duration = 60  # Duração total em segundos
fn = 0.25  # Frequência natural da balança (Hz)
noise_amplitude = 0.05 # Ruído de fundo

if os.path.exists(filename):
    os.remove(filename)

print(f"Simulando dados em {filename}... Abra o seu Live_Plotter agora!")

start_time = time.time()
for i in range(int(duration * fs)):
    curr_t = i / fs
    
    # 1. Ruído aleatório 
    noise = np.random.normal(0, noise_amplitude)
    
    # 2. Oscilação natural 
    oscillation = 0.02 * np.sin(2 * np.pi * fn * curr_t)
    
    # 3. O Evento de Empuxo (ocorre aos 20 segundos)
    thrust = 0
    if 20 < curr_t < 40:
        thrust = 0.5  # O motor liga e desloca 0.5 unidades
    
    # Sinal final (Sujo)
    signal = noise + oscillation + thrust
    
    # Salva no formato que o código lê 
    with open(filename, 'a') as f:
        f.write(f"{curr_t:.4f}\t{signal:.6f}\n".replace('.', ','))
    
    # Mantém o tempo real da amostragem
    time.sleep(1/fs)