import numpy as np
import matplotlib.pyplot as plt

# Parâmetros Revisados do MHR 050
X_max = 1.27  # mm (Saturação do sinal do LVDT, limite nominal)
X_min = 0.001 # mm (Resolução adotada, 1 um)

# Vetor de sensibilidade contínuo (de 1 a 100 mm/mN)
S = np.linspace(1, 100, 500)

# Cálculo das forças em micro-Newtons (multiplicado por 1000 para converter mN para uN)
F_eq_max_uN = (X_max / S) * 1000
F_eq_min_uN = (X_min / S) * 1000

# Criando o plot
plt.figure(figsize=(9, 6))

# Plotando os limites inferior e superior
plt.plot(S, F_eq_max_uN, color='darkred', linewidth=2, label='$F_{eq, max}$ (Saturação MHR 050: 1.27 mm)')
plt.plot(S, F_eq_min_uN, color='navy', linewidth=2, linestyle='--', label='$F_{eq, min}$ (Resolução do Sistema: 1 $\mu$m)')

# Configurações estéticas e de eixo do gráfico
plt.yscale('log')
plt.title('Força Equivalente vs. Sensibilidade do Pêndulo', fontsize=14)
plt.xlabel('Sensibilidade da Balança $S$ (mm/mN)', fontsize=12)
plt.ylabel('Força Equivalente $F_{eq}$ ($\mu$N)', fontsize=12)
plt.grid(True, which="both", ls="--", alpha=0.6)

# Preenchendo a área útil de operação (Envelope de projeto)
plt.fill_between(S, F_eq_min_uN, F_eq_max_uN, color='lightgreen', alpha=0.3, label='Região de Operação Válida')
plt.legend(loc='upper right', fontsize=11)

plt.tight_layout()
plt.show()