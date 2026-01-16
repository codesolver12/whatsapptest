import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Sensor Historical Trend Analysis",
    layout="wide"
)

# ---------------- TITLE ----------------
st.title("📊 Sensor Historical Trend Analysis")
st.markdown(
    "Upload an Excel file containing IoT sensor logs to visualize "
    "historical trends and alert events."
)

# ---------------- FILE UPLOADER ----------------
uploaded_file = st.file_uploader(
    "Upload Excel file (.xlsx)",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Please upload an Excel file to begin analysis.")
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
        "No valid sensor data sheet found.\n\n"
        "Required columns:\n"
        "- timestamp\n"
        "- temperature\n"
        "- moisture\n"
        "- co2"
    )
    st.stop()

# ---------------- AUTO-DETECT ALERT SHEET (OPTIONAL) ----------------
for sheet in sheet_names:
    temp_df = pd.read_excel(xls, sheet)
    temp_df.columns = temp_df.columns.str.lower().str.strip()

    if {"timestamp", "alert", "value"}.issubset(temp_df.columns) or \
       {"timestamp", "alert_type", "value"}.issubset(temp_df.columns):
        alerts_df = temp_df.copy()
        break

# ---------------- ROBUST TIMESTAMP PARSING ----------------
sensor_df["timestamp"] = pd.to_datetime(
    sensor_df["timestamp"],
    errors="coerce",
    infer_datetime_format=True
)

sensor_df = sensor_df.dropna(subset=["timestamp"])
sensor_df = sensor_df.sort_values("timestamp")

# ---------------- SIDEBAR FILTER ----------------
minutes = st.sidebar.slider(
    "Show last (minutes)",
    min_value=5,
    max_value=180,
    value=30
)

cutoff = sensor_df["timestamp"].max() - pd.Timedelta(minutes=minutes)
sensor_df = sensor_df[sensor_df["timestamp"] >= cutoff]

# ---------------- PARSE ALERTS (IF PRESENT) ----------------
if alerts_df is not None:
    alerts_df["timestamp"] = pd.to_datetime(
        alerts_df["timestamp"],
        errors="coerce",
        infer_datetime_format=True
    )
    alerts_df = alerts_df.dropna(subset=["timestamp"])
    alerts_df = alerts_df[alerts_df["timestamp"] >= cutoff]

# ---------------- KPI METRICS ----------------
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Temperature (°C)",
    f"{sensor_df['temperature'].iloc[-1]:.2f}"
)

col2.metric(
    "Moisture (%)",
    f"{sensor_df['moisture'].iloc[-1]:.2f}"
)

col3.metric(
    "CO₂ (ppm)",
    f"{sensor_df['co2'].iloc[-1]:.2f}"
)

col4.metric(
    "Alerts (Selected Window)",
    0 if alerts_df is None else len(alerts_df)
)

# ---------------- SENSOR TRENDS ----------------
st.subheader("📈 Temperature Trend")
st.plotly_chart(
    px.line(
        sensor_df,
        x="timestamp",
        y="temperature",
        labels={"temperature": "Temperature (°C)"}
    ),
    use_container_width=True
)

st.subheader("📈 Moisture Trend")
st.plotly_chart(
    px.line(
        sensor_df,
        x="timestamp",
        y="moisture",
        labels={"moisture": "Moisture (%)"}
    ),
    use_container_width=True
)

st.subheader("📈 CO₂ Trend")
st.plotly_chart(
    px.line(
        sensor_df,
        x="timestamp",
        y="co2",
        labels={"co2": "CO₂ (ppm)"}
    ),
    use_container_width=True
)

# ---------------- ALERT LOG ----------------
st.subheader("🚨 Alert Log")

if alerts_df is not None and not alerts_df.empty:
    st.dataframe(
        alerts_df.sort_values("timestamp", ascending=False),
        use_container_width=True
    )
else:
    st.info("No alerts detected in the selected time window.")
