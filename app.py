import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

st.set_page_config(page_title="Kiln Monitoring Dashboard", layout="wide")

st.title("Kiln IoT Monitoring – Historical Data")

st.write("Upload the Excel file generated from the IoT system.")

# -----------------------
# File Upload
# -----------------------
uploaded_file = st.file_uploader(
    "Upload sensor data (Excel)",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Please upload an Excel file to continue.")
    st.stop()

# -----------------------
# Read Data
# -----------------------
data = pd.read_excel(uploaded_file)

st.write("Detected columns:", data.columns.tolist())

# -----------------------
# Detect Timestamp Column
# -----------------------
time_col = None
time_keywords = ["timestamp", "time", "datetime", "date"]

for col in data.columns:
    if any(key in col.lower() for key in time_keywords):
        time_col = col
        break

if time_col is None:
    st.error("No time-related column found. Please check the Excel file.")
    st.stop()

data[time_col] = pd.to_datetime(data[time_col])
data = data.sort_values(time_col)

# -----------------------
# Detect Sensor Columns
# -----------------------
temp_col = None
hum_col = None
gas_col = None

for col in data.columns:
    col_lower = col.lower()

    if temp_col is None and "temp" in col_lower:
        temp_col = col

    if hum_col is None and ("humidity" in col_lower or "moisture" in col_lower):
        hum_col = col

    if gas_col is None and ("gas" in col_lower or "smoke" in col_lower or "co" in col_lower):
        gas_col = col

missing_cols = []
if temp_col is None:
    missing_cols.append("Temperature")
if hum_col is None:
    missing_cols.append("Humidity / Moisture")
if gas_col is None:
    missing_cols.append("Gas / Smoke")

if missing_cols:
    st.error(f"Missing sensor columns: {', '.join(missing_cols)}")
    st.stop()

# -----------------------
# Sidebar Filter
# -----------------------
st.sidebar.header("Data Filter")

minutes = st.sidebar.selectbox(
    "Show data for last",
    [30, 60, 90, 120],
    index=0
)

latest_time = data[time_col].max()
start_time = latest_time - timedelta(minutes=minutes)

filtered_data = data[data[time_col] >= start_time]

# -----------------------
# Alert Logic
# -----------------------
if filtered_data[temp_col].max() > 450:
    st.warning("⚠ Warning: Kiln temperature exceeded 450°C")
else:
    st.success("Kiln temperature is within safe limits")

# -----------------------
# Summary Metrics
# -----------------------
col1, col2, col3 = st.columns(3)

col1.metric(
    "Max Temperature (°C)",
    round(filtered_data[temp_col].max(), 2)
)

col2.metric(
    "Average Humidity (%)",
    round(filtered_data[hum_col].mean(), 2)
)

col3.metric(
    "Average Gas Level",
    round(filtered_data[gas_col].mean(), 2)
)

# -----------------------
# Temperature Plot
# -----------------------
fig_temp = px.line(
    filtered_data,
    x=time_col,
    y=temp_col,
    title="Kiln Temperature Trend"
)
st.plotly_chart(fig_temp, use_container_width=True)

# -----------------------
# Humidity Plot
# -----------------------
fig_hum = px.line(
    filtered_data,
    x=time_col,
    y=hum_col,
    title="Biomass Humidity / Moisture Trend"
)
st.plotly_chart(fig_hum, use_container_width=True)

# -----------------------
# Gas Plot
# -----------------------
fig_gas = px.line(
    filtered_data,
    x=time_col,
    y=gas_col,
    title="Gas / Smoke Level Trend"
)
st.plotly_chart(fig_gas, use_container_width=True)

# -----------------------
# Raw Data View
# -----------------------
with st.expander("View filtered data"):
    st.dataframe(filtered_data)
