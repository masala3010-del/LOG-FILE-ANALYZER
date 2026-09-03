import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Real-Time Log Analyzer", layout="wide")
st.title("⚡ Real-Time Server Log Analyzer")

LOG_FILE = "live_server.log"

def generate_sample_file(file_path):
    """Generates initial sample data so the cloud app never opens empty."""
    sample_content = """192.168.1.10 - - [10/May/2026:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326
192.168.1.11 - - [10/May/2026:13:55:37 +0000] "POST /login HTTP/1.1" 401 142
192.168.1.10 - - [10/May/2026:13:55:38 +0000] "GET /about.html HTTP/1.1" 200 4500
192.168.1.12 - - [10/May/2026:13:55:39 +0000] "GET /images/logo.png HTTP/1.1" 304 0
192.168.1.11 - - [10/May/2026:13:55:40 +0000] "POST /login HTTP/1.1" 200 1500
192.168.1.13 - - [10/May/2026:13:55:41 +0000] "GET /dashboard HTTP/1.1" 404 512
192.168.1.10 - - [10/May/2026:13:55:42 +0000] "GET /index.html HTTP/1.1" 200 2326
192.168.1.14 - - [10/May/2026:13:55:43 +0000] "GET /contact.html HTTP/1.1" 500 340
192.168.1.12 - - [10/May/2026:13:55:44 +0000] "GET /style.css HTTP/1.1" 200 1200
192.168.1.11 - - [10/May/2026:13:55:45 +0000] "GET /index.html HTTP/1.1" 200 2326"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(sample_content)

# File uploader in sidebar for user custom logs
st.sidebar.header("Log Source")
uploaded_file = st.sidebar.file_uploader("Upload custom log file", type=["txt", "log"])

def parse_logs(file_path=None, uploaded_stream=None):
    log_pattern = re.compile(
        r'^(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[\w:/]+ \+\d{4})\] '
        r'"(?P<request>[^"]+)" (?P<status>\d{3}) (?P<bytes>\d+|-)'
    )
    parsed_data = []

    lines = []
    if uploaded_stream:
        lines = [line.decode("utf-8") for line in uploaded_stream.readlines()]
    elif file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    for line in lines:
        match = log_pattern.match(line)
        if match:
            data = match.groupdict()
            data['status'] = int(data['status'])
            data['bytes'] = int(data['bytes']) if data['bytes'] != '-' else 0
            parsed_data.append(data)

    return pd.DataFrame(parsed_data)

# Auto-generate sample file if no local file exists
if not os.path.exists(LOG_FILE) and uploaded_file is None:
    generate_sample_file(LOG_FILE)

df = parse_logs(LOG_FILE, uploaded_file)

if df.empty:
    st.warning("No log entries found.")
else:
    # Key Metrics
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Requests", len(df))
    kpi2.metric("Unique Client IPs", df['ip'].nunique())
    kpi3.metric("HTTP 500 Errors", len(df[df['status'] == 500]))
    kpi4.metric("Bandwidth Used", f"{df['bytes'].sum() / 1024:.2f} KB")

    st.markdown("---")

    # Visual Charts
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

    st.markdown("---")
    st.subheader("Parsed Log Data Table")
    st.dataframe(df, use_container_width=True)

    # Report Export Option
    st.markdown("---")
    st.subheader("💾 Export Report")
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Parsed Logs as CSV",
        data=csv_data,
        file_name="parsed_log_report.csv",
        mime="text/csv"
    )
