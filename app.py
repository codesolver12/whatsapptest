import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(page_title="Sensor Historical Trend Analysis", layout="wide")

# ✅ REQUIRED HEADING
st.title("📊 Sensor Historical Trend Analysis")
st.markdown("Upload MQTT-exported JSON to visualize historical sensor trends.")

# ---------------- FILE UPLOADER ----------------
uploaded_file = st.file_uploader(
    "Upload sensor data JSON file",
    type=["json"]
)

if uploaded_file is None:
    st.info("Please upload a JSON file to begin analysis.")
    st.stop()

data = json.load(uploaded_file)

# ---------------- EXTRACT MESSAGES CORRECTLY ----------------
if not isinstance(data, list) or "messages" not in data[0]:
    st.error("Invalid JSON format. Expected MQTT export with 'messages' field.")
    st.stop()

messages = data[0]["messages"]

records = []

for msg in messages:
    if msg.get("topic") == "sensor1/data":
        try:
            payload = json.loads(msg["payload"])  # payload is STRING
            records.append({
                "timestamp": pd.to_datetime(msg["createAt"]),
                "temperature": payload.get("temp"),
                "moisture": payload.get("moisture"),
                "co2": payload.get("co2")
            })
        except Exception:
            continue

# ---------------- FINAL VALIDATION ----------------
if len(records) == 0:
    st.error("No sensor1/data entries found in the uploaded file.")
    st.stop()

df = pd.DataFrame(records).dropna().sort_values("timestamp")

# ---------------- TIME FILTER ----------------
minutes = st.sidebar.slider("Show last (minutes)", 5, 180, 30)
cutoff = df["timestamp"].max() - pd.Timedelta(minutes=minutes)
df = df[df["timestamp"] >= cutoff]

# ---------------- KPI METRICS ----------------
col1, col2, col3 = st.columns(3)
col1.metric("Temperature (°C)", f"{df['temperature'].iloc[-1]:.2f}")
col2.metric("Moisture (%)", f"{df['moisture'].iloc[-1]:.2f}")
col3.metric("CO₂ (ppm)", f"{df['co2'].iloc[-1]:.2f}")

# ---------------- PLOTS ----------------
st.subheader("Temperature Trend")
st.plotly_chart(
    px.line(df, x="timestamp", y="temperature"),
    use_container_width=True
)

st.subheader("Moisture Trend")
st.plotly_chart(
    px.line(df, x="timestamp", y="moisture"),
    use_container_width=True
)

st.subheader("CO₂ Trend")
st.plotly_chart(
    px.line(df, x="timestamp", y="co2"),
    use_container_width=True
)
