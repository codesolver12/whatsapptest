import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Kiln Monitoring Dashboard", layout="wide")

st.title("Kiln IoT Monitoring – Historical Data")

st.write("Historical visualization of sensor data collected from the kiln monitoring system.")

# -----------------------
# File Upload
# -----------------------
uploaded_file = st.file_uploader(
    "Upload sensor data (Excel)",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Please upload an Excel file to view the dashboard.")
    st.stop()

# -----------------------
# Load Data
# -----------------------
data = pd.read_excel(uploaded_file)

st.write("Detected columns:", data.columns.tolist())

# -----------------------
# Generate Default Timestamp
# -----------------------
SAMPLING_INTERVAL_SEC = 10  # assumed logging interval

num_rows = len(data)
end_time = datetime.now()

data["Time"] = [
    end_time - timedelta(seconds=SAMPLING_INTERVAL_SEC * (num_rows - i - 1))
    for i in range(num_rows)
]

# -----------------------
# Column Mapping (based on your file)
# -----------------------
temp_col = "Temperature"
hum_col = "Moisture"
gas_col = "CO2"

# -----------------------
# Alert Logic
# -----------------------
TEMP_LIMIT = 450

if data[temp_col].max() > TEMP_LIMIT:
    st.error("🚨 ALERT: Kiln temperature exceeded 450°C")
else:
    st.success("✅ Kiln temperature is within safe operating limits")

# -----------------------
# KPI Metrics
# -----------------------
m1, m2, m3 = st.columns(3)

m1.metric("Max Temperature (°C)", round(data[temp_col].max(), 2))
m2.metric("Average Moisture (%)", round(data[hum_col].mean(), 2))
m3.metric("Average CO₂ Level", round(data[gas_col].mean(), 2))

st.divider()

# -----------------------
# Temperature Graph
# -----------------------
temp_fig = px.line(
    data,
    x="Time",
    y=temp_col,
    title="Kiln Temperature Trend"
)

temp_fig.add_hline(
    y=TEMP_LIMIT,
    line_dash="dash",
    annotation_text="Safety Limit (450°C)"
)

st.plotly_chart(temp_fig, use_container_width=True)

# -----------------------
# Moisture Graph
# -----------------------
hum_fig = px.line(
    data,
    x="Time",
    y=hum_col,
    title="Biomass Moisture Trend"
)

st.plotly_chart(hum_fig, use_container_width=True)

# -----------------------
# Gas Graph
# -----------------------
gas_fig = px.line(
    data,
    x="Time",
    y=gas_col,
    title="CO₂ / Gas Concentration Trend"
)

st.plotly_chart(gas_fig, use_container_width=True)

st.divider()

# -----------------------
# Alert History Table
# -----------------------
st.subheader("⚠ Alert History")

if "Alert" in data.columns:
    alert_rows = data[data["Alert"].notna()]

    if not alert_rows.empty:
        st.dataframe(
            alert_rows[["Time", "Alert", "Alert Value"]],
            use_container_width=True,
            height=250
        )
    else:
        st.info("No alert events recorded.")
else:
    st.info("Alert data not available in the uploaded file.")
