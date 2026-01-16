import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(page_title="Sensor Historical Trend Analysis", layout="wide")

# REQUIRED HEADING
st.title("📊 Sensor Historical Trend Analysis")
st.markdown("Upload the exported MQTT JSON file to visualize historical sensor trends.")

# ---------------- FILE UPLOADER ----------------
uploaded_file = st.file_uploader(
    "Upload sensor data JSON file",
    type=["json"]
)

if uploaded_file is None:
    st.info("Please upload a JSON file to begin analysis.")
    st.stop()

raw_data = json.load(uploaded_file)

records = []

# ---------------- PARSE JSON SAFELY ----------------
for msg in raw_data:
    if msg.get("topic") == "sensor1/data" and "payload" in msg:
        try:
            payload = json.loads(msg["payload"])  # ✅ FIX HERE

            records.append({
                "timestamp": pd.to_datetime(msg["createAt"]),
                "temperature": payload.get("temp"),
                "moisture": payload.get("moisture"),
                "co2": payload.get("co2")
            })
        except Exception:
            continue  # skip malformed entries safely

# ---------------- DATAFRAME CHECK ----------------
if not records:
    st.error("No valid sensor data found in the uploaded JSON file.")
    st.stop()

df = pd.DataFrame(records)
df = df.dropna()
df = df.sort_values("timestamp")

# ---------------- TIME FILTER ----------------
minutes = st.sidebar.slider("Show last (minutes)", 5, 180, 30)
cutoff = df["timestamp"].max() - pd.Timedelta(minutes=minutes)
df = df[df["timestamp"] >= cutoff]

# ---------------- KPI CARDS ----------------
col1, col2, col3 = st.columns(3)
col1.metric("Temperature (°C)", f"{df['temperature'].iloc[-1]:.2f}")
col2.metric("Moisture (%)", f"{df['moisture'].iloc[-1]:.2f}")
col3.metric("CO₂ (ppm)", f"{df['co2'].iloc[-1]:.2f}")

# ---------------- CHARTS ----------------
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
