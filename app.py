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
for col in data.columns:
    if "time" in col.lower():
        time_col = col
        break

if time_col is None:
    st.error("No timestamp column found.")
    st.stop()

# -----------------------
# SAFE datetime conversion
# -----------------------
data[time_col] = pd.to_datetime(
    data[time_col],
    errors="coerce"   # <-- critical fix
)

# Drop rows with invalid timestamps
data = data.dropna(subset=[time_col])

if data.empty:
    st.error("No valid timestamp data found after cleaning.")
    st.stop()

data = data.sort_values(time_col)

# -----------------------
# Detect Sensor Columns
# -----------------------
temp_col = "Temperature"
hum_col = "Moisture"
gas_col = "CO2"

for col in data.columns:
    c = col.lower()
    if "temp" in c:
        temp_col = col
    if "moisture" in c or "humidity" in c:
        hum_col = col
    if "co" in c or "gas" in c:
        gas_col = col

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

if filtered_data.empty:
    st.warning("No data available for the selected time range.")
    st.stop()

# -----------------------
# Alert Logic
# -----------------------
if filtered_data[temp_col].max() > 450:
    st.warning("⚠ Warning: Kiln temperature exceeded 450°C")
else:
    st.success("Kiln temperature is within safe limits")

# -----------------------
# Metrics
# -----------------------
c1, c2, c3 = st.columns(3)

c1.metric("Max Temperature (°C)", round(filtered_data[temp_col].max(), 2))
c2.metric("Average Moisture (%)", round(filtered_data[hum_col].mean(), 2))
c3.metric("Average CO₂ Level", round(filtered_data[gas_col].mean(), 2))

# -----------------------
# Plots
# -----------------------
st.plotly_chart(
    px.line(filtered_data, x=time_col, y=temp_col, title="Temperature Trend"),
    use_container_width=True
)

st.plotly_chart(
    px.line(filtered_data, x=time_col, y=hum_col, title="Moisture Trend"),
    use_container_width=True
)

st.plotly_chart(
    px.line(filtered_data, x=time_col, y=gas_col, title="CO₂ Trend"),
    use_container_width=True
)

# -----------------------
# Raw Data
# -----------------------
with st.expander("View cleaned data"):
    st.dataframe(filtered_data)
