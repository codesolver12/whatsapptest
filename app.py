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
SAMPLING_INTERVAL_SEC = 10  # assumed logging interval

num_rows = len(data)
end_time = datetime.now()

data["Time"] = [
    end_time - timedelta(seconds=SAMPLING_INTERVAL_SEC * (num_rows - i - 1))
    for i in range(num_rows)
]

# -----------------------
# Detect Sensor Columns
# -----------------------
temp_col = "Temperature"
hum_col = "Moisture"
gas_col = "CO2"

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
# Live Alert Logic
# -----------------------
TEMP_LIMIT = 450

if filtered_data[temp_col].max() > TEMP_LIMIT:
    st.error("🚨 ALERT: Kiln temperature exceeded 450°C")
else:
    st.success("✅ Kiln temperature within safe limits")

# -----------------------
# Summary Metrics
# -----------------------
c1, c2, c3 = st.columns(3)

c1.metric("Max Temperature (°C)", round(filtered_data[temp_col].max(), 2))
c2.metric("Average Moisture (%)", round(filtered_data[hum_col].mean(), 2))
c3.metric("Average CO₂ Level", round(filtered_data[gas_col].mean(), 2))

# -----------------------
# Temperature Plot with Alert Line
# -----------------------
temp_fig = px.line(
    filtered_data,
    x="Time",
    y=temp_col,
    title="Kiln Temperature Trend"
)

temp_fig.add_hline(
    y=TEMP_LIMIT,
    line_dash="dash",
    annotation_text="Temp Limit (450°C)"
)

st.plotly_chart(temp_fig, use_container_width=True)

# -----------------------
# Humidity Plot
# -----------------------
st.plotly_chart(
    px.line(filtered_data, x="Time", y=hum_col, title="Biomass Moisture Trend"),
    use_container_width=True
)

# -----------------------
# Gas Plot
# -----------------------
st.plotly_chart(
    px.line(filtered_data, x="Time", y=gas_col, title="CO₂ / Gas Trend"),
    use_container_width=True
)

# -----------------------
# Alert History from Excel
# -----------------------
st.subheader("⚠ Alert History")

if "Alert" in data.columns:
    alert_data = data[data["Alert"].notna()]

    if not alert_data.empty:
        st.dataframe(
            alert_data[["Time", "Alert", "Alert Value"]],
            use_container_width=True
        )
    else:
        st.info("No alerts recorded in the selected data.")
else:
    st.info("Alert column not found in the uploaded file.")

# -----------------------
# Raw Data
# -----------------------
with st.expander("View data with generated timestamps"):
    st.dataframe(filtered_data)
