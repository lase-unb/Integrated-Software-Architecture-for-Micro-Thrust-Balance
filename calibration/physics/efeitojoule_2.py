import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# 1. Entrada dos Dados Brutos (Potência em Watts extraída das 5 tabelas)
tempos = np.array([0, 1, 2, 3, 4, 5])

P_t1 = [3.561, 3.384, 3.309, 3.261, 3.224, 3.190]
P_t2 = [3.510, 3.280, 3.237, 3.195, 3.163, 3.135]
P_t3 = [3.477, 3.283, 3.213, 3.173, 3.142, 3.115]
P_t4 = [3.420, 3.254, 3.186, 3.149, 3.125, 3.100]
P_t5 = [3.485, 3.301, 3.234, 3.196, 3.166, 3.139]

# Consolidando em um DataFrame
df_todas = pd.DataFrame([P_t1, P_t2, P_t3, P_t4, P_t5], columns=tempos)

# 2. Análise de Incerteza (Média e Desvio Padrão)
P_media = df_todas.mean()
P_std = df_todas.std()

# 3. Modelagem do Estado Estacionário (Assíntota)
# Função matemática que descreve o aquecimento (decaimento da potência)
def decaimento_exponencial(t, P_inf, P_0, tau):
    return P_inf + (P_0 - P_inf) * np.exp(-t / tau)

# Chute inicial para os parâmetros [P_inf, P_0, tau] para ajudar o algoritmo
chute_inicial = [3.0, 3.5, 2.0]

# Aplicando o Curve Fitting aos dados médios
parametros_otimizados, covariancia = curve_fit(decaimento_exponencial, tempos, P_media, p0=chute_inicial)
P_inf_opt, P_0_opt, tau_opt = parametros_otimizados

# Criando um vetor de tempo estendido para visualizar o limite (ex: 20 minutos)
tempos_projecao = np.linspace(0, 20, 100)
P_projetada = decaimento_exponencial(tempos_projecao, P_inf_opt, P_0_opt, tau_opt)

# 4. Visualização Gráfica
fig, ax = plt.subplots(figsize=(10, 6))

# Plotando os dados reais com barras de erro (Incerteza)
ax.errorbar(tempos, P_media, yerr=P_std, fmt='o', color='black', 
            capsize=4, capthick=1.5, label='Dados Experimentais (Média $\pm$ Desvio Padrão)')

# Plotando a curva de modelagem com a projeção da assíntota
ax.plot(tempos_projecao, P_projetada, '--', color='tab:red', linewidth=2,
        label=f'Modelo Exponencial (Assíntota: {P_inf_opt:.3f} W)')

# Destacando a linha da assíntota horizontal
ax.axhline(y=P_inf_opt, color='gray', linestyle=':', label='Limite de Estabilidade Térmica')

# Formatação
ax.set_xlabel('Tempo (minutos)', fontsize=12)
ax.set_ylabel('Potência Dissipada (W)', fontsize=12)
ax.set_title('Decaimento da Potência com Incerteza e Projeção de Estado Estacionário', fontsize=14)
ax.set_xlim(-0.5, 20.5)
ax.legend()
ax.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()

# Resultados impressos para colocar no texto da tese
print("--- RESULTADOS DA MODELAGEM ---")
print(f"Potência Inicial Teórica (P_0): {P_0_opt:.3f} W")
print(f"Potência Final Estável (P_inf): {P_inf_opt:.3f} W")
print(f"Constante de Tempo (tau): {tau_opt:.3f} min")