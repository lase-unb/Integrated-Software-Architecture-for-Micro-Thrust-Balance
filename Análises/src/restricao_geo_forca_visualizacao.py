import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc

# Valores das dimensões (mm)
Lp_val = 367.5
R_coil_val = 1.59
r_core_val = 1.37
L_core_val = 12.70
clearance_val = R_coil_val - r_core_val
X_stroke_val = 1.27

# Cálculos dos ângulos reais
theta_sat_rad = np.arcsin(X_stroke_val / Lp_val)
theta_sat_deg = np.degrees(theta_sat_rad)
theta_max_rad = 0.0214 # Calculado anteriormente via Bhaskara
theta_max_deg = np.degrees(theta_max_rad)

# Configuração da figura
fig, ax = plt.subplots(figsize=(15, 9))
ax.set_aspect('equal')
ax.axis('off')

# --- 1. LVDT (Corte Transversal Principal) ---
coil_length = L_core_val + 8
ax.add_patch(Rectangle((-coil_length/2, R_coil_val), coil_length, 2.5, facecolor='#E8E8E8', edgecolor='#666666', hatch='///'))
ax.add_patch(Rectangle((-coil_length/2, -R_coil_val - 2.5), coil_length, 2.5, facecolor='#E8E8E8', edgecolor='#666666', hatch='///'))
ax.plot([-coil_length/2 - 2, coil_length/2 + 2], [0, 0], color='black', linestyle='-.', lw=0.8, alpha=0.6) # Eixo de simetria central

# Núcleo
ax.add_patch(Rectangle((-L_core_val/2, -r_core_val), L_core_val, 2*r_core_val, facecolor='steelblue', edgecolor='black', zorder=3))

# --- 2. LINHAS DE COTA LVDT ---
y_ext_Lnuc = R_coil_val + 4.5
ax.plot([-L_core_val/2, -L_core_val/2], [r_core_val, y_ext_Lnuc + 0.5], 'k--', lw=0.8)
ax.plot([L_core_val/2, L_core_val/2], [r_core_val, y_ext_Lnuc + 0.5], 'k--', lw=0.8)
ax.annotate('', xy=(-L_core_val/2, y_ext_Lnuc), xytext=(L_core_val/2, y_ext_Lnuc), arrowprops=dict(arrowstyle='<|-|>', facecolor='black', lw=1.2))
ax.text(0, y_ext_Lnuc + 0.5, r'$\mathbf{L_{nuc}}$', ha='center', fontsize=12)

x_ext_Rb = coil_length/2 + 1.5
ax.plot([coil_length/2, x_ext_Rb + 0.5], [R_coil_val, R_coil_val], 'r--', lw=0.8)
ax.plot([coil_length/2, x_ext_Rb + 0.5], [-R_coil_val, -R_coil_val], 'r--', lw=0.8)
ax.annotate('', xy=(x_ext_Rb, -R_coil_val), xytext=(x_ext_Rb, R_coil_val), arrowprops=dict(arrowstyle='<|-|>', facecolor='red', edgecolor='red', lw=1.2))
ax.text(x_ext_Rb + 0.5, 0, r'$\mathbf{2R_{bob}}$', color='red', va='center', fontsize=12, fontweight='bold')

x_ext_rn = -L_core_val/2 + 1.5 
ax.annotate('', xy=(x_ext_rn, -r_core_val), xytext=(x_ext_rn, r_core_val), arrowprops=dict(arrowstyle='<|-|>', facecolor='black', lw=1))
ax.text(x_ext_rn + 0.5, 0, r'$\mathbf{2r_{nuc}}$', color='white', va='center', ha='left', fontsize=11, fontweight='bold', bbox=dict(facecolor='black', alpha=0.5, pad=1, edgecolor='none'))

ax.annotate('Folga Radial\n$\Delta R$', xy=(0, R_coil_val - 0.1), xytext=(3, R_coil_val + 1.5),
            arrowprops=dict(arrowstyle='->', color='green', lw=1.5, connectionstyle="arc3,rad=-0.2"), color='green', fontsize=11, fontweight='bold')

ax.axvline(X_stroke_val, color='teal', linestyle=':', linewidth=2)
ax.axvline(-X_stroke_val, color='teal', linestyle=':', linewidth=2)
ax.text(X_stroke_val + 0.2, -R_coil_val - 1.5, r'$\mathbf{X_{sat}}$', color='teal', fontsize=11, fontweight='bold')

# --- 3. ESQUEMA CINEMÁTICO DO PÊNDULO (Para mostrar os ângulos) ---
pivot_x = -20
pivot_y = -1
pend_len = 8 # Comprimento representativo da haste

# Ângulos exagerados visualmente para o desenho técnico ser legível
vis_angle_sat = 15 # graus
vis_angle_max = 35 # graus

# Caixa ao redor do esquema cinemático
ax.add_patch(Rectangle((pivot_x - 6, pivot_y - pend_len - 3), 16, pend_len + 5, facecolor='none', edgecolor='#A0A0A0', linestyle='--', lw=1))
ax.text(pivot_x + 2, pivot_y + 2.5, 'Cinemática do Pêndulo\n(Ângulos Exagerados)', ha='center', fontsize=10, fontweight='bold', color='#444444')

# Pivot (Ponto de giro da balança)
ax.plot(pivot_x, pivot_y, 'ko', markersize=6)
ax.text(pivot_x, pivot_y + 0.5, 'Pivô', ha='center', fontsize=9)

# Linha de Repouso (Vertical, Pêndulo parado)
ax.plot([pivot_x, pivot_x], [pivot_y, pivot_y - pend_len], 'k--', lw=1)

# Linha correspondente à Saturação (theta_sat)
sat_x = pivot_x + pend_len * np.sin(np.radians(vis_angle_sat))
sat_y = pivot_y - pend_len * np.cos(np.radians(vis_angle_sat))
ax.plot([pivot_x, sat_x], [pivot_y, sat_y], color='teal', lw=2, linestyle='-')
ax.plot(sat_x, sat_y, 'o', color='teal', markersize=4)

# Linha correspondente ao Máximo Geométrico (theta_max)
max_x = pivot_x + pend_len * np.sin(np.radians(vis_angle_max))
max_y = pivot_y - pend_len * np.cos(np.radians(vis_angle_max))
ax.plot([pivot_x, max_x], [pivot_y, max_y], color='red', lw=2, linestyle='-')
ax.plot(max_x, max_y, 'o', color='red', markersize=4)

# Desenhando os arcos e indicando os thetas
# Theta Sat
arc_sat_r = 4.0
t_sat_vals = np.linspace(270, 270 + vis_angle_sat, 20) # 270 é o eixo Y para baixo (vertical)
ax.plot(pivot_x + arc_sat_r*np.cos(np.radians(t_sat_vals)), pivot_y + arc_sat_r*np.sin(np.radians(t_sat_vals)), color='teal', lw=1.5)
ax.text(pivot_x + arc_sat_r*np.cos(np.radians(270 + vis_angle_sat/2)) + 0.2, 
        pivot_y + arc_sat_r*np.sin(np.radians(270 + vis_angle_sat/2)) - 0.8, 
        r'$\mathbf{\theta_{sat}}$', color='teal', fontsize=11, fontweight='bold')

# Theta Max
arc_max_r = 6.0
t_max_vals = np.linspace(270, 270 + vis_angle_max, 20)
ax.plot(pivot_x + arc_max_r*np.cos(np.radians(t_max_vals)), pivot_y + arc_max_r*np.sin(np.radians(t_max_vals)), color='red', lw=1.5)
ax.text(pivot_x + arc_max_r*np.cos(np.radians(270 + vis_angle_max/2)) + 0.2, 
        pivot_y + arc_max_r*np.sin(np.radians(270 + vis_angle_max/2)) - 1.2, 
        r'$\mathbf{\theta_{max}}$', color='red', fontsize=11, fontweight='bold')

# Conexão visual tracejada entre o fim do pêndulo e o núcleo do LVDT
ax.annotate('', xy=(-L_core_val/2, 0), xytext=(pivot_x + 5, pivot_y - pend_len/2),
            arrowprops=dict(arrowstyle='->', color='#A0A0A0', lw=1, linestyle=':'))


# Ajuste fino dos limites da tela
ax.set_xlim(-28, coil_length/2 + 10)
ax.set_ylim(-13, 9)

plt.tight_layout()
plt.show()
