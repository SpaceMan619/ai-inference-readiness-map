# AI Inference Readiness Map — Africa (v0)

A founder-facing decision-support tool that visualises where **AI inference workloads**
can realistically be deployed across Africa today.

This project focuses on *deployment reality*, not hype — helping builders understand
where low-latency inference is viable, where it’s emerging, and where it still requires
significant operational effort.

---

## Why this exists

Most conversations about AI infrastructure in Africa focus on:
- sovereignty AI
- hyperscale training clusters
- long-term national strategies

As a founder, the more immediate question is simpler:

> *“Where can I deploy inference today without heroic effort?”*

This tool attempts to answer that question in a **directional, honest way**.

---

## What this tool does (v0)

- Interactive map of selected African countries
- Country-level AI inference readiness classification:
  - **Viable**
  - **Emerging**
  - **Emerging (Early)**
- Qualitative signals across:
  - data center presence
  - cloud maturity
  - power reliability
  - operational friction
- Founder-oriented insight for each country

This is **not** a comprehensive data center database and does **not** attempt to measure
hyperscale training capacity.

---

## What this tool does NOT do

- ❌ No MW-level capacity claims
- ❌ No training / frontier model benchmarking
- ❌ No claim of perfect or complete data
- ❌ No real-time infrastructure monitoring

All data is **directional** and intended for early-stage decision-making.

---

## Tech stack

- **Python**
- **Streamlit** — UI and app framework
- **pandas** — data handling
- **Plotly** — interactive map visualisation

---

## Project structure
ai-inference-map/
├── app.py
├── requirements.txt
├── data/
│   └── ai_inference_readiness_africa_v0.csv

- `app.py` — main Streamlit application
- `data/` — source-of-truth dataset (CSV)
- `requirements.txt` — Python dependencies

---

## Running locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py

Then open:
http://localhost:8501

