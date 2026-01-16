import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sensor Historical Trend Analysis", layout="wide")

st.title("📊 Sensor Historical Trend Analysis")
st.markdown("Upload the Excel file containing sensor data and alerts.")

uploaded_file = st.file_uploader(
    "Upload sensor Excel file",
    type=["xlsx"]
)

if uploaded_file is None:
    st.stop()

# ---------------- LOAD SHEETS ----------------
xls = pd.ExcelFile(uploaded_file)

if "sensor_data" not in xls.sheet_names:
    st.error("Excel must contain a sheet named 'sensor_data'")
    st.stop()

df = pd.read_excel(xls, "sensor_data")
df.columns = df.columns.str.lower().str.strip()
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

# ---------------- LOAD ALERTS (OPTIONAL) ----------------
alerts_df = None
if "alerts" in xls.sheet_names:
    alerts_df = pd.read_excel(xls, "alerts")
    alerts_df.columns = alerts_df.columns.str.lower().str.strip()
    alerts_df["timestamp"] = pd.to_datetime(alerts_df["timestamp"])

# ---------------- TIME FILTER ----------------
minutes = st.sidebar.slider("Show last (minutes)", 5, 180, 30)
cutoff = df["timestamp"].max() - pd.Timedelta(minutes=minutes)
df = df[df["timestamp"] >= cutoff]

if alerts_df is not None:
    alerts_df = alerts_df[alerts_df["timestamp"] >= cutoff]

# ---------------- KPI METRICS ----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Temperature (°C)", f"{df['temperature'].iloc[-1]:.2f}")
c2.metric("Moisture (%)", f"{df['moisture'].iloc[-1]:.2f}")
c3.metric("CO₂ (ppm)", f"{df['co2'].iloc[-1]:.2f}")
c4.metric("Alerts (last window)", 0 if alerts_df is None else len(alerts_df))

# ---------------- PLOTS ----------------
st.subheader("Temperature Trend")
st.plotly_chart(px.line(df, x="timestamp", y="temperature"), use_container_width=True)

st.subheader("Moisture Trend")
st.plotly_chart(px.line(df, x="timestamp", y="moisture"), use_container_width=True)

st.subheader("CO₂ Trend")
st.plotly_chart(px.line(df, x="timestamp", y="co2"), use_container_width=True)

# ---------------- ALERTS SECTION ----------------
if alerts_df is not None and not alerts_df.empty:
    st.subheader("🚨 Alert Log")
    st.dataframe(alerts_df.sort_values("timestamp", ascending=False))
else:
    st.info("No alerts in the selected time window.")
