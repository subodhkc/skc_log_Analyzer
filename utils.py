"""
utils.py - Shared helper utilities used throughout the SKC Log Reader app
"""

import re
import os
from datetime import datetime

# Converts Windows timestamp strings to datetime

def parse_timestamp(line):
    try:
        return datetime.strptime(line, "%Y-%m-%d %H:%M:%S")
    except:
        try:
            return datetime.strptime(line, "%m/%d/%Y %I:%M:%S %p")
        except:
            return datetime.now()

# Normalizes component names

def safe_component(comp):
    return comp.strip().lower().replace(" ", "_") if comp else "unknown"

# Generates filenames safely from titles

def safe_filename(name):
    return re.sub(r'[^\w\-_\.]', '_', name)

# Regex search across text using list of patterns

def matches_any(text, pattern_list):
    return any(re.search(pat, text, re.IGNORECASE) for pat in pattern_list)

# Save matplotlib chart from buffer to temp file for PDF use

def save_chart_to_png(buf, name):
    charts_dir = "charts"
    os.makedirs(charts_dir, exist_ok=True)
    path = os.path.join(charts_dir, f"{name}.png")
    with open(path, "wb") as f:
        f.write(buf.getbuffer())
    return path
