# Integrated Software Architecture for Micro-Thrust Balance

> Pipeline digital de quatro camadas para automação metrológica e tratamento de ruídos em bancadas de microempuxo — LaSE/UnB × AEB

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
│   ├── find_deflection.py           # Análise de deflexão + incerteza GUM
│   ├── k_calculation.py             # Constante de rigidez torcional k
│   └── pendulum-dynamic.py          # Modelo dinâmico do pêndulo
│
├── signal_processing/               # Camadas 1 e 2 — FFT + DSP
│   ├── fn_calculation.py            # Análise espectral FFT + detecção de fn
│   ├── processing.py                # Filtro Butterworth 5ª ordem + conversão µm→mN
│   └── simulator.py                 # Gêmeo Digital do sistema dinâmico
│
├── interface/                       # Camada 4 — interface e relatórios
│   ├── main.py                      # Aplicação Streamlit (entry point)
│   ├── live_plot.py                 # Telemetria em tempo real (50 ms)
│   ├── report_pdf.py                # Gerador de relatório PDF bilíngue PT/EN
│   └── web/                         # Interface web alternativa (HTML/CSS)
│       ├── index.html               # Dashboard
│       ├── calibracao.html          # Página de calibração
│       ├── analise.html             # Análise e exportação
│       └── style.css
│
├── hardware/                        # Aquisição de dados
│   └── data_acquisition.py          # Interface serial USB com LVDT
│
├── tools/                           # Scripts auxiliares
│   └── LVDT_Plot_V2.py              # Identificação de deslocamento máximo
│
├── docs/                            # Documentação técnica
│   └── balanca.md                   # Especificações da balança
│
├── data/                            # Dados experimentais (ver .gitignore)
│   └── Calibration Data/            # Dados de calibração
│
├── main.py                          # Entry point principal (streamlit run main.py)
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
streamlit run main.py
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
| 4 — Interface | `interface/main.py` | Streamlit: calibração, aquisição, análise |
| 4 — Telemetria | `interface/live_plot.py` | Monitoramento tempo real (50 ms) |
| 4 — Relatório | `interface/report_pdf.py` | PDF institucional bilíngue PT/EN |

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