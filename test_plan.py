"""
test_plan.py - Validates parsed logs against structured test plans (JSON/YAML)
"""

import json
import yaml
import os

def load_test_plan(path):
    """
    Loads a test plan from a .json or .yaml file.
    """
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            if path.endswith(".yaml") or path.endswith(".yml"):
                return yaml.safe_load(f)
            else:
                return json.load(f)
    except Exception as e:
        print(f"[Test Plan] Failed to load: {e}")
        return None

def validate_plan(plan, events):
    """
    Matches each test plan step to actual log events.
    Returns a list of dicts with Step, Action, Expected Result, Status
    """
    results = []

    if not plan or not isinstance(plan, list):
        return results

    for idx, step in enumerate(plan):
        step_text = step.get("Step Action") or step.get("[HPPM] Image System - DASH") or ""
        expected = step.get("Expected Result") or step.get("") or ""
        found = False

        for ev in events:
            if step_text and step_text.lower() in ev.message.lower():
                found = True
                break

        results.append({
            "Step": idx + 1,
            "Step Action": step_text.strip(),
            "Expected Result": expected.strip(),
            "Status": "Pass" if found else "Fail"
        })

    return results
