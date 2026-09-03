# -*- coding: utf-8 -*-

# Members 2, 3, 4, 5 Lead: Streamlit Web UI & Parser Engine
# Member 1 Lead: Real-time Log Generator
import time
import random
from datetime import datetime

LOG_FILE = "live_server.log"

IP_POOL = ["192.168.1.10", "192.168.1.11", "192.168.1.12", "192.168.1.13", "10.0.0.5"]
ENDPOINTS = ["/index.html", "/login", "/dashboard", "/api/v1/resource", "/contact"]
STATUS_CODES = [200, 200, 200, 304, 401, 404, 500]

def generate_log_line():
    ip = random.choice(IP_POOL)
    timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")
    endpoint = random.choice(ENDPOINTS)
    method = "POST" if endpoint == "/login" else "GET"
    status = random.choice(STATUS_CODES)
    size = random.randint(200, 5000)
    
    return f'{ip} - - [{timestamp}] "{method} {endpoint} HTTP/1.1" {status} {size}\n'

if __name__ == "__main__":
    print(f"Starting real-time log generation in '{LOG_FILE}'... Press Ctrl+C to stop.")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        while True:
            line = generate_log_line()
            f.write(line)
            f.flush()  # Force write to disk immediately
            time.sleep(1)