# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 14:32:36 2026

@author: khus2
"""

# Members 2, 3, 4, 5 Lead: Streamlit Web UI & Parser Engine
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Page setup
st.set_page_config(page_title="Real-Time Log Analyzer", layout="wide")
st.title("⚡ Real-Time Server Log Analyzer")

# Auto-refresh page every 2000 milliseconds (2 seconds)
st_autorefresh(interval=2000, key="log_monitor_refresh")

LOG_FILE = "live_server.log"

def parse_logs(file_path):
    log_pattern = re.compile(
        r'^(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[\w:/]+ \+\d{4})\] '
        r'"(?P<request>[^"]+)" (?P<status>\d{3}) (?P<bytes>\d+|-)'
    )
    parsed_data = []
    
    if not os.path.exists(file_path):
        return pd.DataFrame()

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = log_pattern.match(line)
            if match:
                data = match.groupdict()
                data['status'] = int(data['status'])
                data['bytes'] = int(data['bytes']) if data['bytes'] != '-' else 0
                parsed_data.append(data)
                
    return pd.DataFrame(parsed_data)

# Process Logs
df = parse_logs(LOG_FILE)

if df.empty:
    st.warning("Waiting for live log data... Ensure 'log_generator.py' is running.")
else:
    # Top KPI Metrics Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Requests", len(df))
    kpi2.metric("Unique Client IPs", df['ip'].nunique())
    kpi3.metric("HTTP 500 Errors", len(df[df['status'] == 500]))
    kpi4.metric("Bandwidth Used", f"{df['bytes'].sum() / 1024:.2f} KB")

    st.markdown("---")

    # Real-time Visualizations
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("HTTP Response Status Codes")
        fig1, ax1 = plt.subplots(figsize=(5, 3.5))
        status_counts = df['status'].value_counts()
        ax1.bar(status_counts.index.astype(str), status_counts.values, color='teal')
        ax1.set_xlabel("Status Code")
        ax1.set_ylabel("Frequency")
        st.pyplot(fig1)

    with chart_col2:
        st.subheader("Traffic Distribution by IP")
        fig2, ax2 = plt.subplots(figsize=(5, 3.5))
        ip_counts = df['ip'].value_counts()
        ax2.pie(ip_counts.values, labels=ip_counts.index, autopct='%1.1f%%', startangle=90)
        st.pyplot(fig2)

    # Real-Time Data Stream Table
    st.markdown("---")
    st.subheader("Recent Activity Stream (Latest 10 Logs)")
    st.dataframe(df.tail(10).iloc[::-1], use_container_width=True)
    # Add this inside app.py after the parsed dataframe (df) is generated

st.markdown("---")
st.subheader("💾 Export Report")

# Convert DataFrame to CSV format for download
csv_data = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download Parsed Logs as CSV",
    data=csv_data,
    file_name="parsed_log_report.csv",
    mime="text/csv",
    key="download-csv"
)