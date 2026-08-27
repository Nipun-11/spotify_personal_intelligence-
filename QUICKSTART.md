# Spotify Personal Intelligence Engine — Quickstart Guide

This guide describes how to reproduce the entire pipeline from scratch on a clean machine.

---

## 1. Prerequisites

- Python 3.10, 3.11, or 3.12+
- Git & Virtualenv (or Conda)

---

## 2. Installation

```bash
# Clone the repository
git clone https://github.com/Nipun-11/spotify_personal_intelligence-.git
cd spotify_personal_intelligence-

# Create and activate virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 3. Data Processing & Pipeline Execution

```bash
# Run the complete end-to-end data pipeline
# (Ingestion -> Validation -> Normalization -> Sessionization -> Analytics -> Discovery Engine)
python scripts/run_pipeline.py
```
*Outputs generated in `data/processed/` as optimized Parquet and JSON files.*

---

## 4. Machine Learning Training & Benchmark Evaluation

```bash
# Build chronological datasets, train baselines and LightGBM model, and run leakage audit
python scripts/run_ml.py
```
*Outputs generated in `data/ml/`, `models/`, and `reports/`.*

---

## 5. Run Automated Test Suite

```bash
pytest -v
```

---

## 6. Launch REST API Backend & Interactive Dashboard

```bash
python scripts/start_server.py
```
Open **http://127.0.0.1:8000** in your browser to view the interactive Spotify Personal Intelligence Engine.

---

## 7. Generate Public Demonstration Dataset

```bash
python scripts/export_sample_data.py
```
Generates a sanitized 500-record JSON dataset in `data/sample/sample_streaming_history.json` with redacted IP addresses (`0.0.0.0`) for public portfolio sharing.
