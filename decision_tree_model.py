"""
decision_tree_model.py - Uses Decision Trees to predict severity of events
"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
from utils import safe_component

def analyze_event_severity(events):
    if not events:
        return None

    # Prepare DataFrame
    df = pd.DataFrame([{
        "timestamp": (ev.timestamp - datetime(1970, 1, 1)).total_seconds() if hasattr(ev.timestamp, 'timestamp') else 0,
        "component": safe_component(ev.component),
        "severity": ev.severity
    } for ev in events])

    # Encode categorical features
    le_comp = LabelEncoder()
    le_sev = LabelEncoder()
    df["component"] = le_comp.fit_transform(df["component"])
    df["severity"] = le_sev.fit_transform(df["severity"])

    X = df[["timestamp", "component"]]
    y = df["severity"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    # Train Decision Tree model
    tree = DecisionTreeClassifier(max_depth=4)
    tree.fit(X_train, y_train)

    # Plot decision tree
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_tree(tree, feature_names=["timestamp", "component"], class_names=le_sev.classes_, filled=True, ax=ax)
    ax.set_title("Decision Tree - Severity Prediction")

    return fig  # Return the matplotlib figure
