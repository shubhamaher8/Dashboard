import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ----------------------------
# Constants
# ----------------------------
US_GRID_CO2_FACTOR = 0.4  # kg CO₂ per kWh (approx. US average)
ENERGY_PER_1K_TOKENS_KWH = 0.0003  # Example: 0.0003 kWh per 1K tokens (placeholder)

# ----------------------------
# Streamlit Setup
# ----------------------------
st.set_page_config(page_title="AI Energy And CO₂ Dashboard", layout="wide")
st.title("⚡ AI Model Energy And CO₂ Dashboard")

# Sidebar for API Key & Model Selection
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter OpenRouter API Key", type="password")

model = st.sidebar.selectbox(
    "Choose AI Model",
    [
        "x-ai/grok-4-fast:free",
        "openai/gpt-oss-20b:free",
        "google/gemma-3n-e4b-it:free",
        "meta-llama/llama-4-maverick:free",
    ],
)

# Initialize history DataFrame
if "history" not in st.session_state:
    st.session_state["history"] = pd.DataFrame(
        columns=[
            "id", "model", "prompt", "input_tokens", "output_tokens",
            "total_tokens", "energy_kWh", "co2_kg", "response"
        ]
    )

# ----------------------------
# Helper Functions
# ----------------------------
def call_openrouter_api(model, prompt, api_key):
    """Call OpenRouter API with given model and prompt."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        output_text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", input_tokens + output_tokens)
        return output_text, input_tokens, output_tokens, total_tokens
    except Exception as e:
        st.error(f"API call failed: {e}")
        return "", 0, 0, 0

def calculate_energy_co2(tokens):
    energy = (tokens / 1000) * ENERGY_PER_1K_TOKENS_KWH
    co2 = energy * US_GRID_CO2_FACTOR
    return energy, co2

# ----------------------------
# Main Prompt Input
# ----------------------------
prompt = st.text_area("Enter your prompt:")
if st.button("Generate Answer"):
    if not api_key:
        st.warning("Please enter your OpenRouter API key in the sidebar.")
    else:
        with st.spinner("Generating response..."):
            response_text, in_tokens, out_tokens, total_tokens = call_openrouter_api(model, prompt, api_key)
            energy_kWh, co2_kg = calculate_energy_co2(total_tokens)

            # Store in history
            new_entry = pd.DataFrame([
                {
                    "id": len(st.session_state["history"]) + 1,
                    "model": model,
                    "prompt": prompt,
                    "input_tokens": in_tokens,
                    "output_tokens": out_tokens,
                    "total_tokens": total_tokens,
                    "energy_kWh": energy_kWh,
                    "co2_kg": co2_kg,
                    "response": response_text,
                }
            ])
            st.session_state["history"] = pd.concat([st.session_state["history"], new_entry], ignore_index=True)

            st.success("Response generated!")

# ----------------------------
# Display Latest Response
# ----------------------------
if not st.session_state["history"].empty:
    latest = st.session_state["history"].iloc[-1]
    st.subheader("AI Response")
    st.write(latest["response"])

    # Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Input Tokens", latest["input_tokens"])
    col2.metric("Output Tokens", latest["output_tokens"])
    col3.metric("Total Tokens", latest["total_tokens"])
    col4.metric("Energy (kWh)", f"{latest['energy_kWh']:.6f}")
    col5.metric("CO₂ (kg)", f"{latest['co2_kg']:.6f}")

# ----------------------------
# Charts & Analytics
# ----------------------------
if not st.session_state["history"].empty:
    df = st.session_state["history"]

    # Input vs Output tokens
    fig_tokens = px.bar(
        df,
        x="id",
        y=["input_tokens", "output_tokens"],
        title="Input vs Output Tokens per Query",
        labels={"value": "Tokens", "id": "Query ID"},
    )
    st.plotly_chart(fig_tokens, use_container_width=True)

    # Total tokens trend
    fig_total = px.line(
        df,
        x="id",
        y="total_tokens",
        title="Total Tokens Over Queries",
        markers=True
    )
    st.plotly_chart(fig_total, use_container_width=True)

    # Tokens vs CO2
    fig_corr = px.scatter(
        df,
        x="total_tokens",
        y="co2_kg",
        color="model",
        title="Tokens vs CO₂ Emissions",
        labels={"total_tokens": "Total Tokens", "co2_kg": "CO₂ (kg)"}
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # CO₂ by Model
    fig_pie = px.pie(df, names="model", values="co2_kg", title="CO₂ Share by Model")
    st.plotly_chart(fig_pie, use_container_width=True)

    # History Table
    st.subheader("Query History")
    st.dataframe(df["id model prompt input_tokens output_tokens total_tokens energy_kWh co2_kg".split()])
