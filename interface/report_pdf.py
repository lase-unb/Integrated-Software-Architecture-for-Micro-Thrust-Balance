# -*- coding: utf-8 -*-
"""
report_pdf.py
Gerador de relatório PDF para a Balança de Microempuxo — LaSE/UnB
Bilíngue PT/EN · ReportLab
"""

import io
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Image as RLImage


# ── Cores institucionais LaSE ─────────────────────────────────────────────
LASE_BLUE  = colors.HexColor("#1a3a6b")
LASE_GREEN = colors.HexColor("#2d7a3a")
LASE_GRAY  = colors.HexColor("#4a5568")
LASE_LIGHT = colors.HexColor("#f1f3f7")
LASE_BORDER= colors.HexColor("#e2e6ef")
BLACK      = colors.black
WHITE      = colors.white


# ── Caminhos ──────────────────────────────────────────────────────────────
_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(_DIR, "lase_logo.png")


# ═════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE GRÁFICO (retornam bytes PNG para embutir no PDF)
# ═════════════════════════════════════════════════════════════════════════

def _fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    buf.seek(0)
    plt.close(fig)
    return buf


def plot_empuxo_tempo(time_arr, thrust_mn, nominal_thrust, bias):
    """Gráfico principal: Empuxo vs Tempo."""
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.plot(time_arr, thrust_mn, color="#2563eb", linewidth=1.0,
            label="Thrust signal / Sinal de empuxo (mN)")
    ax.axhline(y=nominal_thrust, color="#16a34a", linestyle="--", linewidth=1.2,
               label=f"Nominal thrust / Empuxo nominal: {nominal_thrust:.4f} mN")
    ax.axhline(y=bias, color="#dc2626", linestyle=":", linewidth=1.0,
               label=f"Bias (zero offset): {bias:.4f} mN")
    ax.set_xlabel("Time / Tempo (s)", fontsize=10)
    ax.set_ylabel("Thrust / Empuxo (mN)", fontsize=10)
    ax.set_title("Thrust vs Time  ·  Empuxo vs Tempo", fontsize=11, fontweight="bold")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_xlim(time_arr[0], time_arr[-1])
    fig.tight_layout()
    return _fig_to_bytes(fig)


def plot_fft(xf, yr, yf, fnat):
    """Gráfico FFT com fnat marcada."""
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.plot(xf, yr, color="#cbd5e1", linewidth=0.8, label="Raw spectrum / Espectro bruto")
    ax.plot(xf, yf, color="#dc2626", linewidth=1.5, label="Filtered spectrum / Espectro filtrado")
    if fnat and fnat > 0:
        peak_idx = np.argmin(np.abs(xf - fnat))
        ax.plot(fnat, yf[peak_idx] if peak_idx < len(yf) else 0,
                "x", color="black", markersize=10, markeredgewidth=2,
                label=f"fnat = {fnat:.4f} Hz")
    ax.set_xlabel("Frequency / Frequência (Hz)", fontsize=10)
    ax.set_ylabel("Magnitude", fontsize=10)
    ax.set_title("FFT Analysis  ·  Análise de Frequência (Hanning window)", fontsize=11, fontweight="bold")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, linestyle="--")
    fig.tight_layout()
    return _fig_to_bytes(fig)


def plot_calibracao(theta, mteq, k, a_off, r2, err_theta=None):
    """Curva de calibração estática com regressão linear."""
    fig, ax = plt.subplots(figsize=(7, 3.8))
    if err_theta is not None:
        ax.errorbar(theta, mteq, xerr=err_theta, fmt="o", color="#2563eb",
                    markersize=5, label="Experimental data / Dados experimentais",
                    capsize=3, elinewidth=0.8)
    else:
        ax.scatter(theta, mteq, color="#2563eb", s=30,
                   label="Experimental data / Dados experimentais")
    x_fit = np.linspace(theta.min(), theta.max(), 100)
    ax.plot(x_fit, a_off + k * x_fit, "--", color="#16a34a", linewidth=1.5,
            label=f"Linear fit: k = {k:.5f} N·m/rad")
    ax.set_xlabel("Angular displacement θ / Deslocamento angular θ (rad)", fontsize=9)
    ax.set_ylabel("Torque (N·m)", fontsize=9)
    ax.set_title(f"Static Calibration  ·  Calibração Estática  (R² = {r2:.4f})",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, linestyle="--")
    fig.tight_layout()
    return _fig_to_bytes(fig)


# ═════════════════════════════════════════════════════════════════════════
# ESTILOS
# ═════════════════════════════════════════════════════════════════════════

def _estilos():
    base = getSampleStyleSheet()
    estilos = {}

    estilos["titulo"] = ParagraphStyle(
        "titulo", parent=base["Normal"],
        fontSize=16, fontName="Helvetica-Bold",
        textColor=LASE_BLUE, alignment=TA_LEFT,
        spaceAfter=2
    )
    estilos["subtitulo"] = ParagraphStyle(
        "subtitulo", parent=base["Normal"],
        fontSize=10, fontName="Helvetica",
        textColor=LASE_GRAY, alignment=TA_LEFT,
        spaceAfter=6
    )
    estilos["secao"] = ParagraphStyle(
        "secao", parent=base["Normal"],
        fontSize=11, fontName="Helvetica-Bold",
        textColor=LASE_BLUE, spaceBefore=14, spaceAfter=6,
        borderPad=3
    )
    estilos["corpo"] = ParagraphStyle(
        "corpo", parent=base["Normal"],
        fontSize=9, fontName="Helvetica",
        textColor=LASE_GRAY, leading=14,
        spaceAfter=4
    )
    estilos["caption"] = ParagraphStyle(
        "caption", parent=base["Normal"],
        fontSize=8, fontName="Helvetica-Oblique",
        textColor=LASE_GRAY, alignment=TA_CENTER,
        spaceAfter=8, spaceBefore=2
    )
    estilos["rodape"] = ParagraphStyle(
        "rodape", parent=base["Normal"],
        fontSize=7.5, fontName="Helvetica",
        textColor=colors.HexColor("#9aa3b5"),
        alignment=TA_CENTER
    )
    return estilos


# ═════════════════════════════════════════════════════════════════════════
# COMPONENTES DO DOCUMENTO
# ═════════════════════════════════════════════════════════════════════════

def _cabecalho(estilos, timestamp, nome_sessao):
    """Cabeçalho com logo LaSE + título."""
    elementos = []

    # Logo + título lado a lado via tabela
    logo_cell = ""
    if os.path.exists(LOGO_PATH):
        logo_cell = RLImage(LOGO_PATH, width=4.5*cm, height=1.2*cm)

    titulo_cell = [
        Paragraph("Microthrust Balance — Test Report", estilos["titulo"]),
        Paragraph("Relatório de Ensaio — Balança de Microempuxo", estilos["subtitulo"]),
        Paragraph(
            f"<font color='#9aa3b5'>Session / Sessão: {nome_sessao} &nbsp;·&nbsp; "
            f"Generated / Gerado: {timestamp}</font>",
            estilos["corpo"]
        ),
    ]

    header_table = Table(
        [[logo_cell, titulo_cell]],
        colWidths=[5*cm, 12.5*cm]
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
    ]))

    elementos.append(header_table)
    elementos.append(Spacer(1, 0.3*cm))
    elementos.append(HRFlowable(width="100%", thickness=2, color=LASE_BLUE, spaceAfter=8))
    return elementos


def _tabela_estilo_base():
    return TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  LASE_BLUE),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0),  9),
        ("ALIGN",        (0, 0), (-1, 0),  "CENTER"),
        ("BACKGROUND",   (0, 1), (-1, -1), LASE_LIGHT),
        ("ROWBACKGROUNDS",(0,1), (-1,-1),  [WHITE, LASE_LIGHT]),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 8.5),
        ("ALIGN",        (1, 1), (-1, -1), "RIGHT"),
        ("ALIGN",        (0, 1), (0, -1),  "LEFT"),
        ("GRID",         (0, 0), (-1, -1), 0.4, LASE_BORDER),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ])


def _secao_metadados(estilos, params_calib, modo_teste, n_amostras, fs, duracao):
    """Seção 1 — Metadados do ensaio."""
    elementos = []
    elementos.append(Paragraph("1. Test Configuration  ·  Configuração do Ensaio", estilos["secao"]))

    dados = [
        ["Parameter / Parâmetro", "Value / Valor", "Unit / Unidade"],
        ["Torsional stiffness / Rigidez torcional (k)",
         f"{params_calib.get('k_torque', '—'):.5f}", "N·m/rad"],
        ["LVDT arm / Braço LVDT (L_LVDT)",
         f"{params_calib.get('l_lvdt', '—'):.3f}", "m"],
        ["Thrust arm / Braço motor (L_thrust)",
         f"{params_calib.get('l_thrust', '—'):.3f}", "m"],
        ["Natural frequency / Freq. natural (fnat)",
         f"{params_calib.get('fn', '—'):.4f}" if params_calib.get('fn') else "—", "Hz"],
        ["Sensitivity / Sensibilidade (S)",
         f"{params_calib.get('S', '—'):.2f}" if params_calib.get('S') else "—", "µm/N"],
        ["Test mode / Modo de teste",
         "Pulsed / Pulsado" if modo_teste == "pulsado" else "Continuous / Contínuo", "—"],
        ["Samples / Amostras (N)", f"{n_amostras:,}", "pts"],
        ["Sampling rate / Taxa de amostragem (fs)", f"{fs:.1f}", "Hz"],
        ["Duration / Duração", f"{duracao:.1f}", "s"],
    ]

    t = Table(dados, colWidths=[8*cm, 5.5*cm, 4*cm])
    t.setStyle(_tabela_estilo_base())
    elementos.append(t)
    return elementos


def _secao_resultados(estilos, metrics, xmax=None, std_thrust=None, err_rel=None):
    """Seção 2 — Resultados principais."""
    elementos = []
    elementos.append(Paragraph("2. Main Results  ·  Resultados Principais", estilos["secao"]))

    Ft   = metrics.get("nominal_thrust", 0)
    bias = metrics.get("bias", 0)
    peak = metrics.get("peak_value", 0)
    std  = std_thrust if std_thrust is not None else 0
    err  = err_rel if err_rel is not None else 0

    dados = [
        ["Result / Resultado", "Value / Valor", "Unit / Unidade", "Criterion / Critério"],
        ["Nominal thrust / Empuxo nominal (Ft)",
         f"{Ft:.5f}", "mN", "—"],
        ["Zero bias / Bias de zero",
         f"{bias:.5f}", "mN", "< 0.01 mN"],
        ["Peak value / Valor de pico",
         f"{peak:.5f}", "mN", "—"],
        ["Std deviation / Desvio padrão (σ)",
         f"{std:.5f}", "mN", "—"],
        ["Relative error / Erro relativo",
         f"{err:.3f}", "%", "< 1.0% (RNF03)"],
    ]
    if xmax is not None:
        dados.insert(2, ["Max deflection / Deflexão máxima (xmax)",
                         f"{xmax:.4f}", "µm", "res. 0.01 µm (RF08)"])

    t = Table(dados, colWidths=[7*cm, 3.5*cm, 2.5*cm, 4.5*cm])
    t.setStyle(_tabela_estilo_base())

    # Destaca linha de erro relativo
    n = len(dados) - 1
    if err > 1.0:
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, n), (-1, n), colors.HexColor("#fef2f2")),
            ("TEXTCOLOR",  (1, n), (1,  n), colors.HexColor("#dc2626")),
            ("FONTNAME",   (1, n), (1,  n), "Helvetica-Bold"),
        ]))
    else:
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, n), (-1, n), colors.HexColor("#f0fdf4")),
            ("TEXTCOLOR",  (1, n), (1,  n), colors.HexColor("#16a34a")),
            ("FONTNAME",   (1, n), (1,  n), "Helvetica-Bold"),
        ]))

    elementos.append(t)

    # Nota de validação
    if err <= 1.0:
        nota = ("✓  Calibration error within specification (< 1%, RNF03 / INMETRO–EURAMET).  "
                "Erro de calibração dentro do especificado.")
        elementos.append(Spacer(1, 0.2*cm))
        elementos.append(Paragraph(f'<font color="#16a34a">{nota}</font>', estilos["corpo"]))
    else:
        nota = ("⚠  Calibration error exceeds 1% — recalibration recommended.  "
                "Erro acima de 1% — recalibração recomendada.")
        elementos.append(Spacer(1, 0.2*cm))
        elementos.append(Paragraph(f'<font color="#dc2626">{nota}</font>', estilos["corpo"]))

    return elementos


def _secao_estatisticas(estilos, thrust_mn):
    """Seção 3 — Estatísticas detalhadas."""
    elementos = []
    elementos.append(Paragraph("3. Statistical Analysis  ·  Análise Estatística", estilos["secao"]))

    dados = [
        ["Statistic / Estatística", "Value (mN) / Valor (mN)"],
        ["Mean / Média aritmética",        f"{np.mean(thrust_mn):.6f}"],
        ["Std deviation / Desvio padrão",  f"{np.std(thrust_mn):.6f}"],
        ["Variance / Variância",           f"{np.var(thrust_mn):.8f}"],
        ["Minimum / Mínimo",               f"{np.min(thrust_mn):.6f}"],
        ["Maximum / Máximo",               f"{np.max(thrust_mn):.6f}"],
        ["Peak-to-peak / Pico a pico",     f"{np.ptp(thrust_mn):.6f}"],
        ["RMS noise / Ruído RMS",          f"{np.std(thrust_mn):.6f}"],
    ]

    t = Table(dados, colWidths=[9*cm, 8.5*cm])
    t.setStyle(_tabela_estilo_base())
    elementos.append(t)
    return elementos


def _secao_graficos(estilos, buf_empuxo, buf_fft, buf_calib):
    """Seção 4 — Gráficos."""
    elementos = []
    elementos.append(Paragraph("4. Graphs  ·  Gráficos", estilos["secao"]))
    largura = 17.5*cm

    # Empuxo vs tempo
    elementos.append(KeepTogether([
        RLImage(buf_empuxo, width=largura, height=largura*0.38),
        Paragraph(
            "Figure 1 / Figura 1 — Thrust signal over time with nominal thrust and bias lines.  "
            "Sinal de empuxo ao longo do tempo com linhas de empuxo nominal e bias.",
            estilos["caption"]
        ),
    ]))

    # FFT
    if buf_fft is not None:
        elementos.append(KeepTogether([
            RLImage(buf_fft, width=largura, height=largura*0.35),
            Paragraph(
                "Figure 2 / Figura 2 — FFT spectrum showing natural frequency (fnat) peak.  "
                "Espectro FFT com o pico de frequência natural (fnat) identificado.",
                estilos["caption"]
            ),
        ]))

    # Calibração estática
    if buf_calib is not None:
        elementos.append(KeepTogether([
            RLImage(buf_calib, width=largura*0.7, height=largura*0.38),
            Paragraph(
                "Figure 3 / Figura 3 — Static calibration curve (torque vs angle) with linear regression.  "
                "Curva de calibração estática (torque vs ângulo) com regressão linear.",
                estilos["caption"]
            ),
        ]))

    return elementos


def _rodape(canvas, doc):
    """Rodapé em todas as páginas."""
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#9aa3b5"))
    largura, _ = A4
    canvas.drawString(
        2*cm, 1.2*cm,
        "LaSE — Laboratório de Sistemas Espaciais · Universidade de Brasília"
    )
    canvas.drawRightString(
        largura - 2*cm, 1.2*cm,
        f"Page / Página {doc.page}"
    )
    canvas.setStrokeColor(colors.HexColor("#e2e6ef"))
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 1.5*cm, largura - 2*cm, 1.5*cm)
    canvas.restoreState()


# ═════════════════════════════════════════════════════════════════════════
# FUNÇÃO PRINCIPAL — gera e retorna bytes do PDF
# ═════════════════════════════════════════════════════════════════════════

def gerar_pdf(
    time_arr,
    thrust_mn,
    metrics,
    params_calib,
    modo_teste="pulsado",
    nome_sessao=None,
    fnat=None,
    xf=None,
    yr=None,
    yf=None,
    xmax=None,
    theta_calib=None,
    mteq_calib=None,
    k_calib=None,
    a_off_calib=None,
    r2_calib=None,
    err_theta_calib=None,
):
from report_pdf import gerar_pdf

# Substitui o st.button de PDF por:
if st.button("⬇️ Gerar PDF", use_container_width=True):
    with st.spinner("Gerando relatório PDF..."):
        pdf_bytes = gerar_pdf(
            time_arr      = time_arr,
            thrust_mn     = thrust_mn_full,
            metrics       = metrics_full,
            params_calib  = {
                "k_torque": st.session_state.k_torque,
                "l_lvdt":   st.session_state.l_lvdt,
                "l_thrust": st.session_state.l_thrust,
                "fn":       st.session_state.fn_calculada,
                "S":        st.session_state.S_calculada,
            },
            modo_teste    = st.session_state.modo_teste,
            nome_sessao   = nome_arquivo,
            fnat          = st.session_state.fn_calculada,
            xf            = xf if 'xf' in dir() else None,
            yr            = yr if 'yr' in dir() else None,
            yf            = yf if 'yf' in dir() else None,
        )
    st.download_button(
        "📄 Baixar PDF",
        data      = pdf_bytes,
        file_name = nome_arquivo + ".pdf",
        mime      = "application/pdf",
        use_container_width=True,
    )

    if nome_sessao is None:
        nome_sessao = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    fs = (len(time_arr) - 1) / (time_arr[-1] - time_arr[0]) if len(time_arr) > 1 else 50.0
    duracao = float(time_arr[-1] - time_arr[0])
    std_thrust = float(np.std(thrust_mn))
    mean_t = float(np.mean(thrust_mn))
    err_rel = abs(std_thrust / mean_t * 100) if mean_t != 0 else 0.0

    estilos = _estilos()

    # ── Gera os gráficos ──────────────────────────────────────────────────
    buf_empuxo = plot_empuxo_tempo(
        time_arr, thrust_mn,
        metrics.get("nominal_thrust", 0),
        metrics.get("bias", 0)
    )

    buf_fft = None
    if xf is not None and yr is not None and yf is not None:
        buf_fft = plot_fft(xf, yr, yf, fnat)

    buf_calib = None
    if theta_calib is not None and mteq_calib is not None and k_calib is not None:
        buf_calib = plot_calibracao(
            theta_calib, mteq_calib, k_calib,
            a_off_calib or 0.0, r2_calib or 0.0, err_theta_calib
        )

    # ── Monta o documento ─────────────────────────────────────────────────
    buf_pdf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf_pdf,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm,  bottomMargin=2.5*cm,
        title=f"LaSE Microthrust Report — {nome_sessao}",
        author="LaSE / UnB",
        subject="Microthrust Balance Test Report",
    )

    story = []

    # Cabeçalho
    story += _cabecalho(estilos, timestamp, nome_sessao)
    story.append(Spacer(1, 0.4*cm))

    # Seção 1 — Configuração
    story += _secao_metadados(
        estilos, params_calib, modo_teste,
        len(time_arr), fs, duracao
    )
    story.append(Spacer(1, 0.3*cm))

    # Seção 2 — Resultados
    story += _secao_resultados(estilos, metrics, xmax, std_thrust, err_rel)
    story.append(Spacer(1, 0.3*cm))

    # Seção 3 — Estatísticas
    story += _secao_estatisticas(estilos, thrust_mn)
    story.append(Spacer(1, 0.3*cm))

    # Seção 4 — Gráficos
    story += _secao_graficos(estilos, buf_empuxo, buf_fft, buf_calib)

    # Rodapé institucional final
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=LASE_BORDER, spaceAfter=6))
    story.append(Paragraph(
        "This report was automatically generated by the LaSE Microthrust Balance Control System.  "
        "Este relatório foi gerado automaticamente pelo Sistema de Controle da Balança de Microempuxo do LaSE.",
        estilos["rodape"]
    ))

    doc.build(story, onFirstPage=_rodape, onLaterPages=_rodape)
    buf_pdf.seek(0)
    return buf_pdf.read()