"""
anomaly_svm.py - Uses Linear SVM to detect anomalous log patterns
"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from utils import safe_component

def detect_anomalies(events):
    if not events or len(events) < 10:
        return None

    # Transform logs into a numerical DataFrame
    df = pd.DataFrame([{
        "timestamp": (ev.timestamp - datetime(1970, 1, 1)).total_seconds() if hasattr(ev.timestamp, 'timestamp') else 0,
        "component": hash(safe_component(ev.component)) % 1000,
        "severity": 0 if ev.severity == "INFO" else 1 if ev.severity == "WARNING" else 2 if ev.severity == "ERROR" else 3
    } for ev in events])

    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)

    # Train SVM
    clf = svm.OneClassSVM(nu=0.05, kernel="rbf", gamma='scale')
    preds = clf.fit_predict(X_scaled)

    df["outlier"] = preds

    # Visualize anomalies
    fig, ax = plt.subplots(figsize=(10, 5))
    inliers = df[df['outlier'] == 1]
    outliers = df[df['outlier'] == -1]

    ax.scatter(inliers['timestamp'], inliers['component'], c='blue', label='Normal', alpha=0.6)
    ax.scatter(outliers['timestamp'], outliers['component'], c='red', label='Anomaly', alpha=0.8)

    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Component Index")
    ax.set_title("SVM Anomaly Detection on Logs")
    ax.legend()
    fig.tight_layout()

    return fig  # Return the matplotlib figure object
