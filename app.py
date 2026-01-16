import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sensor Historical Trend Analysis", layout="wide")
st.title("📊 Sensor Historical Trend Analysis")
st.markdown("Upload an Excel file containing sensor data to visualize historical trends.")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is None:
    st.stop()

# ---------------- READ EXCEL ----------------
xls = pd.ExcelFile(uploaded_file)
sheet_names = xls.sheet_names

sensor_df = None
alerts_df = None

# ---------------- AUTO-DETECT SENSOR DATA SHEET ----------------
for sheet in sheet_names:
    temp_df = pd.read_excel(xls, sheet)
    temp_df.columns = temp_df.columns.str.lower().str.strip()

    required_cols = {"timestamp", "temperature", "moisture", "co2"}
    if required_cols.issubset(temp_df.columns):
        sensor_df = temp_df.copy()
        break

if sensor_df is None:
    st.error(
        "No sheet with required columns found.\n"
        "Required columns: timestamp, temperature, moisture, co2"
    )
    st.stop()

# ---------------- OPTIONAL ALERT SHEET ----------------
for sheet in sheet_names:
    temp_df = pd.read_excel(xls, sheet)
    temp_df.columns = temp_df.columns.str.lower().str.strip()

    if {"timestamp", "alert", "value"}.issubset(temp_df.columns) or \
       {"timestamp", "alert_type", "value"}.issubset(temp_df.columns):
        alerts_df = temp_df.copy()
        break

# ---------------- DATA PREP ----------------
sensor_df["timestamp"] = pd.to_datetime(sensor_df["timestamp"])
sensor_df = sensor_df.sort_values("timestamp")

# ---------------- TIME FILTER ----------------
minutes = st.sidebar.slider("Show last (minutes)", 5, 180, 30)
cutoff = sensor_df["timestamp"].max() - pd.Timedelta(minutes=minutes)
sensor_df = sensor_df[sensor_df["timestamp"] >= cutoff]

if alerts_df is not None:
    alerts_df["timestamp"] = pd.to_datetime(alerts_df["timestamp"])
    alerts_df = alerts_df[alerts_df["timestamp"] >= cutoff]

# ---------------- KPI METRICS ----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Temperature (°C)", f"{sensor_df['temperature'].iloc[-1]:.2f}")
c2.metric("Moisture (%)", f"{sensor_df['moisture'].iloc[-1]:.2f}")
c3.metric("CO₂ (ppm)", f"{sensor_df['co2'].iloc[-1]:.2f}")
c4.metric("Alerts", 0 if alerts_df is None else len(alerts_df))

# ---------------- PLOTS ----------------
st.subheader("Temperature Trend")
st.plotly_chart(
    px.line(sensor_df, x="timestamp", y="temperature"),
    use_container_width=True
)

st.subheader("Moisture Trend")
st.plotly_chart(
    px.line(sensor_df, x="timestamp", y="moisture"),
    use_container_width=True
)

st.subheader("CO₂ Trend")
st.plotly_chart(
    px.line(sensor_df, x="timestamp", y="co2"),
    use_container_width=True
)

# ---------------- ALERT TABLE ----------------
if alerts_df is not None and not alerts_df.empty:
    st.subheader("🚨 Alert Log")
    st.dataframe(alerts_df.sort_values("timestamp", ascending=False))
else:
    st.info("No alerts found in the selected time window.")
