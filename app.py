import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(page_title="Sensor Historical Trend Analysis", layout="wide")
st.title("📊 Sensor Historical Trend Analysis")

st.markdown("Upload MQTTX-exported JSON to visualize historical sensor trends.")

uploaded_file = st.file_uploader("Upload JSON file", type=["json"])

if uploaded_file is None:
    st.stop()

data = json.load(uploaded_file)

# ---------------- FIND MESSAGES SAFELY ----------------
messages = []

if isinstance(data, list):
    for item in data:
        if isinstance(item, dict) and "messages" in item:
            messages.extend(item["messages"])

elif isinstance(data, dict) and "messages" in data:
    messages = data["messages"]

if not messages:
    st.error("No messages found in uploaded JSON.")
    st.stop()

# ---------------- PARSE SENSOR DATA ----------------
records = []

for msg in messages:
    try:
        topic = msg.get("topic", "")
        payload_raw = msg.get("payload", "")
        timestamp = msg.get("createAt")

        if topic == "sensor1/data" and payload_raw:
            payload = json.loads(payload_raw)

            records.append({
                "timestamp": pd.to_datetime(timestamp),
                "temperature": payload.get("temp"),
                "moisture": payload.get("moisture"),
                "co2": payload.get("co2")
            })
    except Exception:
        continue

if not records:
    st.error("Sensor messages found, but payload parsing failed.")
    st.stop()

df = pd.DataFrame(records).dropna().sort_values("timestamp")

# ---------------- TIME FILTER ----------------
minutes = st.sidebar.slider("Show last (minutes)", 5, 180, 30)
cutoff = df["timestamp"].max() - pd.Timedelta(minutes=minutes)
df = df[df["timestamp"] >= cutoff]

# ---------------- METRICS ----------------
c1, c2, c3 = st.columns(3)
c1.metric("Temperature (°C)", f"{df['temperature'].iloc[-1]:.2f}")
c2.metric("Moisture (%)", f"{df['moisture'].iloc[-1]:.2f}")
c3.metric("CO₂ (ppm)", f"{df['co2'].iloc[-1]:.2f}")

# ---------------- PLOTS ----------------
st.subheader("Temperature Trend")
st.plotly_chart(px.line(df, x="timestamp", y="temperature"), use_container_width=True)

st.subheader("Moisture Trend")
st.plotly_chart(px.line(df, x="timestamp", y="moisture"), use_container_width=True)

st.subheader("CO₂ Trend")
st.plotly_chart(px.line(df, x="timestamp", y="co2"), use_container_width=True)
