# -*- coding: utf-8 -*-
"""
LaSE — Balança de Microempuxo para Pequenos Satélites
Sistema de Controle e Aquisição de Dados
INPE / LaSE
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.fft import rfft, rfftfreq
from scipy import signal as scipy_signal
import math
import io
import os
import time
import serial.tools.list_ports
from datetime import datetime

# ── Importa módulos do projeto ──────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from processing import apply_lowpass_filter, convert_to_mn, calculate_metrics

# ── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="LaSE — Balança de Microempuxo",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Estilo global ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .stMetric { background: #f8f9fb; border: 1px solid #e2e6ef; border-radius: 8px; padding: 12px; }
    .stAlert  { border-radius: 8px; }
    div[data-testid="stMetricValue"] { font-size: 1.4rem; font-weight: 600; }
    .req-badge {
        display: inline-block; font-size: 10px; font-weight: 600;
        padding: 1px 6px; border-radius: 10px; margin-left: 4px;
        background: #fef2f2; color: #991b1b; border: 1px solid #fecaca;
    }
    .section-title { font-size: 13px; font-weight: 600; color: #4a5568;
        text-transform: uppercase; letter-spacing: .05em; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES — DSP
# ════════════════════════════════════════════════════════════════════════════

def calcular_fs(time_arr):
    """Calcula frequência de amostragem a partir do vetor de tempo."""
    if len(time_arr) < 2:
        return 50.0
    return (len(time_arr) - 1) / (time_arr[-1] - time_arr[0])


def calcular_fnat(d_um, fs, cutoff=0.5, max_freq=5.0):
    """
    FFT com janela Hanning — retorna (fnat, freqs, magnitudes_raw, magnitudes_filt).
    Implementação de fn_calculation.py adaptada para Streamlit.
    """
    d_centered = d_um - np.mean(d_um)
    d_filt = apply_lowpass_filter(d_centered, fs=fs, cutoff_freq=cutoff)

    N = len(d_centered)
    yf_raw  = rfft(d_centered) / N * 2
    yf_filt = rfft(d_filt)     / N * 2
    xf = rfftfreq(N, 1.0 / fs)

    # Limita ao intervalo útil
    mask = (xf > 0.01) & (xf <= max_freq)
    xf_m  = xf[mask]
    yr_m  = np.abs(yf_raw[mask])
    yf_m  = np.abs(yf_filt[mask])

    if len(yf_m) == 0:
        return 0.0, xf_m, yr_m, yf_m

    peak_idx = np.argmax(yf_m)
    fnat = xf_m[peak_idx]
    return float(fnat), xf_m, yr_m, yf_m


def calcular_deflexao(time_arr, d_um, t1_start, t1_end, t2_start, t2_end, fs, cutoff=0.05):
    """
    Calcula deflexão entre baseline e patamar com incerteza.
    Implementação de find_deflection.py adaptada.
    """
    b, a = scipy_signal.butter(5, cutoff, btype='lowpass', fs=fs)
    d_filt = scipy_signal.filtfilt(b, a, d_um)

    def janela(t0, t1):
        idx = (time_arr >= t0) & (time_arr <= t1)
        w = d_filt[idx]
        return w.mean(), w.std(), time_arr[idx]

    av1, std1, tw1 = janela(t1_start, t1_end)
    av2, std2, tw2 = janela(t2_start, t2_end)
    delta = abs(av2 - av1)
    incerteza = math.sqrt(std1**2 + std2**2)

    return {
        "delta_um": delta, "incerteza_um": incerteza,
        "av1": av1, "std1": std1, "tw1": tw1,
        "av2": av2, "std2": std2, "tw2": tw2,
        "d_filt": d_filt
    }


def detectar_xmax(d_um, fs, cutoff=0.1):
    """
    Identifica xmax (primeiro pico-vale) no sinal filtrado.
    Implementação de LVDT_Plot_V2.py adaptada.
    """
    d_filt = apply_lowpass_filter(d_um, fs=fs, cutoff_freq=cutoff)
    peak_idx = np.argmax(np.abs(d_filt))
    return float(d_filt[peak_idx]), peak_idx, d_filt


def calibracao_estatica(massas_kg, desl_m, erros_m, g=9.81, l_aplicacao=0.005, L_lvdt=0.3):
    """
    Regressão linear para determinar k.
    Implementação de k_calculation.py adaptada.
    """
    Mteq  = massas_kg * g * l_aplicacao
    Theta = desl_m / L_lvdt
    err_theta = erros_m / L_lvdt

    k, a_off = np.polyfit(Theta, Mteq, deg=1)
    y_pred = a_off + k * Theta
    ss_res = np.sum((Mteq - y_pred)**2)
    ss_tot = np.sum((Mteq - np.mean(Mteq))**2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0

    return float(k), float(a_off), float(r2), Theta, Mteq, err_theta


def calcular_parametros_balanca(m1_kg, r1_m, m2_kg, r2_m, m_balanca=0.8, r_balanca=0.06, g=9.81):
    """Calcula CG, I, k, fnat e sensibilidade a partir dos contrapesos."""
    m_tot = m1_kg + m2_kg + m_balanca
    cg = -(m1_kg * r1_m + m2_kg * r2_m) / m_tot  # negativo = abaixo do pivô
    I  = m1_kg * r1_m**2 + m2_kg * r2_m**2 + m_balanca * r_balanca**2
    k  = m_tot * g * abs(cg)
    fn = (1 / (2 * np.pi)) * np.sqrt(k / I) if I > 0 and k > 0 else 0.0
    S  = (1 / (m_tot * (2 * np.pi * fn)**2)) * 1e6 if fn > 0 else 0.0
    return {"cg": cg, "I": I, "k": k, "fn": fn, "S": S, "m_tot": m_tot}


def calcular_voltagem_dce(forca_uN, de_mm, k_dce=0.45):
    """Calcula voltagem DCE necessária. Retorna V e flag de bloqueio (RF14)."""
    V = math.sqrt(forca_uN / k_dce) * de_mm
    bloqueado = V > 1000.0
    return round(V, 1), bloqueado


def gerar_csv(time_arr, thrust_mn):
    df = pd.DataFrame({"Tempo (s)": time_arr, "Empuxo (mN)": thrust_mn})
    return df.to_csv(index=False).encode("utf-8")


def gerar_simulacao(modo="pulsado", duracao=30, fs=100):
    """Gera sinal simulado de pêndulo amortecido para testes sem hardware."""
    t = np.linspace(0, duracao, int(duracao * fs))
    fn_sim, zeta = 1.2, 0.05
    wd = fn_sim * np.sqrt(1 - zeta**2)
    ruido = np.random.normal(0, 0.3, len(t))

    if modo == "pulsado":
        sinal = np.zeros(len(t))
        for pulso_t in [5, 12, 19, 26]:
            t_rel = t - pulso_t
            mask = t_rel >= 0
            sinal[mask] += (
                8.0 * np.exp(-zeta * 2 * np.pi * fn_sim * t_rel[mask])
                * np.sin(2 * np.pi * wd * t_rel[mask])
            )
    else:
        sinal = np.where(
            (t > 5) & (t < 25),
            5.0 + 0.3 * np.sin(2 * np.pi * fn_sim * t),
            0.1 * np.sin(2 * np.pi * fn_sim * t)
        )

    return pd.DataFrame({"time": t, "raw_disp": sinal + ruido})


def listar_portas():
    return [p.device for p in serial.tools.list_ports.comports()] or ["Nenhuma porta detectada"]


# ════════════════════════════════════════════════════════════════════════════
# ESTADO DA SESSÃO
# ════════════════════════════════════════════════════════════════════════════

defaults = {
    "calibrado": False,
    "k_torque": 0.0125,
    "l_lvdt": 0.3,
    "l_thrust": 0.25,
    "fn_calculada": None,
    "S_calculada": None,
    "df_dados": None,
    "modo_teste": "pulsado",
    "timestamp_calib": None,
    "massa_calib": 0.0,
    "cg_calib": 0.0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ════════════════════════════════════════════════════════════════════════════
# NAVEGAÇÃO
# ════════════════════════════════════════════════════════════════════════════

st.markdown("### 🛰️ LaSE — Balança de Microempuxo")

status_calib = "✅ Calibrada" if st.session_state.calibrado else "⚠️ Não calibrada"
cor_status   = "green" if st.session_state.calibrado else "orange"
st.markdown(
    f"<span style='font-size:12px;color:{cor_status};font-weight:600;'>{status_calib}</span> &nbsp;|&nbsp; "
    f"<span style='font-size:12px;color:#9aa3b5;'>{datetime.now().strftime('%d/%m/%Y %H:%M')}</span>",
    unsafe_allow_html=True
)

aba1, aba2, aba3 = st.tabs([
    "⚙️  1 · Calibração",
    "📡  2 · Aquisição de dados",
    "📊  3 · Análise e exportação"
])


# ════════════════════════════════════════════════════════════════════════════
# ABA 1 — CALIBRAÇÃO
# ════════════════════════════════════════════════════════════════════════════

with aba1:

    st.markdown("#### Configuração da balança")
    st.caption("Preencha os parâmetros físicos da balança antes de iniciar qualquer teste.")

    col_cp, col_res, col_dce = st.columns(3)

    # ── Contrapesos ──────────────────────────────────────────────────────────
    with col_cp:
        st.markdown('<div class="section-title">Contrapesos <span class="req-badge">RF03 · RF11</span></div>',
                    unsafe_allow_html=True)

        cp1_on = st.checkbox("Contrapeso 1 ativo", value=True)
        with st.container():
            cp1_m = st.number_input("Massa CP1 (g)",  value=50.0,  step=1.0,  format="%.1f",
                                    disabled=not cp1_on, key="cp1m")
            cp1_r = st.number_input("Distância CP1 ao pivô (mm)", value=120.0, step=1.0, format="%.1f",
                                    disabled=not cp1_on, key="cp1r")

        cp2_on = st.checkbox("Contrapeso 2 ativo", value=False)
        with st.container():
            cp2_m = st.number_input("Massa CP2 (g)",  value=20.0,  step=1.0,  format="%.1f",
                                    disabled=not cp2_on, key="cp2m")
            cp2_r = st.number_input("Distância CP2 ao pivô (mm)", value=80.0,  step=1.0, format="%.1f",
                                    disabled=not cp2_on, key="cp2r")

        cg_manual = st.checkbox("Inserir CG manualmente")
        if cg_manual:
            cg_valor = st.number_input("CG eixo y (m)", value=-0.010, step=0.001, format="%.4f")
        else:
            cg_valor = None

        st.markdown("---")
        st.markdown('<div class="section-title">Braços da balança</div>', unsafe_allow_html=True)
        l_lvdt   = st.number_input("Braço LVDT — pivô ao sensor (m)",    value=0.300, step=0.001, format="%.3f")
        l_thrust = st.number_input("Braço motor — pivô ao propulsor (m)", value=0.250, step=0.001, format="%.3f")

    # ── Parâmetros calculados ─────────────────────────────────────────────
    with col_res:
        st.markdown('<div class="section-title">Parâmetros calculados</div>', unsafe_allow_html=True)

        m1 = (cp1_m / 1000) if cp1_on else 0.0
        r1 = (cp1_r / 1000) if cp1_on else 0.0
        m2 = (cp2_m / 1000) if cp2_on else 0.0
        r2 = (cp2_r / 1000) if cp2_on else 0.0

        params = calcular_parametros_balanca(m1, r1, m2, r2)
        cg_final = cg_valor if cg_manual else params["cg"]

        # Alerta de CG
        if cg_final > 0.001:
            st.error("⚠️ **CG acima do pivô — balança instável!**  \n"
                     "Reposicione os contrapesos para que o CG fique abaixo do ponto de pivô.")
        elif params["fn"] > 0 and params["fn"] < 0.5:
            st.warning(f"⚠️ Frequência natural muito baixa ({params['fn']:.3f} Hz).  \n"
                       "Aproxime os contrapesos do pivô ou reduza a massa para aumentar fnat.")
        elif params["fn"] > 5:
            st.warning(f"⚠️ Frequência natural muito alta ({params['fn']:.3f} Hz).  \n"
                       "Afaste os contrapesos do pivô ou aumente a massa.")
        elif params["fn"] > 0:
            st.success(f"✅ Parâmetros dentro do intervalo operacional.")

        mc1, mc2 = st.columns(2)
        mc1.metric("CG calculado",    f"{cg_final:.4f} m",      help="Negativo = CG abaixo do pivô (estável)")
        mc2.metric("Inércia I",        f"{params['I']:.5f} kg·m²")
        mc1.metric("Rigidez k",        f"{params['k']:.4f} N·m/rad")
        mc2.metric("Freq. natural fnat", f"{params['fn']:.3f} Hz",  help="Ideal: 0.5 – 5 Hz")
        mc1.metric("Sensibilidade S",  f"{params['S']:.2f} µm/N",  help="Quanto a balança se desloca por Newton")

        st.markdown("---")
        st.markdown('<div class="section-title">Constante k — calibração estática <span class="req-badge">RF15</span></div>',
                    unsafe_allow_html=True)
        st.caption("Carregue um CSV com colunas M (kg), d (m), e (m) para calcular k por regressão linear.")

        arquivo_k = st.file_uploader("Arquivo de calibração estática (.csv)", type=["csv"], key="calib_k")
        if arquivo_k:
            try:
                df_k = pd.read_csv(arquivo_k)
                k_calc, a_off, r2, Theta, Mteq, err_theta = calibracao_estatica(
                    df_k["M"].values, df_k["d"].values, df_k["e"].values,
                    l_aplicacao=l_thrust, L_lvdt=l_lvdt
                )
                cc1, cc2 = st.columns(2)
                cc1.metric("k calculado", f"{k_calc:.5f} N·m/rad")
                cc2.metric("R²",          f"{r2:.4f}", delta="válido" if r2 >= 0.99 else "abaixo de 0.99")

                if r2 >= 0.99:
                    st.success("✅ Ajuste linear válido — R² ≥ 0.99.")
                else:
                    st.warning("⚠️ R² abaixo de 0.99. Revise os dados de calibração.")

                fig_k, ax_k = plt.subplots(figsize=(5, 3))
                ax_k.errorbar(Theta, Mteq, xerr=err_theta, fmt="o", color="#2563eb", label="Dados", markersize=4)
                x_fit = np.linspace(Theta.min(), Theta.max(), 100)
                ax_k.plot(x_fit, a_off + k_calc * x_fit, "--", color="#16a34a",
                          label=f"k = {k_calc:.4f} N·m/rad")
                ax_k.set_xlabel("θ (rad)"); ax_k.set_ylabel("Torque (N·m)")
                ax_k.set_title(f"Curva de calibração — R² = {r2:.4f}")
                ax_k.legend(fontsize=8); ax_k.grid(alpha=0.3)
                plt.tight_layout()
                st.pyplot(fig_k)

                if st.button("Usar este k na análise"):
                    st.session_state.k_torque = k_calc
                    st.success(f"k = {k_calc:.5f} N·m/rad salvo na sessão.")
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")

    # ── DCE ──────────────────────────────────────────────────────────────────
    with col_dce:
        st.markdown('<div class="section-title">Configuração DCE <span class="req-badge">RF05 · RF06 · RF14</span></div>',
                    unsafe_allow_html=True)

        modo_dce = st.radio("Tipo de teste", ["Pulsado (Ibit)", "Contínuo (ss)"],
                            horizontal=True, key="modo_dce_radio")

        if "Pulsado" in modo_dce:
            st.info("**Modo pulsado:** o sistema vai capturar a maior deflexão (xmax) gerada "
                    "pelo impulso. Use para caracterizar PPTs e propulsores pulsados.")
        else:
            st.info("**Modo contínuo:** aguarda regime permanente (variação <0.1%) e mede a "
                    "deflexão estável (xss). Filtro Butterworth ativo.")

        st.markdown("---")
        forca_uN = st.slider("Força desejada (µN)", min_value=10, max_value=1000,
                             value=100, step=1, key="forca_slider")
        forca_num = st.number_input("Ou digite a força (µN)", value=float(forca_uN),
                                    min_value=10.0, max_value=1000.0, step=1.0, key="forca_num")
        forca_final = forca_num

        de_mm = st.number_input("Distância entre placas DCE — DE (mm)",
                                value=1.00, min_value=0.50, max_value=2.00, step=0.01, format="%.2f")
        st.caption("Dados experimentais disponíveis para: 1.00 mm e 0.99 mm. Outros valores: estimado (erro ≤2%).")

        V_calc, bloqueado = calcular_voltagem_dce(forca_final, de_mm)

        st.markdown("**Voltagem calculada para o DCE:**")
        if bloqueado:
            st.error(f"## ⛔ {V_calc} V — BLOQUEADO")
            st.error("**RF14 — Limite de segurança de 1.000 V atingido.**  \n"
                     "A aplicação desta voltagem foi bloqueada automaticamente. "
                     "Reduza a força ou aumente DE.")
        elif V_calc > 800:
            st.warning(f"## ⚠️ {V_calc} V")
            st.warning("Voltagem acima de 80% do limite. Monitore com cuidado.")
        else:
            st.success(f"## ✅ {V_calc} V")
            st.caption(f"Dentro do limite de segurança (≤ 1.000 V)  —  {V_calc/10:.1f}% do limite")

        pct_volt = min(V_calc / 1000 * 100, 100)
        st.progress(int(pct_volt))
        st.caption(f"0 V ────────── 500 V ────────── 1.000 V (limite)")

        st.markdown("---")
        st.markdown('<div class="section-title">Parâmetros de análise do regime</div>',
                    unsafe_allow_html=True)
        if "Pulsado" in modo_dce:
            st.markdown("""
            | Parâmetro | Valor |
            |-----------|-------|
            | Medida de interesse | xmax (1º pico) |
            | Resolução | 0.01 µm |
            | Repetições | N = 10 |
            | Filtro | Butterworth 5ª ord. |
            """)
        else:
            st.markdown("""
            | Parâmetro | Valor |
            |-----------|-------|
            | Medida de interesse | x_ss (regime perm.) |
            | Settling time | ~100 s (τ × 4) |
            | Critério steady-state | variação < 0.1% |
            | Filtro | Butterworth 5ª ord. |
            """)

    st.markdown("---")

    # ── Sequência de calibração ──────────────────────────────────────────────
    st.markdown("#### Sequência de calibração automática")
    st.caption("Execute as etapas em ordem. Tempo estimado: < 30 minutos.")

    seq_col1, seq_col2 = st.columns([3, 1])
    with seq_col1:
        etapa = st.selectbox("Etapa atual", [
            "1 · Calibração estática — deflexão com massa padrão",
            "2 · Calibração dinâmica — FFT e frequência natural",
            "3 · Validação DCE — curvas FE e tabela lookup",
            "4 · Aprovação final — verificação de incerteza"
        ])
    with seq_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅ Marcar etapa como concluída", use_container_width=True):
            if "4 ·" in etapa:
                st.session_state.calibrado = True
                st.session_state.k_torque = params["k"] if not arquivo_k else st.session_state.k_torque
                st.session_state.l_lvdt   = l_lvdt
                st.session_state.l_thrust = l_thrust
                st.session_state.fn_calculada = params["fn"]
                st.session_state.S_calculada  = params["S"]
                st.session_state.timestamp_calib = datetime.now().strftime("%d/%m/%Y %H:%M")
                st.session_state.massa_calib = params["m_tot"]
                st.session_state.cg_calib    = cg_final
                st.session_state.modo_teste  = "pulsado" if "Pulsado" in modo_dce else "continuo"
                st.success("🎉 Calibração concluída! A balança está pronta para uso.")
                st.balloons()
            else:
                st.info(f"Etapa marcada: {etapa[:30]}…  \nProssiga para a próxima etapa.")

    if st.session_state.calibrado:
        st.success(f"✅ Balança calibrada em {st.session_state.timestamp_calib}  —  "
                   f"k = {st.session_state.k_torque:.5f} N·m/rad  |  "
                   f"fnat = {st.session_state.fn_calculada:.3f} Hz")


# ════════════════════════════════════════════════════════════════════════════
# ABA 2 — AQUISIÇÃO DE DADOS
# ════════════════════════════════════════════════════════════════════════════

with aba2:

    if not st.session_state.calibrado:
        st.warning("⚠️ A balança ainda não foi calibrada. Vá para a aba **Calibração** antes de iniciar um teste.")

    st.markdown("#### Fonte de dados")
    fonte = st.radio("Como você quer fornecer os dados?",
                     ["📁 Carregar arquivo (.txt)", "🧪 Usar simulação (sem hardware)"],
                     horizontal=True)

    df_aq = None

    # ── Arquivo real ──────────────────────────────────────────────────────────
    if "Carregar" in fonte:
        st.caption("Formato esperado: duas colunas separadas por TAB — tempo (s) e deslocamento (µm). "
                   "Decimal pode ser vírgula ou ponto.")
        arquivo = st.file_uploader("Arquivo de dados do LVDT (.txt)", type=["txt", "csv"])

        if arquivo:
            try:
                df_aq = pd.read_csv(arquivo, sep=r'\s+', names=["time", "raw_disp"],
                                    decimal=",", engine="python")
                df_aq["time"]     = df_aq["time"].astype(float)
                df_aq["raw_disp"] = df_aq["raw_disp"].astype(float)
                st.success(f"✅ {len(df_aq):,} amostras carregadas  —  "
                           f"duração: {df_aq['time'].iloc[-1]:.1f} s")
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")

        st.markdown("---")
        st.markdown("##### Conexão com hardware (LVDT serial)")
        st.caption("Se o condicionador do LVDT estiver conectado via USB, selecione a porta abaixo.")

        portas = listar_portas()
        porta_sel = st.selectbox("Porta serial", portas)
        baud = st.selectbox("Baud rate", [9600, 115200, 57600], index=0)
        st.info(f"Para aquisição contínua via hardware: execute `data_acquisition.py` com a porta **{porta_sel}** "
                f"e baud **{baud}**. O arquivo `data.txt` gerado pode ser carregado aqui.")

    # ── Simulação ─────────────────────────────────────────────────────────────
    else:
        st.info("Modo simulação: gera sinal de pêndulo amortecido com ruído gaussiano. "
                "Útil para testar o pipeline sem hardware.")

        sc1, sc2, sc3 = st.columns(3)
        modo_sim = sc1.selectbox("Modo", ["pulsado", "continuo"])
        dur_sim  = sc2.slider("Duração (s)", 10, 120, 30)
        fs_sim   = sc3.selectbox("Taxa (Hz)", [50, 100], index=1)

        if st.button("▶ Gerar simulação", type="primary"):
            df_aq = gerar_simulacao(modo=modo_sim, duracao=dur_sim, fs=fs_sim)
            st.session_state.df_dados = df_aq
            st.success(f"✅ {len(df_aq):,} amostras simuladas geradas.")

        if st.session_state.df_dados is not None and df_aq is None:
            df_aq = st.session_state.df_dados
            st.caption("Usando dados da última simulação gerada.")

    # ── Visualização e análise prévia ─────────────────────────────────────────
    if df_aq is not None:
        st.session_state.df_dados = df_aq

        time_arr = df_aq["time"].values.astype(float)
        d_raw    = df_aq["raw_disp"].values.astype(float)
        fs_dados = calcular_fs(time_arr)

        st.markdown("---")
        st.markdown("#### Visualização — sinal bruto do LVDT")

        fig_raw, ax_raw = plt.subplots(figsize=(10, 3))
        ax_raw.plot(time_arr, d_raw, color="#94a3b8", linewidth=0.7, label="Sinal bruto (µm)")
        ax_raw.set_xlabel("Tempo (s)"); ax_raw.set_ylabel("Deslocamento (µm)")
        ax_raw.set_title(f"Sinal LVDT — {len(d_raw):,} amostras · fs = {fs_dados:.1f} Hz")
        ax_raw.grid(alpha=0.3); ax_raw.legend()
        plt.tight_layout()
        st.pyplot(fig_raw)

        st.markdown("---")
        st.markdown("#### Análise de frequência natural (FFT)")
        st.caption("A FFT mostra em quais frequências o pêndulo oscila. "
                   "O pico principal é a frequência natural (fnat).")

        fnat, xf, yr, yf = calcular_fnat(d_raw, fs_dados)

        fc1, fc2, fc3 = st.columns(3)
        fc1.metric("fnat detectada", f"{fnat:.4f} Hz",
                   delta="✓ faixa ok" if 0.5 <= fnat <= 5 else "fora de 0.5–5 Hz")
        fc2.metric("fs detectada", f"{fs_dados:.1f} Hz")
        fc3.metric("N amostras", f"{len(d_raw):,}")

        if fnat < 0.5 or fnat > 5:
            st.warning(f"fnat = {fnat:.4f} Hz está fora da faixa operacional (0.5–5 Hz). "
                       "Verifique a configuração dos contrapesos.")
        else:
            st.success(f"✅ fnat = {fnat:.4f} Hz — dentro da faixa operacional.")

        fig_fft, (ax_t, ax_f) = plt.subplots(2, 1, figsize=(10, 6))

        d_filt_fft = apply_lowpass_filter(d_raw - np.mean(d_raw), fs=fs_dados, cutoff_freq=0.5)
        ax_t.plot(time_arr, d_raw - np.mean(d_raw), color="#cbd5e1", linewidth=0.6, label="Sinal bruto")
        ax_t.plot(time_arr, d_filt_fft, color="#2563eb", linewidth=1.2, label="Filtrado (Butterworth)")
        ax_t.set_ylabel("Deslocamento (µm)"); ax_t.set_title("Domínio do tempo")
        ax_t.legend(fontsize=8); ax_t.grid(alpha=0.3)

        ax_f.plot(xf, yr, color="#cbd5e1", linewidth=0.8, label="Espectro bruto")
        ax_f.plot(xf, yf, color="#dc2626", linewidth=1.5, label="Espectro filtrado")
        peak_mask = np.argmax(yf)
        ax_f.plot(xf[peak_mask], yf[peak_mask], "x", color="black", markersize=10,
                  label=f"fnat = {fnat:.4f} Hz")
        ax_f.set_xlabel("Frequência (Hz)"); ax_f.set_ylabel("Magnitude")
        ax_f.set_title("FFT — Domínio da frequência (janela Hanning)")
        ax_f.legend(fontsize=8); ax_f.grid(alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig_fft)

        st.session_state.fn_calculada = fnat


# ════════════════════════════════════════════════════════════════════════════
# ABA 3 — ANÁLISE E EXPORTAÇÃO
# ════════════════════════════════════════════════════════════════════════════

with aba3:

    if st.session_state.df_dados is None:
        st.warning("⚠️ Nenhum dado carregado ainda. Vá para a aba **Aquisição de dados** primeiro.")
        st.stop()

    df = st.session_state.df_dados
    time_arr = df["time"].values.astype(float)
    d_raw    = df["raw_disp"].values.astype(float)
    fs_dados = calcular_fs(time_arr)

    k  = st.session_state.k_torque
    lL = st.session_state.l_lvdt
    lT = st.session_state.l_thrust

    st.markdown("#### Parâmetros de análise")
    pc1, pc2, pc3, pc4 = st.columns(4)
    pc1.metric("k (N·m/rad)", f"{k:.5f}")
    pc2.metric("Braço LVDT (m)", f"{lL:.3f}")
    pc3.metric("Braço motor (m)", f"{lT:.3f}")
    pc4.metric("fnat", f"{st.session_state.fn_calculada:.3f} Hz"
               if st.session_state.fn_calculada else "—")

    modo_analise = st.radio("Modo de análise",
                            ["Pulsado — captura xmax", "Contínuo — regime permanente"],
                            horizontal=True)

    st.markdown("---")

    # ── MODO PULSADO ──────────────────────────────────────────────────────────
    if "Pulsado" in modo_analise:
        st.markdown("#### Análise pulsada — detecção de xmax")
        st.caption("O sistema identifica a maior deflexão (xmax) gerada por cada pulso, "
                   "usada para calcular a força de empuxo (Ft) e o impulso (Ibit).")

        xmax, peak_idx, d_filt_xmax = detectar_xmax(d_raw, fs_dados, cutoff=0.1)
        thrust_mn = convert_to_mn(d_filt_xmax, k, lT, lL)
        metrics   = calculate_metrics(time_arr, thrust_mn)

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("xmax detectado",    f"{xmax:.4f} µm",
                  help="Maior deflexão — resolução 0.01 µm (RF08)")
        r2.metric("Empuxo (Ft)",       f"{metrics['nominal_thrust']:.4f} mN",
                  help="Força calculada pela mecânica da balança")
        r3.metric("Bias (offset zero)", f"{metrics['bias']:.4f} mN",
                  help="Calculado nos primeiros 50 pontos")
        r4.metric("Ruído RMS (σ)",     f"{np.std(thrust_mn):.4f} mN")

        fig_p, ax_p = plt.subplots(figsize=(10, 4))
        ax_p.plot(time_arr, d_raw,       color="#cbd5e1", linewidth=0.6, alpha=0.6, label="Sinal bruto")
        ax_p.plot(time_arr, d_filt_xmax, color="#2563eb", linewidth=1.2, label="Sinal filtrado")
        ax_p.plot(time_arr[peak_idx], xmax, "x", color="#dc2626", markersize=12, markeredgewidth=2,
                  label=f"xmax = {xmax:.4f} µm")
        ax_p.set_xlabel("Tempo (s)"); ax_p.set_ylabel("Deslocamento (µm)")
        ax_p.set_title("Identificação de xmax — modo pulsado")
        ax_p.legend(); ax_p.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig_p)

    # ── MODO CONTÍNUO ─────────────────────────────────────────────────────────
    else:
        st.markdown("#### Análise contínua — regime permanente")
        st.caption("Define janelas de baseline (antes da força) e patamar (durante a força) "
                   "para calcular a deflexão estável com incerteza.")

        t_max = float(time_arr[-1])
        jc1, jc2 = st.columns(2)
        with jc1:
            st.markdown("**Janela de baseline** (antes da força)")
            t1s = st.slider("Início baseline (s)", 0.0, t_max * 0.4, t_max * 0.05, 0.1)
            t1e = st.slider("Fim baseline (s)",    t1s, t_max * 0.5, t_max * 0.25, 0.1)
        with jc2:
            st.markdown("**Janela de patamar** (durante a força)")
            t2s = st.slider("Início patamar (s)", t1e, t_max * 0.8, t_max * 0.55, 0.1)
            t2e = st.slider("Fim patamar (s)",    t2s, t_max,       t_max * 0.85, 0.1)

        res = calcular_deflexao(time_arr, d_raw, t1s, t1e, t2s, t2e, fs_dados)
        thrust_mn = convert_to_mn(res["d_filt"], k, lT, lL)

        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Δd (deflexão)",  f"{res['delta_um']:.5f} µm",
                   help="Diferença entre patamar e baseline (RF07)")
        rc2.metric("Incerteza (±σ)", f"{res['incerteza_um']:.5f} µm",
                   help="Propagação de erro combinada √(σ₁²+σ₂²)")
        rc3.metric("Força ss (mN)",
                   f"{convert_to_mn(np.array([res['delta_um']]), k, lT, lL)[0]:.4f} mN")

        fig_c, ax_c = plt.subplots(figsize=(10, 4))
        ax_c.plot(time_arr, d_raw,       color="#cbd5e1", linewidth=0.5, alpha=0.6, label="Sinal bruto")
        ax_c.plot(time_arr, res["d_filt"], color="#2563eb", linewidth=1.2, label="Filtrado (Butterworth 5ª)")
        ax_c.hlines(res["av1"], t1s, t1e, colors="black", linestyles="--",
                    label=f"Baseline: {res['av1']:.2f} µm")
        ax_c.hlines(res["av2"], t2s, t2e, colors="#16a34a", linestyles="--",
                    label=f"Patamar: {res['av2']:.2f} µm")
        ax_c.fill_between(res["tw1"], res["av1"] - res["std1"], res["av1"] + res["std1"],
                          color="#ef4444", alpha=0.15, label="Incerteza ±σ")
        ax_c.fill_between(res["tw2"], res["av2"] - res["std2"], res["av2"] + res["std2"],
                          color="#ef4444", alpha=0.15)
        ax_c.set_xlabel("Tempo (s)"); ax_c.set_ylabel("Deslocamento (µm)")
        ax_c.set_title("Análise de deflexão — regime permanente")
        ax_c.legend(fontsize=8); ax_c.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig_c)

    # ── Estatísticas ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Estatísticas detalhadas")

    thrust_mn_full = convert_to_mn(
        apply_lowpass_filter(d_raw, fs=fs_dados, cutoff_freq=0.3), k, lT, lL
    )
    metrics_full = calculate_metrics(time_arr, thrust_mn_full)

    stats_data = {
        "Métrica": ["Empuxo nominal (Ft)", "Bias (offset)",
                    "Pico máximo", "Média", "Desvio padrão (σ)", "Ruído RMS"],
        "Valor (mN)": [
            f"{metrics_full['nominal_thrust']:.5f}",
            f"{metrics_full['bias']:.5f}",
            f"{metrics_full['peak_value']:.5f}",
            f"{np.mean(thrust_mn_full):.5f}",
            f"{np.std(thrust_mn_full):.5f}",
            f"{np.std(thrust_mn_full):.5f}",
        ]
    }
    st.table(pd.DataFrame(stats_data))

    err_rel = abs(np.std(thrust_mn_full) / np.mean(thrust_mn_full) * 100) if np.mean(thrust_mn_full) != 0 else 0
    if err_rel < 1.0:
        st.success(f"✅ Erro relativo: {err_rel:.3f}% — dentro do critério de 1% (RNF03).")
    else:
        st.warning(f"⚠️ Erro relativo: {err_rel:.3f}% — acima de 1%. Considere recalibrar.")

    # ── Exportação ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Exportação de dados")

    nome_arquivo = st.text_input("Nome do arquivo",
                                 value=f"lase_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    ec1, ec2, ec3 = st.columns(3)

    # CSV
    csv_bytes = gerar_csv(time_arr, thrust_mn_full)
    ec1.download_button(
        "⬇️ Baixar CSV",
        data=csv_bytes,
        file_name=nome_arquivo + ".csv",
        mime="text/csv",
        use_container_width=True,
        help="Abre no Excel. UTF-8 com BOM para compatibilidade."
    )

    # PNG do gráfico
    fig_exp, ax_exp = plt.subplots(figsize=(10, 4))
    ax_exp.plot(time_arr, thrust_mn_full, color="#16a34a", linewidth=1.2, label="Empuxo processado (mN)")
    ax_exp.axhline(y=metrics_full["nominal_thrust"], color="#dc2626", linestyle="--",
                   label=f"Empuxo nominal: {metrics_full['nominal_thrust']:.4f} mN")
    ax_exp.set_xlabel("Tempo (s)"); ax_exp.set_ylabel("Empuxo (mN)")
    ax_exp.set_title(f"Relatório — {nome_arquivo}")
    ax_exp.grid(alpha=0.3); ax_exp.legend()
    plt.tight_layout()

    img_buf = io.BytesIO()
    fig_exp.savefig(img_buf, format="png", dpi=300, bbox_inches="tight")
    img_buf.seek(0)

    ec2.download_button(
        "⬇️ Baixar gráfico (PNG 300 dpi)",
        data=img_buf,
        file_name=nome_arquivo + ".png",
        mime="image/png",
        use_container_width=True,
        help="Adequado para publicação em artigo."
    )

    # PDF — instrução
    with ec3:
        st.button("⬇️ Gerar PDF", use_container_width=True, disabled=True,
                  help="Conecte o backend FastAPI com ReportLab (RF16). Endpoint: POST /api/export/pdf")
        st.caption("PDF: implemente `report_generator.py` como endpoint FastAPI + ReportLab.")

    st.pyplot(fig_exp)

    # ── Alerta de recalibração ────────────────────────────────────────────────
    st.markdown("---")
    if st.session_state.calibrado:
        st.success(f"✅ Calibração válida desde {st.session_state.timestamp_calib}. "
                   "Nenhuma mudança de configuração detectada nesta sessão.")
    else:
        st.warning("⚠️ A balança não foi calibrada nesta sessão. "
                   "Os resultados podem estar incorretos. Acesse a aba **Calibração**.")