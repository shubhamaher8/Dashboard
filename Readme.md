# ⚡ AI Energy & CO₂ Dashboard

Live app ➜ https://ai-sustainable-co2-energy-dashboard.streamlit.app/

> Measure, visualize, and compare the environmental footprint of LLM inference across different models — in real time.

![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌍 Overview

This interactive Streamlit app estimates electricity usage and CO₂ emissions produced when running prompts on different large language models via OpenRouter. It tracks token usage, estimates energy consumption, and visualizes the total and per‑prompt environmental impact — helping you make greener AI choices.

### What you can do

- 🧪 Run prompts against multiple AI models
- 🔋 Estimate energy use (kWh) per query
- 🌫️ Convert energy to CO₂ emissions (kg), using a US grid average factor
- 📈 Explore charts for trends, correlations, and model share
- 🗂️ Review a query history with tokens, energy, and CO₂ per run

---

## 🚀 Live Demo

Open the hosted app on Streamlit Cloud:

- App: https://ai-sustainable-co2-energy-dashboard.streamlit.app/


---

## 🧠 How it works

The app calls OpenRouter’s chat completion API, reads token usage, and applies model‑specific energy factors to estimate electricity and emissions.

### 🧮 Footprint calculations

- Energy factor by model (kWh per 1K tokens)
- US grid average emission factor: 0.4 kg CO₂ per kWh (configurable in code)

Formulas:

- $E_{kWh} = \dfrac{\text{tokens}}{1000} \times \text{energyFactor(model)}$
- $\text{CO₂}_{kg} = E_{kWh} \times 0.4$

### 📦 Model energy factors (defaults in code)

| Model | kWh / 1K tokens |
|---|---:|
| x-ai/grok-4-fast:free | 0.00045 |
| openai/gpt-oss-20b:free | 0.00040 |
| google/gemma-3n-e4b-it:free | 0.00015 |
| meta-llama/llama-4-maverick:free | 0.00035 |
| default (fallback) | 0.00030 |

> These are illustrative factors intended for relative comparison, not lifecycle‑accurate measurements. See “Notes & caveats.”

---

## 🧷 Key screens

- 📨 Latest Prompt Analysis: response viewer with token/energy/CO₂ metrics
- 🧭 Dashboard KPIs: total energy, total CO₂, prompts processed, avg tokens per prompt
- 📊 Statistical Analysis: average and median CO₂ per prompt
- 📉 Charts & Analytics:
	- CO₂ share by model (pie)
	- Tokens over time (line)
	- Tokens vs CO₂ correlation (scatter/line)
	- Input vs Output tokens for the latest prompt (bar)
- 📖 Query History table

---

## 🛠️ Local setup (Windows / PowerShell)

1) Clone or download this repository.

2) Create a virtual environment (optional but recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Install dependencies:

```powershell
pip install -r requirements.txt
```

4) Run the app:

```powershell
streamlit run app.py
```

5) Open the Streamlit sidebar and paste your OpenRouter API key when prompted.

---

## 🔑 Configuration

OpenRouter API key is entered securely via the Streamlit sidebar at runtime.

---

## 📚 Project structure

```
app.py              # Streamlit app
requirements.txt    # Python dependencies
Readme.md           
public/             # static assets
```

---

## 🧭 Usage guide

1. Enter your OpenRouter API key in the sidebar.
2. Select a model from the dropdown.
3. Type your prompt and click “Generate & Analyze.”
4. Review the AI response, token usage, energy, and CO₂ output.
5. Explore the analytics and history to compare models and prompts.

---

## 🧩 Tech stack

- 🖼️ Streamlit for UI and state management
- 🔗 Requests for API calls
- 🧮 Pandas for data handling
- 📈 Plotly Express for interactive charts

---

## 🗺️ Roadmap

- ✅ Per‑model energy factors and token accounting
- ✅ KPI dashboard with charts and history
- ⏳ Export to CSV / JSON
- ⏳ Model latency and cost overlays
- ⏳ Region‑specific grid emission factors
- ⏳ Persistent storage (e.g., SQLite) beyond the session

Contributions welcome — see below!


---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) included.
