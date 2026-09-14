# Integrated Software Architecture for Micro-Thrust Balance

> Pipeline digital de quatro camadas para automação metrológica e tratamento de ruídos em bancadas de microempuxo 

[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Interface-Streamlit-red)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-TBD-gray)]()

---

## Visão Geral

Este repositório contém a arquitetura de software desenvolvida no **Laboratório de Sistemas Espaciais (LaSE)** da Universidade de Brasília (UnB), em parceria com a **Agência Espacial Brasileira (AEB)**, para caracterização precisa de sistemas de micropropulsão.

A arquitetura é estruturada em um **pipeline digital de quatro camadas** implementado em Python, integrando análise espectral (FFT), filtragem Butterworth de quinta ordem com fase zero, Filtro de Kalman sintonizado em Gêmeo Digital, gerenciamento metrológico de dados e interface Streamlit para telemetria e geração automatizada de relatórios PDF institucionais.

---

## Estrutura do Repositório

```
Integrated-Software-Architecture-for-Micro-Thrust-Balance/
│
├── Análises/                        # Análises experimentais anteriores (LaSE)
│   ├── data/                        # Dados brutos dos experimentos
│   ├── resultados/                  # Resultados processados
│   └── src/
│       ├── Hector/                  # Scripts de análise (H. Gessini)
│       └── ...                      # Scripts de análise física
│
├── calibration/                     # Camada 3 — calibração e gerenciamento
│   ├── physics/                     # Modelos físicos da balança
│   │   ├── centro_gravidade.m       # Cálculo do centro de gravidade
│   │   ├── carga_constante.m        # Análise de carga constante
│   │   ├── carga_constante_derivaTermica.m
│   │   ├── efeitojoule.py           # Modelagem efeito Joule
│   │   ├── efeitojoule_2.py
│   │   ├── eletroima_forca.py       # Força eletromagnética
│   │   ├── forca_eletroima.m
│   │   ├── graph_calibracao.m
│   │   ├── movimento_nucleo.py      # Dinâmica do núcleo
│   │   ├── plot_carga_cte.m
│   │   ├── relatorio_calibracao.py
│   │   ├── restricao_geo_forca.py
│   │   ├── superficie_calibracao.m
│   │   ├── 2_modo_vibracao.py       # Análise de modos de vibração
│   │   └── calibracao.py
│   ├── find_deflection.py           # Análise de deflexão + incerteza GUM (importado por interface/main.py)
│   ├── k_calculation.py             # Constante de rigidez efetiva k (importado por interface/main.py)
│   ├── dce_calibration.py           # Calibração in situ via DCE (simulada, sem hardware validado)
│   └── pendulum-dynamic.py          # Modelo dinâmico do pêndulo
│
├── signal_processing/               # Camadas 1 e 2 — FFT + DSP
│   ├── fn_calculation.py            # Análise espectral FFT + detecção de fn (importado por interface/main.py)
│   ├── processing.py                # Filtro Butterworth 5ª ordem + Kalman + conversão µm→mN
│   └── simulator.py                 # Gêmeo Digital do sistema dinâmico
│
├── interface/                       # Camada 4 — interface e relatórios
│   ├── main.py                      # Aplicação Streamlit (entry point — abas de calibração, aquisição e análise/exportação)
│   ├── live_plot.py                 # Telemetria em tempo real (50 ms)
│   ├── report_pdf.py                # Gerador de relatório PDF bilíngue PT/EN
│   └── web/                         # Interface web alternativa (HTML/CSS)
│       ├── index.html               # Dashboard
│       ├── calibracao.html          # Página de calibração
│       ├── analise.html             # Análise e exportação
│       └── style.css
│
├── hardware/                        # Aquisição de dados
│   ├── data_acquisition.py          # Interface serial USB com LVDT
│   └── dce_power_supply.py          # Driver SCPI/USB da fonte do DCE (real + simulado)
│
├── tools/                           # Scripts auxiliares
│   └── LVDT_Plot_V2.py              # Identificação de deslocamento máximo (importado por interface/main.py)
│
├── docs/                            # Documentação técnica
│   └── balanca.md                   # Especificações da balança
│
├── requirements.txt                 # Dependências Python
├── .gitignore
└── README.md
```

---

## Instalação

### Pré-requisitos

- Python 3.9+
- pip

### Passos

```bash
# Clone o repositório
git clone https://github.com/lase-unb/Integrated-Software-Architecture-for-Micro-Thrust-Balance.git
cd Integrated-Software-Architecture-for-Micro-Thrust-Balance

# Instale as dependências
pip install -r requirements.txt

# Execute a interface principal
streamlit run interface/main.py
```

---

## Pipeline de Quatro Camadas

| Camada | Módulo | Função |
|--------|--------|--------|
| 1 — Análise Espectral | `signal_processing/fn_calculation.py` | FFT + janela Hanning → identificação de fn |
| 2 — DSP | `signal_processing/processing.py` | Butterworth 5ª ordem + filtfilt + Kalman |
| 2 — Gêmeo Digital | `signal_processing/simulator.py` | Modelo dinâmico para sintonização do Kalman |
| 3 — Calibração | `calibration/k_calculation.py` | Constante k, ajuste linear, R² |
| 3 — Metrologia | `calibration/find_deflection.py` | Deflexão + incerteza σ_d (GUM) |
| 3 — Pico de deflexão | `tools/LVDT_Plot_V2.py` | Identificação de xmax (regime pulsado) |
| 4 — Interface | `interface/main.py` | Streamlit: calibração, aquisição, análise (3 abas) |
| 4 — Telemetria | `interface/live_plot.py` | Monitoramento tempo real (50 ms) |
| 4 — Relatório | `interface/report_pdf.py` | PDF institucional bilíngue PT/EN, via ReportLab |

Os módulos das Camadas 1–3 (`fn_calculation.py`, `find_deflection.py`, `k_calculation.py`, `LVDT_Plot_V2.py`) funcionam tanto de forma independente (`python <script>.py`, para análise offline de um arquivo) quanto importados diretamente por `interface/main.py` — não há lógica duplicada entre o app e os scripts standalone.

---

## Guia de Módulos

Descrição do que cada arquivo da arquitetura faz e como ele se encaixa no pipeline. Não cobre `Análises/` (scripts históricos de experimentos anteriores do LaSE, fora da arquitetura de software mantida).

### `calibration/`

- **`find_deflection.py`** — calcula a deflexão (Δd) entre uma janela de baseline e uma janela de patamar, com incerteza combinada σ_c = √(σ₁²+σ₂²) (GUM). Expõe `calcular_deflexao()`, importada por `interface/main.py`; também roda sozinho (`python find_deflection.py arquivo.txt`) para análise offline com gráfico.
- **`k_calculation.py`** — determina a rigidez efetiva k por regressão linear T(θ)=k·θ+a (mínimos quadrados) a partir de um CSV de massas/deslocamento/erro, com R² para validar o ajuste. Expõe `calibracao_estatica()`, importada por `interface/main.py`.
- **`dce_calibration.py`** — calibração in situ via DCE (Dispositivo de Calibração Eletrostática): varre voltagens conhecidas, lê a deflexão resultante (`calibrar_via_dce()`) e ajusta a rigidez efetiva por regressão, com a força convertida pela lei quadrática de placas paralelas (`forca_dce()`). Interlock de 1000V embutido. **Validado apenas em simulação** (`python dce_calibration.py`, usando `FontePowerSupplySimulada`) — ainda não testado com a fonte/DCE/LVDT reais nem conectado à interface Streamlit.
- **`pendulum-dynamic.py`** — só cabeçalho/comentários por enquanto; reservado para as equações diferenciais da dinâmica do pêndulo (simples e 2º modo de vibração). Ainda não implementado.
- **`physics/`** — scripts MATLAB/Python de modelagem física (efeito Joule, força eletromagnética, geometria do núcleo etc.) usados nos estudos de dimensionamento da balança. Não são importados pelo app; ficam como referência de cálculo.

### `signal_processing/`

- **`processing.py`** — núcleo de DSP do projeto. `apply_kalman_filter()` implementa o Filtro de Kalman linear (2 estados: posição e velocidade) sintonizado pela frequência natural; `apply_lowpass_filter()` aplica Butterworth 5ª ordem fase-zero (`filtfilt`) seguido do Kalman; `convert_to_mn()` converte deslocamento (µm) em empuxo (mN); `calculate_metrics()` extrai bias, empuxo nominal e ruído RMS. É importado por praticamente todos os outros módulos (main.py, live_plot.py, fn_calculation.py, LVDT_Plot_V2.py).
- **`fn_calculation.py`** — identifica a frequência natural (fnat) via FFT (rfft) do sinal filtrado, buscando o pico de maior magnitude. Expõe `calcular_fnat()`, importada por `interface/main.py`; também roda sozinho.
- **`simulator.py`** — script standalone que gera dados sintéticos de pêndulo amortecido (ruído + oscilação + degrau de empuxo) e escreve continuamente em `data.txt`, respeitando o tempo real (`time.sleep`) — serve para testar `live_plot.py` sem hardware conectado. Não é importado por `main.py` (que tem seu próprio gerador de simulação embutido, em lote).

### `interface/`

- **`main.py`** — aplicação Streamlit, ponto de entrada (`streamlit run interface/main.py`). Três abas: Calibração (parâmetros físicos da balança, constante k, configuração do DCE), Aquisição de dados (upload de arquivo ou simulação), Análise e exportação (modo pulsado/contínuo, métricas, exportação CSV/PNG/PDF).
- **`report_pdf.py`** — gera o relatório PDF institucional bilíngue PT/EN via ReportLab (metadados do ensaio, resultados, estatísticas e gráficos). Função principal `gerar_pdf()`, chamada pelo botão "Gerar PDF" da aba 3.
- **`live_plot.py`** — visualizador de telemetria em tempo real standalone (desktop, matplotlib `FuncAnimation`, 50 ms), lê um arquivo de dados fixo via polling. É uma ferramenta separada do app Streamlit, não integrada ao `main.py`.
- **`web/`** — protótipo estático de interface alternativa em HTML/CSS/Chart.js (`index.html`, `calibracao.html`, `analise.html`). Sem integração com nenhum backend — é um mockup visual, não uma interface funcional.

### `hardware/`

- **`data_acquisition.py`** — lê a porta serial USB do condicionador do LVDT (baud rate 9600) e grava as amostras em `data.txt`, no formato que os demais módulos esperam (tempo e deslocamento separados por TAB, decimal em vírgula).
- **`dce_power_supply.py`** — driver SCPI/USB da fonte programável do DCE (`RigolDP932U`, via PyVISA — não testado com hardware real) e um substituto sem hardware com a mesma interface (`FontePowerSupplySimulada`), usado por `calibration/dce_calibration.py`.

### `tools/`

- **`LVDT_Plot_V2.py`** — identifica o xmax (maior deflexão absoluta) em um sinal já filtrado, usado na análise do regime pulsado. Expõe `detectar_xmax()`, importada por `interface/main.py`.

---

## Publicação

**Arquitetura de Software Integrada para Automação Metrológica e Tratamento de Ruídos em Bancadas de Microempuxo**

Sessão 2 — Sustentabilidade, Educação, Ciência e Tecnologia | Formato: Presencial

**Autores:**
- Luana Carvalho de Almeida — 242004840@aluno.unb.br (UnB)
- Thamiris Thomazini Libard — 200043820@aluno.unb.br (UnB)
- Lui Txai Calvoso Habl — lui.habl@unb.br (UnB)
- Paolo Gessini — paolo.gessini@aeb.gov.br (AEB)

**Palavras-chave:** micropropulsão · arquitetura de software modular · processamento digital de sinais · calibração eletrostática in situ · Gêmeo Digital

---

## Licença

A definir.
