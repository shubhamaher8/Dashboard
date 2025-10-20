import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ----------------------------
# Constants & Configuration
# ----------------------------
US_GRID_CO2_FACTOR = 0.4  # kg CO₂ per kWh (approx. US average)

MODEL_ENERGY_FACTORS = {
    "deepseek/deepseek-r1-distill-llama-70b:free": 8.5,
    "openai/gpt-oss-20b:free": 2.71,
    "google/gemma-3n-e4b-it:free": 0.95,
    "meta-llama/llama-4-maverick:free": 6.2,
    "mistralai/mistral-small-24b-instruct-2501:free": 3.8,
    "qwen/qwen3-14b:free": 2.2,
    "meta-llama/llama-4-scout:free": 2.5,
    "default": 2.56  # Add a default value
}

# ----------------------------
# Streamlit Page Setup
# ----------------------------
st.set_page_config(page_title="AI Energy & CO₂ Dashboard", layout="wide")
st.title("⚡ AI Model Energy & CO₂ Dashboard")
st.markdown("An interactive tool to measure and compare the environmental footprint of LLM inference across different models.")

# Sidebar for API Key & Model Selection
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter OpenRouter API Key", type="password")

model = st.sidebar.selectbox(
    "Choose AI Model",
    list(MODEL_ENERGY_FACTORS.keys())[:-1] # Exclude 'default' from selector
)

# Update DataFrame columns
if "history" not in st.session_state:
    st.session_state["history"] = pd.DataFrame(
        columns=[
            "id", "model", "prompt", "input_tokens", "output_tokens",
            "total_tokens", "energy_Wh", "co2_g", "response"
        ]
    )

# ----------------------------
# Helper Functions
# ----------------------------
def call_openrouter_api(model, prompt, api_key):
    """Call OpenRouter API with a given model and prompt."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        output_text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", input_tokens + output_tokens)
        return output_text, input_tokens, output_tokens, total_tokens
    except requests.exceptions.RequestException as e:
        st.error(f"API call failed: {e}")
        return "", 0, 0, 0
    except (KeyError, IndexError) as e:
        st.error(f"Failed to parse API response: {e}. Response: {data}")
        return "", 0, 0, 0

def calculate_energy_co2(tokens, model_name):
    """Calculate energy and CO2 based on token count and the specific model used."""
    energy_per_1k_tokens_wh = MODEL_ENERGY_FACTORS.get(model_name, MODEL_ENERGY_FACTORS["default"])
    energy = (tokens / 1000) * energy_per_1k_tokens_wh
    co2 = energy * US_GRID_CO2_FACTOR
    return energy, co2

# ----------------------------
# Main Application Logic
# ----------------------------
prompt = st.text_area("Enter your prompt:", height=100)
if st.button("Generate & Analyze"):
    if not api_key:
        st.warning("Please enter your OpenRouter API key in the sidebar.")
    elif not prompt:
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Generating response and calculating footprint..."):
            response_text, in_tokens, out_tokens, total_tokens = call_openrouter_api(model, prompt, api_key)

            if total_tokens > 0:
                energy_Wh, co2_g = calculate_energy_co2(total_tokens, model)

                # Store new entry in history
                new_entry = pd.DataFrame([
                    {
                        "id": len(st.session_state["history"]) + 1,
                        "model": model,
                        "prompt": prompt,
                        "input_tokens": in_tokens,
                        "output_tokens": out_tokens,
                        "total_tokens": total_tokens,
                        "energy_Wh": energy_Wh,
                        "co2_g": co2_g,
                        "response": response_text,
                    }
                ])
                st.session_state["history"] = pd.concat([st.session_state["history"], new_entry], ignore_index=True)
                st.success("Analysis complete!")

# ----------------------------
# Display Results
# ----------------------------
if not st.session_state["history"].empty:
    df = st.session_state["history"].copy() # Use a copy for modifications
    latest = df.iloc[-1]

    st.markdown("---")
    st.subheader("Latest Prompt Analysis")
    with st.expander("Show AI Response", expanded=True):
        st.write(latest["response"])

    # Metrics Row for the latest query
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Input Tokens", latest["input_tokens"])
    col2.metric("Output Tokens", latest["output_tokens"])
    col3.metric("Total Tokens", latest["total_tokens"])
    col4.metric("Energy (Wh)", f"{latest['energy_Wh']:.2f}")
    col5.metric("CO₂ (g)", f"{latest['co2_g']:.2f}")

    st.markdown("---")

    # NEW: Headline KPIs Section
    st.subheader("📊 Overall Dashboard Summary")
    total_wh = df['energy_Wh'].sum()
    total_co2_g = df['co2_g'].sum()
    total_prompts = len(df)
    avg_tokens = df['total_tokens'].mean()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Energy Consumed (Wh)", f"{total_wh:.2f}")
    kpi2.metric("Total CO₂ Emitted (g)", f"{total_co2_g:.2f}")
    kpi3.metric("Total Prompts Processed", total_prompts)
    kpi4.metric("Avg. Tokens per Prompt", f"{avg_tokens:.0f}")

    st.markdown("---")

    # NEW: Statistical Analysis Section
    st.subheader("🔬 Statistical Analysis")
    avg_co2_prompt = df['co2_g'].mean()
    median_co2_prompt = df['co2_g'].median()

    stat1, stat2 = st.columns(2)
    stat1.metric("Average CO₂ per Prompt (g)", f"{avg_co2_prompt:.2f}")
    stat2.metric("Median CO₂ per Prompt (g)", f"{median_co2_prompt:.2f}", help="The median is less sensitive to very large/small prompts and can represent a more 'typical' value.")

    st.markdown("---")

    # Charts & Analytics
    st.subheader("📈 Charts & Analytics")
    
    c1, c2 = st.columns(2)

    with c1:
        # CO₂ by Model (Pie Chart)
        fig_pie = px.pie(df, names="model", values="co2_g", title="Total CO₂ Share by Model", hole=.3)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("---")
        
        # Total tokens trend (Scatter Chart)
        fig_total = px.scatter(
            df, x="id", y="total_tokens", color="model", title="Total Tokens Over Queries",
            labels={"id": "Query ID", "total_tokens": "Total Tokens"},
            hover_data=['prompt']
        )
        fig_total.update_xaxes(tickmode='linear', dtick=1)
        st.plotly_chart(fig_total, use_container_width=True)

    with c2:
        # Tokens vs CO2 (Scatter Plot) - No lines between points
        fig_corr = px.scatter(
            df, x="total_tokens", y="co2_g",
            title="Tokens vs. CO₂ Emissions",
            labels={"total_tokens": "Total Tokens", "co2_g": "CO₂ (g)"},
            hover_data=['id', 'prompt']
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        st.markdown("---")

        # Input vs Output tokens (Bar Chart) - Only for latest prompt
        latest_tokens_df = pd.DataFrame({
            "Token Type": ["Input Tokens", "Output Tokens"],
            "Count": [latest["input_tokens"], latest["output_tokens"]]
        })
        fig_tokens = px.bar(
            latest_tokens_df, x="Token Type", y="Count",
            title="Input vs. Output Tokens (Current Prompt)",
            labels={"Count": "Tokens", "Token Type": "Type"},
            text="Count"
        )
        st.plotly_chart(fig_tokens, use_container_width=True)


    st.markdown("---")
    # History Table
    st.subheader("📖 Query History")
    # Define columns to show, excluding the long response text for clarity
    display_cols = ["id", "model", "prompt", "input_tokens", "output_tokens", "total_tokens", "energy_Wh", "co2_g"]
    st.dataframe(df[display_cols])

else:
    st.info("Enter a prompt and click 'Generate & Analyze' to see the dashboard.")
