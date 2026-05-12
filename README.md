#  SIFT — Signal Intelligence for Financial Transactions

> Real-time AI-powered transaction risk monitoring dashboard built for CIB environments.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![scikit-learn](https://img.shields.io/badge/scikit--learn-IsolationForest-orange)
![License](https://img.shields.io/badge/License-MIT-green)



## What Is SIFT?

SIFT is a real-time financial transaction anomaly detection and risk monitoring system. It simulates a live feed of institutional transactions — wire transfers, FX conversions, equity trades, bond settlements and uses machine learning to detect suspicious activity before it becomes a problem.

Built to mirror the kind of risk monitoring infrastructure used in Corporate & Investment Banking environments.



## What It Does

- **Simulates** a live feed of institutional financial transactions (wire transfers, FX, equity trades, derivatives)
- **Detects** anomalous transactions using Isolation Forest — an unsupervised ML algorithm that requires no labelled training data
- **Scores** every transaction on a four-tier risk scale: 🟢 Low / 🟡 Medium / 🟠 High / 🔴 Critical
- **Visualises** risk in real time — scatter plots, donut charts, hourly anomaly heatmaps
- **Alerts** on Critical and High risk transactions in a live feed panel
- **Generates** a downloadable branded PDF audit report with findings and recommendations



## Tech Stack

| Layer | Tool |
|-------|------|
| Dashboard | Streamlit |
| ML Model | scikit-learn (Isolation Forest) |
| Data | Pandas + NumPy |
| Charts | Plotly |
| PDF Reports | fpdf2 |
| Language | Python 3.10+ |



## How Anomaly Detection Works

SIFT uses **Isolation Forest** , an unsupervised ML algorithm that detects outliers by randomly partitioning data. Anomalies are isolated faster (fewer splits) so they receive lower anomaly scores.

Three features drive detection:
1. **Transaction amount** — unusually large values relative to the batch
2. **Hour of day** — transactions at 2–4am are statistically suspicious
3. **Foreign currency flag** — unexpected FX exposure spikes

No labelled training data is required. The model learns what "normal" looks like from the batch itself.



## Project Structue
```
sift/
├── app.py                 # Main Streamlit dashboard — run this
├── transaction_gen.py     # Simulates live institutional transaction feed
├── anomaly_detector.py    # Isolation Forest ML model + risk scoring
├── report_gen.py          # PDF audit report generator
├── requirements.txt       # Dependencies
└── README.md
```



## Run Locally

```bash
# Clone the repo
git clone https://github.com/PixelAndPotion/sift.git
cd sift

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

Then open `http://localhost:8501` in browser.



## Screenshots

> Dashboard showing live transaction feed, risk distribution, and critical alerts panel.




## Built By

**Arika Bharath** — BSc Software Engineering, Eduvos  
[github.com/PixelAndPotion](https://github.com/PixelAndPotion)



*SIFT is a portfolio project demonstrating ML-based anomaly detection applied to financial transaction risk monitoring.*
