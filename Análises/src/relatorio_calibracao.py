# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 15:23:44 2025

@author: Adm
"""
import os
import glob
import matplotlib.pyplot as plt # plotagem de gráficos
import pandas as pd # leitura e manipulação de dados
import numpy as np # operações numéricas
import math
from scipy import signal # processamento de sinais (filtros)

# ==============================================================================
# FUNÇÃO PARA PLOTAR A CURVA DE CALIBRAÇÃO E CALCULAR RIGIDEZ
# ==============================================================================
def plotar_curva_calibracao(Feq, deslocamento, desvio_padrao, save_path):
    print("\n" + "="*50)
    print("Gerando Curva de Calibração...")
    
    # Ajuste Linear (Regressão)
    k, a = np.polyfit(deslocamento, Feq, deg=1)

    # Cria pontos para desenhar a reta teórica no gráfico
    x_fit = np.linspace(min(deslocamento) - 0.0005, max(deslocamento) + 0.0005, 100)
    y_fit = k * x_fit + a

    # Plotagem do Gráfico
    plt.figure(figsize=(8, 6))

    # Plota os pontos com as barras de erro horizontais (xerr)
    plt.errorbar(deslocamento, Feq, xerr=desvio_padrao, fmt='o', color='red', 
                 ecolor='black', capsize=4, elinewidth=1.5, markeredgecolor='black',
                 label='Dados Experimentais ± Desvio Padrão')

    # Plota a reta de ajuste (k) tracejada
    plt.plot(x_fit, y_fit, '--k', alpha=0.7, label=f'Ajuste Linear (k = {k:.0f})')

    # Configurações Visuais
    plt.xlabel('Deslocamento (µm)', fontsize=12)
    plt.ylabel('Força Equivalente - Feq (µN)', fontsize=12)
    plt.title('Curva de Calibração: Força Equivalente vs Deslocamento', fontsize=14)

    # Adiciona grid, legenda e ajusta margens
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='upper left', fontsize=10)
    plt.tight_layout()

    # Salva a figura na pasta de resultados ANTES de exibir na tela
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Gráfico salvo em: {save_path}")

    # Exibe o gráfico na tela
    plt.show()

    # Imprime os resultados no terminal
    print(f"Rigidez Calculada (k): {k:.2f} µN/µm")
    print(f"Offset (a): {a:.2f} µN")
    print("="*50 + "\n")
    
    return k, a


# ==============================================================================
# CONFIGURAÇÃO DE DIRETÓRIOS E ARQUIVOS
# ==============================================================================
input_dir = r"C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\data\carga_constante\menor sensibilidade"
output_dir = r"C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\menor sensibilidade"
output_filename = "resultados_curvaCalibracao_menorSensibilidade.txt"

# Cria a pasta de resultados caso ela não exista
os.makedirs(output_dir, exist_ok=True)
output_filepath = os.path.join(output_dir, output_filename)

# ==============================================================================
# PARÂMETROS FÍSICOS E MAPEAMENTO DE NOMES (NOVA LÓGICA)
# ==============================================================================
g_local = 9.784 # Aceleração da gravidade local (m/s^2)
L = 0.3675      # Distância L em metros (367.5 mm)

massas_conhecidas = {
    'P1': 0.0011377, # kg
    'P2': 0.0014954, # kg
    'P3': 0.0022072, # kg
    'P4': 0.0032791, # kg
    'P5': 0.0033093, # kg
    'P6': 0.0043203, # kg
    'P7': 0.0055006  # kg
}

distancias_d = {
    'd1': 0.00552,  # metros
    'd2': 0.01052,  # metros
    'd3': 0.01552   # metros
}

# ==============================================================================
# PARÂMETROS INICIAIS DE PROCESSAMENTO DO SINAL
# ==============================================================================
find_diff=True
time1=[20,110]
time2=[150,240]

cutoff_freq=0.05
order=5

def find_nearest_index(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx

# Listas para armazenar os resultados
lista_forca = []
lista_deslocamento = []
lista_desvio_padrao = []

# ==============================================================================
# INÍCIO DO LOOP PARA LER TODOS OS ARQUIVOS DA PASTA
# ==============================================================================
arquivos_txt = glob.glob(os.path.join(input_dir, "*.txt"))

print(f"Encontrados {len(arquivos_txt)} arquivos para análise. Processando...")

for filepath in arquivos_txt:
    Filename = os.path.basename(filepath)
    
    # Reinicializa as listas de tempo e deslocamento para cada arquivo
    time = [] 
    d = []
    
    # ---------------------------------------------------------
    # NOVA LÓGICA: Extração de P e d a partir do nome do arquivo
    # ---------------------------------------------------------
    nome_sem_extensao = Filename.replace('.txt', '')
    partes = nome_sem_extensao.split('_') # Divide Ex: ['P2', 'd1', '1']
    
    forca_eq = np.nan
    
    if len(partes) >= 2:
        chave_P = partes[0]
        chave_d = partes[1]
        
        # Verifica se P e d existem nos nossos dicionários
        if chave_P in massas_conhecidas and chave_d in distancias_d:
            m_conhecida = massas_conhecidas[chave_P]
            dist_d = distancias_d[chave_d]
            
            # Cálculo da Força Equivalente (em Newtons)
            Feq_Newtons = m_conhecida * g_local * dist_d * (1/L)
            
            # Convertendo de Newtons para microNewtons (µN)
            forca_eq = Feq_Newtons * 1e6
        else:
            print(f"AVISO: Chaves não encontradas para o arquivo {Filename} ({chave_P}, {chave_d})")
            
    # ---------------------------------------------------------
    
    data = pd.read_csv(filepath, sep="\t", header=None)

    # CÁLCULOS DE FILTRO E DESLOCAMENTO
    for i in range(len(data[0])):
        time.append(float(data[0][i].replace(',', '.')))
        d.append(float(data[1][i].replace(',', '.'))*1000)

    N=len(d)
    fs=N/(float(data[0][N-1].replace(',', '.'))-float(data[0][0].replace(',', '.')))
    b, a = signal.butter(order, cutoff_freq, analog=False, btype='lowpass', fs=fs)
    av = signal.filtfilt(b, a, d)

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
        
        print(f'[{Filename}] Feq = {forca_eq:.3f}µN | Displacement = {diff:.5f}µm')
        
        disp_std=math.sqrt((std1**2)+(std2**2))
        
        lista_forca.append(forca_eq)
        lista_deslocamento.append(diff)
        lista_desvio_padrao.append(disp_std)

    # GERAÇÃO DOS GRÁFICOS INTERMEDIÁRIOS
    fig, ax = plt.subplots()
    ax.plot(time, d, linewidth=0.5)
    ax.plot(time, av, label=f'Average Butterwoth filter: order={order}, cutoff={cutoff_freq}Hz')

    if find_diff==True:
        ax.plot([startime1,endtime1], [av1, av1], 'k--', label=f'Average between {time1[0]} and {time1[1]}s = {av1:.5f}µm')
        ax.plot([startime1,endtime1], [av1+std1, av1+std1], 'r--', label=f'Standard Deviation = {std1:.5f}µm')
        ax.plot([startime1,endtime1], [av1-std1, av1-std1], 'r--')
        
        ax.plot([startime2,endtime2], [av2, av2], 'k--', label=f'Average between {time2[0]} and {time2[1]}s = {av2:.5f}µm')
        ax.plot([startime2,endtime2], [av2+std2, av2+std2], 'r--', label=f'Standard Deviation = {std2:.5f}µm')
        ax.plot([startime2,endtime2], [av2-std2, av2-std2], 'r--')
        
        ax.plot([time[-1],time[-1]], [av1, av2], linewidth=5.0, label=f'Displacement = {diff:.5f}µm ; std={disp_std:.5f}µm')
        
    ax.set(xlabel='Time (s)', ylabel='d (µm)')
    ax.set_title(f'Displacement for {Filename} (Feq={forca_eq:.3f}µN)')
    ax.grid()
    plt.legend()
    plt.close(fig) # Libera a memória fechando o gráfico em background

# ==============================================================================
# SALVAR O ARQUIVO DE RESULTADOS E PLOTAR A CURVA FINAL
# ==============================================================================
# Cria um DataFrame do pandas
df_resultados = pd.DataFrame({
    'Nome_Arquivo': [os.path.basename(fp) for fp in arquivos_txt],
    'Forca_Equivalente_uN': lista_forca,
    'Deslocamento_script_um': lista_deslocamento,
    'Desvio_Padrao_um': lista_desvio_padrao
})

# Remove arquivos onde a Feq não pôde ser calculada ou o Deslocamento deu falha
df_resultados = df_resultados.dropna()

if df_resultados.empty:
    print("\nERRO CRÍTICO: Nenhum dado válido foi extraído. Verifique os dicionários de massa/distância e os tempos de corte.")
else:
    # Ordenar pelos valores de força para o txt ficar organizado
    df_resultados = df_resultados.sort_values(by='Forca_Equivalente_uN')

    # Salva o arquivo como .txt separado por tabulação ('\t')
    df_resultados.to_csv(output_filepath, sep='\t', index=False, decimal=',')

    print("\n" + "="*50)
    print(f"Análise dos arquivos concluída com sucesso!")
    print(f"Arquivo salvo em: {output_filepath}")

    # Cria o caminho da imagem trocando a extensão de .txt para .png
    image_filepath = output_filepath.replace('.txt', '.png')

    # Chama a função para calcular a rigidez e mostrar o gráfico, passando o caminho para salvar
    plotar_curva_calibracao(
        Feq=df_resultados['Forca_Equivalente_uN'].values,
        deslocamento=df_resultados['Deslocamento_script_um'].values,
        desvio_padrao=df_resultados['Desvio_Padrao_um'].values,
        save_path=image_filepath
    )