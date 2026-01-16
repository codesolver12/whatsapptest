import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

st.set_page_config(page_title="Kiln Monitoring Dashboard", layout="wide")

st.title("Kiln IoT Monitoring – Historical Data")

st.write("Upload the sensor data file exported from the IoT system.")

# -----------------------
# File Upload
# -----------------------
uploaded_file = st.file_uploader(
    "Upload Excel file",
    type=["xlsx"]
)

if uploaded_file is not None:

    # Read excel file
    data = pd.read_excel(uploaded_file)

    # Convert timestamp column
    data["timestamp"] = pd.to_datetime(data["timestamp"])

    # Sort data just in case
    data = data.sort_values("timestamp")

    # -----------------------
    # Time Filter
    # -----------------------
    st.sidebar.header("Data Filter")

    minutes = st.sidebar.selectbox(
        "Show data for last",
        [30, 60, 90, 120],
        index=0
    )

    latest_time = data["timestamp"].max()
    start_time = latest_time - timedelta(minutes=minutes)

    filtered_data = data[data["timestamp"] >= start_time]

    # -----------------------
    # Alert Logic
    # -----------------------
    if filtered_data["kiln_temp"].max() > 450:
        st.warning("⚠ Warning: Kiln temperature exceeded safe limit (450°C)")
    else:
        st.success("Kiln temperature is within safe range")

    # -----------------------
    # Summary Values
    # -----------------------
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Max Temperature (°C)",
        round(filtered_data["kiln_temp"].max(), 1)
    )

    col2.metric(
        "Average Humidity (%)",
        round(filtered_data["humidity"].mean(), 1)
    )

    col3.metric(
        "Average Gas Level (ppm)",
        round(filtered_data["gas"].mean(), 1)
    )

    # -----------------------
    # Temperature Plot
    # -----------------------
    temp_plot = px.line(
        filtered_data,
        x="timestamp",
        y="kiln_temp",
        title="Kiln Temperature Trend"
    )
    st.plotly_chart(temp_plot, use_container_width=True)

    # -----------------------
    # Humidity Plot
    # -----------------------
    humidity_plot = px.line(
        filtered_data,
        x="timestamp",
        y="humidity",
        title="Biomass Humidity Trend"
    )
    st.plotly_chart(humidity_plot, use_container_width=True)

    # -----------------------
    # Gas Plot
    # -----------------------
    gas_plot = px.line(
        filtered_data,
        x="timestamp",
        y="gas",
        title="Smoke / Gas Level Trend"
    )
    st.plotly_chart(gas_plot, use_container_width=True)

    # -----------------------
    # Raw Data View
    # -----------------------
    with st.expander("View filtered sensor data"):
        st.dataframe(filtered_data)

else:
    st.info("Please upload an Excel file to view the dashboard.")
