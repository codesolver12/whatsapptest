import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
import requests
from PIL import Image
import io
import base64
from typing import Dict, List

# Page configuration
st.set_page_config(
    page_title="WhatsApp Campaign Bot",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid #1f77b4;
}
.status-badge {
    padding: 0.2rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: bold;
}
.status-new { background: #e3f2fd; color: #1976d2; }
.status-sent { background: #fff3e0; color: #f57c00; }
.status-catalogue { background: #f3e5f5; color: #7b1fa2; }
.status-selected { background: #e8f5e8; color: #388e3c; }
.success-box {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'leads_data' not in st.session_state:
    st.session_state.leads_data = [
        {
            "name": "John Smith",
            "mobile": "+1-234-567-8901",
            "social_media": "@johnsmith",
            "status": "New",
            "date_added": "2024-10-14",
            "last_activity": "2024-10-14 10:30"
        },
        {
            "name": "Sarah Johnson",
            "mobile": "+1-234-567-8902",
            "social_media": "@sarahjohnson",
            "status": "Welcome Sent",
            "date_added": "2024-10-14",
            "last_activity": "2024-10-14 10:45"
        },
        {
            "name": "Mike Davis",
            "mobile": "+1-234-567-8903",
            "social_media": "@mikedavis",
            "status": "Catalogue Sent",
            "date_added": "2024-10-14",
            "last_activity": "2024-10-14 11:10"
        },
        {
            "name": "Emily Wilson",
            "mobile": "+1-234-567-8904",
            "social_media": "@emilywilson",
            "status": "Product Selected",
            "date_added": "2024-10-14",
            "last_activity": "2024-10-14 11:25"
        }
    ]

# Sidebar configuration
st.sidebar.title("🔧 Configuration")

# WhatsApp API Settings
st.sidebar.subheader("📱 WhatsApp API")
whatsapp_token = st.sidebar.text_input("Access Token", type="password", help="Your WhatsApp Business API token")
whatsapp_phone_id = st.sidebar.text_input("Phone Number ID", help="Your WhatsApp Business phone number ID")
webhook_url = st.sidebar.text_input("Webhook URL", help="URL to receive webhook notifications")

# Google Sheets Integration
st.sidebar.subheader("📊 Google Sheets")
google_sheets_url = st.sidebar.text_input(
    "Google Sheets URL", 
    help="Paste your Google Sheets sharing link here",
    placeholder="https://docs.google.com/spreadsheets/d/your-sheet-id/edit"
)

if google_sheets_url:
    st.sidebar.success("✅ Google Sheets Connected")
    if st.sidebar.button("📥 Import Leads from Sheets"):
        st.sidebar.info("📊 Importing leads... (This would connect to your actual Google Sheets)")
else:
    st.sidebar.warning("⚠️ Google Sheets Not Connected")

# Main app header
st.markdown("<h1 class='main-header'>📱 WhatsApp Campaign Bot Dashboard</h1>", unsafe_allow_html=True)

# Navigation tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Dashboard", 
    "👥 Leads", 
    "🛍️ Products", 
    "💬 Templates", 
    "📈 Analytics", 
    "⚙️ Settings",
    "🔄 Automation"
])

with tab1:
    st.header("📊 Campaign Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Leads", 
            "1,247",
            delta="+50 this week"
        )
    
    with col2:
        st.metric(
            "Messages Sent", 
            "3,841",
            delta="+156 today"
        )
    
    with col3:
        st.metric(
            "Responses", 
            "892",
            delta="+23 today"
        )
    
    with col4:
        st.metric(
            "Conversion Rate", 
            "17.5%",
            delta="+2.1%"
        )
    
    # Campaign controls
    st.subheader("🎮 Campaign Controls")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Start Campaign", type="primary"):
            st.success("✅ Campaign started successfully!")
    
    with col2:
        if st.button("⏸️ Pause Campaign"):
            st.warning("⏸️ Campaign paused")
    
    with col3:
        if st.button("🧪 Send Test Message"):
            st.info("📱 Test message sent!")

# Rest of the tabs would continue...
# This is a truncated version for the demo
