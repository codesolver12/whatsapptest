import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

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
# Generate Default Timestamp
# -----------------------
SAMPLING_INTERVAL_SEC = 10  # adjust if needed

num_rows = len(data)
end_time = datetime.now()

generated_time = [
    end_time - timedelta(seconds=SAMPLING_INTERVAL_SEC * (num_rows - i - 1))
    for i in range(num_rows)
]

data["Time"] = generated_time

# -----------------------
# Detect Sensor Columns
# -----------------------
temp_col = None
hum_col = None
gas_col = None

for col in data.columns:
    c = col.lower()

    if temp_col is None and "temp" in c:
        temp_col = col

    if hum_col is None and ("moisture" in c or "humidity" in c):
        hum_col = col

    if gas_col is None and ("co" in c or "gas" in c):
        gas_col = col

if temp_col is None or hum_col is None or gas_col is None:
    st.error("Required sensor columns not found.")
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

latest_time = data["Time"].max()
start_time = latest_time - timedelta(minutes=minutes)

filtered_data = data[data["Time"] >= start_time]

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
c3.metric("Average Gas Level", round(filtered_data[gas_col].mean(), 2))

# -----------------------
# Plots
# -----------------------
st.plotly_chart(
    px.line(filtered_data, x="Time", y=temp_col, title="Temperature Trend"),
    use_container_width=True
)

st.plotly_chart(
    px.line(filtered_data, x="Time", y=hum_col, title="Moisture Trend"),
    use_container_width=True
)

st.plotly_chart(
    px.line(filtered_data, x="Time", y=gas_col, title="Gas / Smoke Trend"),
    use_container_width=True
)

# -----------------------
# Raw Data
# -----------------------
with st.expander("View data with generated timestamps"):
    st.dataframe(filtered_data)
