import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="IoT Kiln Monitoring", layout="wide")
st.title("🔥 IoT Kiln Historical Monitoring Dashboard")

# Load JSON
with open("data/sensor_data.json", "r") as f:
    raw_data = json.load(f)

records = []

for msg in raw_data:
    if msg.get("topic") == "sensor1/data":
        records.append({
            "timestamp": pd.to_datetime(msg["createAt"]),
            "temperature": msg["payload"]["temp"],
            "moisture": msg["payload"]["moisture"],
            "co2": msg["payload"]["co2"]
        })

df = pd.DataFrame(records).sort_values("timestamp")

# Sidebar filter
minutes = st.sidebar.slider("Show last (minutes)", 5, 120, 30)
cutoff = df["timestamp"].max() - pd.Timedelta(minutes=minutes)
df = df[df["timestamp"] >= cutoff]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Temperature (°C)", f"{df['temperature'].iloc[-1]:.2f}")
col2.metric("Moisture (%)", f"{df['moisture'].iloc[-1]:.2f}")
col3.metric("CO₂ (ppm)", f"{df['co2'].iloc[-1]:.2f}")

# Charts
st.subheader("📈 Temperature Trend")
st.plotly_chart(
    px.line(df, x="timestamp", y="temperature"),
    use_container_width=True
)

st.subheader("📈 Moisture Trend")
st.plotly_chart(
    px.line(df, x="timestamp", y="moisture"),
    use_container_width=True
)

st.subheader("📈 CO₂ Trend")
st.plotly_chart(
    px.line(df, x="timestamp", y="co2"),
    use_container_width=True
)
