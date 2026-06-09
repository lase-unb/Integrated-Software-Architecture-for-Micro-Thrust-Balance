<div align="center">

<br/>

**Micro-Thrust Balance — Signal Processing & Autonomous Calibration Pipeline**

*LaSE · Laboratory of Space Systems*

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-f59e0b?style=flat-square)]()
[![Offline](https://img.shields.io/badge/Operation-Fully%20Offline-6366f1?style=flat-square)]()
[![Docs](https://img.shields.io/badge/Docs-Requirements%20Spec-0ea5e9?style=flat-square)](docs/)

<br/>

> A full signal processing, autonomous calibration, and data acquisition pipeline  
> for the micro-thrust balance used in small satellite propulsion testing at LaSE.

<br/>

---

</div>

## Overview

This repository contains the software infrastructure for operating the **LaSE Micro-Thrust Balance**, a precision torsional pendulum instrument used to characterize pulsed and continuous thrust from small satellite propulsion systems (PPTs and similar).

The pipeline covers three main layers:

- **Signal Filtering** — real-time noise filtering on LVDT sensor data
- **Autonomous Calibration** — automated static and dynamic calibration sequences (DCE-driven)
- **Interface** — web-based GUI for lab operators, designed for non-specialist use in isolated environments

All modules operate **100% offline** — no internet dependency at runtime — targeting deployment in vacuum chamber environments.

<br/>

---

## Repository Structure

```
microthrustpy/
│
├── filters/                   # Signal processing & noise filtering
│   ├── butterworth.py         #   Butterworth filter (order 5, cutoff 0.05·fnat)
│   ├── fft_analysis.py        #   FFT with Hanning window, 0.01 Hz resolution
│   └── steady_state.py        #   Steady-state detection (<0.1% variation threshold)
│
├── calibration/               # Autonomous calibration pipeline
│   ├── static_cal.py          #   Static calibration sequence
│   ├── dynamic_cal.py         #   Dynamic calibration (J, k, ω₀, S via FFT)
│   ├── dce_controller.py      #   DCE voltage control (<5 ms latency, ≤1000 V limit)
│   └── cg_calculator.py       #   Center-of-gravity computation from counterweight data
│
├── acquisition/               # Data acquisition
│   └── lvdt_reader.py         #   Real-time LVDT capture at 100 Hz (zero-packet-loss)
│
├── analysis/                  # Post-acquisition analysis
│   ├── pulsed_mode.py         #   xmax extraction from transient (first peak-valley)
│   ├── continuous_mode.py     #   Steady-state mean: xss/FE → sensitivity S
│   └── regression.py         #   Linear / least-squares curve fitting (R² > 0.99)
│
├── interface/                 # Web GUI (offline)
│   ├── app.py                 #   Main application entry point
│   ├── pages/                 #   Calibration, Acquisition, Analysis views
│   └── components/            #   Reusable UI components
│
├── reports/                   # Export engine
│   └── exporter.py            #   CSV (UTF-8) and PDF (ReportLab) generation
│
├── docs/                      # Documentation
│   └── requirements_spec.pdf  #   Full software requirements specification
│
├── tests/                     # Unit and integration tests
└── README.md
```

<br/>

---

## Key Features

### Signal Filtering
- Real-time noise reduction on LVDT displacement signals
- Butterworth low-pass filter (order 5, cutoff = `0.05 × fnat`)
- FFT analysis with Hanning window at 0.01 Hz resolution
- Automatic steady-state detection (variation threshold < 0.1%)
- Dashboard updates every **10 ms**; FFT processing < **1 s** for 1-minute signals

### Autonomous Calibration
- Full static + dynamic calibration sequences in < 30 min
- Computes: moment of inertia **J**, torsional stiffness **k**, natural frequency **ω₀**, and sensitivity **S**
- DCE voltage auto-calculation from target force input (precision: 0.1 V)
- Center-of-gravity computation from counterweight mass and position inputs
- Hard voltage limit: **≤ 1000 V** with software interlock, visual/audio alert, and incident logging
- Post-calibration recommendations based on threshold rules (e.g., hysteresis > 2%)

### Acquisition & Analysis
| Mode | Focus | Key Metric |
|------|-------|------------|
| **Pulsed (DCE)** | Transient regime | `xmax` — first peak-valley, resolution 0.01 μm |
| **Continuous (DCE)** | Steady-state regime | `xss` — mean after τ × 4 settling, σ < 0.01 μm |

- Supports N ≥ 10 repeated pulses with mean and standard deviation
- `xss / FE` → sensitivity S (μm/N or V/N), error < 1% vs. analytical
- FE lookup table from experimental curves; DE interpolation error ≤ 2%

### Interface
- Offline web application (no internet dependency)
- Pulsed / Continuous mode toggle with automatic parameter switching
- Real-time interactive plots (time domain + FFT) with zoom and pan
- Drag-and-drop layout, contextual tooltips, responsive in < 50 ms
- Automatic recalibration alert when mass or CG changes > 1%

### Reporting
- Export to **PDF** (ReportLab) and **CSV** (UTF-8)
- Includes: time/FFT graphs, calibration curves, parameter tables, uncertainty estimates, timestamps
- Download time < 10 s for 1 hour of data

<br/>

---

## Requirements

| Requirement | Value |
|---|---|
| Python | ≥ 3.10 |
| Network | Not required (fully offline) |
| Calibration error | < 1% (INMETRO/EURAMET standards) |
| Measurement repeatability | < 0.05 Ns |
| DCE control latency | < 5 ms |
| Dashboard refresh | 10 ms |
| Max DCE voltage | 1000 V (hard limit) |
| MTBF | ≥ 99.9% over 8 h operation |

<br/>

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/your-org/microthrustpy.git
cd microthrustpy

# Install dependencies
pip install -r requirements.txt

# Run the interface
python interface/app.py
```

> **Note:** The system is designed for isolated lab environments. No external network calls are made at any point during operation.

<br/>

---

## Requirements Specification

The full software requirements document is available at [`docs/requirements_spec.pdf`](docs/requirements_spec.pdf).

A summary of the requirement matrix:

| ID | Title | Priority | Status |
|----|-------|----------|--------|
| RNF01 | Offline Operation | Must Have | Proposed |
| RF01 | Full Calibration, Acquisition & Analysis Coverage | Must Have | Proposed |
| RF02 | Statistics for Pulsed and Continuous Loads | Must Have | Proposed |
| RF03 | Counterweight & Distance Input for Calibration | Must Have | Proposed |
| RF05 | DCE Force Magnitude Input | Must Have | Proposed |
| RF06 | Automatic DCE Voltage Calculation | Must Have | Proposed |
| RF07 | Steady-State Acquisition (Continuous DCE) | Must Have | Proposed |
| RF08 | Peak Amplitude Analysis (Pulsed DCE) | Must Have | Proposed |
| RF09 | Known-Input Consideration (Continuous DCE) | Must Have | Proposed |
| RF10 | Real-Time Curve Generation | Must Have | Proposed |
| RF13 | Real-Time LVDT Acquisition | Must Have | Proposed |
| RF14 | DCE Voltage Safety Limit (≤ 1000 V) | Must Have | Proposed |
| RF15 | Automated Static/Dynamic Calibration Sequences | Must Have | Proposed |
| RNF02 | Real-Time Performance | Must Have | Proposed |
| RI01 | Time Domain + FFT Visualization | Should Have | Proposed |
| RF16 | CSV/PDF Report Export | Should Have | Proposed |
| RNF03 | Measurement Precision & Reliability | Should Have | Proposed |
| RI02 | Pulsed / Continuous Mode Selection | Must Have | Proposed |
| RF04 | Post-Calibration Recommendations | Could Have | Proposed |
| RF11 | Automatic Center-of-Gravity Calculation | Could Have | Proposed |
| RF12 | Recalibration Reminder on Mass/CG Change | Could Have | Proposed |

<br/>

---

## Instrument Context

The **LaSE Micro-Thrust Balance** is a torsional pendulum designed to measure thrust forces in the range of **10 μN – 1 mN**, used for characterizing pulsed plasma thrusters (PPTs) and similar low-thrust propulsion systems for small satellites.

Key physical parameters:
- Sensor: **LVDT** (Linear Variable Differential Transformer)
- Excitation: **DCE** (Dynamic Capacitive Excitation), U ≤ 1000 V
- Calibration modes: static (sensitivity S) and dynamic (natural frequency ω₀)
- Operating environment: vacuum chamber (isolated, no network)

<br/>

---

## Contributing

This project is developed within the LaSE research group. For contribution guidelines, please refer to [`CONTRIBUTING.md`](CONTRIBUTING.md).

<br/>

---

## License

MIT License — see [`LICENSE`](LICENSE) for details.

<br/>

<div align="center">

---

*LaSE · Laboratory of Space Systems*  
*Developed for the Micro-Thrust Balance Project*

</div>