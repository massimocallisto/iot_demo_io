import os
import random
from datetime import datetime

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("Missing dependency: install 'streamlit-autorefresh' first.")
    st.stop()

load_dotenv()

st.set_page_config(
    page_title="IoT Demo",
    page_icon="📡",
    layout="wide",
)

st.title("📡 IoT Live Dashboard")
st.caption("Un semplice esempio di sensore IoT: temperatura, umidità e presenza, aggiornati ogni 3 secondi.")

st.info("💡 Idea di base dell'IoT: il sensore raccoglie dati, li invia e li visualizza in tempo reale per aiutare a capire lo stato dell'ambiente.")

st_autorefresh(interval=8000, key="iot_refresh")

if "history" not in st.session_state:
    st.session_state.history = []

# Generate realistic random sensor values
temperature = round(random.uniform(18.5, 29.5), 1)
humidity = round(random.uniform(30.0, 85.0), 1)
presence = random.choice([True, False])

if temperature < 20:
    temp_status = "Fresco"
    temp_color = "🧊"
elif temperature <= 25:
    temp_status = "Nella norma"
    temp_color = "🌤️"
else:
    temp_status = "Caldo"
    temp_color = "🔥"

if humidity < 40:
    hum_status = "Bassa"
    hum_color = "💨"
elif humidity <= 60:
    hum_status = "Nella norma"
    hum_color = "💧"
else:
    hum_status = "Alta"
    hum_color = "🌧️"

presence_label = "Presenza rilevata" if presence else "Nessuna presenza"
presence_icon = "🟢" if presence else "⚪"


def get_ai_summary(temp: float, hum: float, has_presence: bool) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

    if not api_key:
        return "AI summary unavailable: add OPENROUTER_API_KEY to the .env file."

    prompt = (
        "You are helping a non-expert understand an IoT sensor dashboard. "
        f"Current values: temperature {temp}°C, humidity {hum}%, presence {'detected' if has_presence else 'not detected'}. "
        "Write a short, friendly explanation in Italian, with simple advice and no technical jargon."
    )

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "http://localhost",
                "X-Title": "IoT Demo",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
            },
            timeout=45,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        return f"AI summary unavailable right now: {exc}"


record_time = datetime.now()

st.session_state.history.append(
    {
        "Ora": record_time,
        "Temperatura": temperature,
        "Umidità": humidity,
        "Presenza": "Sì" if presence else "No",
    }
)
st.session_state.history = st.session_state.history[-15:]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div style='background:#1f2937; padding:16px; border-radius:14px; border-left:6px solid #38bdf8;'>
          <div style='font-size:24px;'>{temp_color} Temperatura</div>
          <div style='font-size:32px; font-weight:700; color:#67e8f9;'>{temperature} °C</div>
          <div style='font-size:14px; color:#dbeafe;'>Stato: {temp_status}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div style='background:#1f2937; padding:16px; border-radius:14px; border-left:6px solid #4ade80;'>
          <div style='font-size:24px;'>{hum_color} Umidità</div>
          <div style='font-size:32px; font-weight:700; color:#bbf7d0;'>{humidity} %</div>
          <div style='font-size:14px; color:#dcfce7;'>Stato: {hum_status}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div style='background:#1f2937; padding:16px; border-radius:14px; border-left:6px solid #facc15;'>
          <div style='font-size:24px;'>{presence_icon} Presenza</div>
          <div style='font-size:18px; font-weight:700; color:#fde68a;'>{presence_label}</div>
          <div style='font-size:14px; color:#fef3c7;'>Il sensore segnala se c'è movimento o meno.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### 🤖 AI insight")
st.info(get_ai_summary(temperature, humidity, presence))

st.divider()
st.subheader("📊 Storico degli ultimi valori")
df = pd.DataFrame(st.session_state.history)
df["Ora"] = pd.to_datetime(df["Ora"])
df = df.sort_values("Ora", ascending=False).reset_index(drop=True)
df["Ora"] = df["Ora"].dt.strftime("%H:%M:%S")
st.dataframe(df, width="stretch", hide_index=True)

