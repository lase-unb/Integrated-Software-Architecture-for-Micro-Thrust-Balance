import numpy as np
from scipy.optimize import fsolve

def resolver_limites_lvdt(Lp_mm=367.5):
    # Parâmetros do LVDT em mm
    R_bobina = 3.18 / 2
    r_nucleo = 2.74 / 2
    L_nucleo = 12.70
    
    # Função da restrição geométrica
    def equacao(theta):
        Y_pendulo = Lp_mm * (1 - np.cos(theta))
        Y_inclinacao = (L_nucleo / 2) * np.sin(theta)
        Y_raio = r_nucleo * np.cos(theta)
        return Y_pendulo + Y_inclinacao + Y_raio - R_bobina
    
    # Chute inicial de 0.01 grau (em radianos)
    chute_inicial = np.radians(0.00174)
    
    # Resolver
    theta_max_rad = fsolve(equacao, chute_inicial)[0]
    theta_max_deg = np.degrees(theta_max_rad)
    
    # Deslocamento horizontal
    deslocamento_max = Lp_mm * np.sin(theta_max_rad)
    
    return theta_max_deg, deslocamento_max

angulo, deslocamento = resolver_limites_lvdt()

print(f"Ângulo Máximo: {angulo:.3f} graus")
print(f"Deslocamento Máximo: {deslocamento:.3f} mm")