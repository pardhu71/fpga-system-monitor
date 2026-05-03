# fpga-system-monitor
Real-time FPGA monitoring dashboard built with Python and PyQt5
# FPGA System Monitor Dashboard

A real-time GUI dashboard built with Python + PyQt5 that simulates FPGA telemetry monitoring.

## What It Shows
- Clock Frequency (MHz) — live updating
- Core Temperature (°C) — with red alert when overheating
- Power Draw (W)
- LUT Utilization (%)
- Resource bars — LUT, Flip-Flop, BRAM, DSP, I/O
- Device Info — Xilinx Virtex-7

## Tech Stack
- Python 3.x
- PyQt5 — GUI framework
- PyQtGraph — Real-time charts

## How To Run

Install dependencies:
pip install PyQt5 pyqtgraph

Run:
python dashboard.py

## About
Built as a portfolio project to demonstrate GUI development skills
relevant to embedded systems and aerospace applications.

Developer: Masimukku Pardhasardhi
