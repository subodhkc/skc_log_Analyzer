"""
analysis.py - Ingests logs, extracts events, builds timeline and metadata
"""

import zipfile
import os
import re
import tempfile
from datetime import datetime
from dateutil import parser as dt_parser

# Define a class to structure log events
class InstallEvent:
    def __init__(self, timestamp, component, message, severity="INFO"):
        self.timestamp = timestamp
        self.component = component
        self.message = message
        self.severity = severity

    def __repr__(self):
        return f"[{self.timestamp}] ({self.severity}) {self.component}: {self.message}"

# Utility: guess severity from message content
def guess_severity(msg):
    msg = msg.lower()
    if "error" in msg or "failed" in msg:
        return "ERROR"
    elif "critical" in msg or "fatal" in msg:
        return "CRITICAL"
    elif "warning" in msg or "deprecated" in msg:
        return "WARNING"
    else:
        return "INFO"

# Utility: extract system metadata from logs
def extract_metadata(all_logs):
    metadata = {
        "OS Version": "Unknown",
        "BIOS Version": "Unknown",
        "System Model": "Unknown"
    }

    for fname, lines in all_logs.items():
        for line in lines:
            if "OS Version" in line:
                metadata["OS Version"] = line.split(":")[-1].strip()
            if "BIOS Version" in line:
                metadata["BIOS Version"] = line.split(":")[-1].strip()
            if "System Model" in line or "Product Name" in line:
                metadata["System Model"] = line.split(":")[-1].strip()

    return metadata

# Main parser function
def parse_zip(zip_file_obj):
    all_logs = {}
    events = []

    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_file_obj, 'r') as archive:
            archive.extractall(tmpdir)

            for root, dirs, files in os.walk(tmpdir):
                for fname in files:
                    full_path = os.path.join(root, fname)
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            all_logs[fname] = lines
                    except Exception as e:
                        continue

    for fname, lines in all_logs.items():
        for line in lines:
            try:
                # Try to extract timestamp from beginning of line
                ts_match = re.match(r"^\[?(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})", line)
                ts = dt_parser.parse(ts_match.group(1)) if ts_match else datetime.now()

                component = os.path.splitext(fname)[0]
                msg = line.strip()
                severity = guess_severity(msg)

                events.append(InstallEvent(ts, component, msg, severity))
            except Exception:
                continue

    events.sort(key=lambda x: x.timestamp)
    metadata = extract_metadata(all_logs)

    return events, metadata
