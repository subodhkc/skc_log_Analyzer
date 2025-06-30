# app.py - Streamlit UI and orchestration for SKC Log Reader (Enhanced UX)

import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import streamlit as st
import pandas as pd
import zipfile, io
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Core Modules
import analysis
import redaction
import test_plan
import charts
import recommendations
import ai_rca
import report
import setup
import clustering_model
import decision_tree_model
import anomaly_svm
from rca_rules import get_all_rca_summaries

# App metadata
st.set_page_config(page_title="SKC Log Reader", layout="wide")

# --- Welcome Screen ---
if "show_welcome" not in st.session_state:
    st.session_state["show_welcome"] = True

if st.session_state["show_welcome"]:
    st.title("Welcome to SKC Log Reader")
    st.markdown("""
    ##  

    **This is a powerful diagnostic assistant for TPMs, QA engineers, and system integrators.  
    It helps analyze complex provisioning and deployment logs from BIOS updates, SoftPaq installations, Windows imaging, and Fusion agents.

    **No data ever leaves your system** without your explicit consent.

    ---
    ##  Features at a Glance

    -  **Multi-Log Ingestion**: Upload a ZIP of log files — the app extracts, parses, and organizes everything.
    -  **Root Cause Detection**: Timeline of events, error tagging, and test validation — all pre-AI.
    -  **Redaction Engine**: Automatically masks hostnames, serials, "HP" mentions, emails, IPs, etc.
    -  **Test Plan Validation**: Choose DASH or SoftPaq plans — or upload your own. Steps are mapped to log events with pass/fail reporting.
    -  **Smart Machine Learning Insights**:
        - **Clustering**: Groups log events by behavior (K-Means/DBSCAN).
        - **Severity Prediction**: Uses decision trees to identify critical failure paths.
        - **Anomaly Detection**: Linear SVM detects deviations in behavior vs. expected installs.
    -  **Optional AI RCA (Redacted + Secure)**:
        - Powered by OpenAI's GPT API (optional)
        - No data is stored or trained on externally
        - Provides RCA summary in plain English for faster triage
    -  **PDF Report Generation**:
        - Includes: System Info, Errors, Timeline, Test Validation, RCA
        - Embedded charts and summaries
    ---
    ##  Machine Learning Overview

    - **Clustering**: Groups similar event types for easier investigation.
    - **Decision Trees**: Predict impact severity from log patterns.
    - **SVM Anomaly Detection**: Flags unexpected sequences.

    ---
    ##  Security

    - Everything is processed **locally**
    - AI API is optional and **redacted**
    - Private API — **no data used for training**

    ---
    Click below to start:
    """)
    if st.button("Start Log Analysis"):
        st.session_state["show_welcome"] = False
        st.rerun()
    st.stop()

# --- Input Phase ---
st.title("SKC Log Reader")
user_name = st.text_input("Your Name", placeholder="Enter your full name", help="This will appear in your final report.")
app_name = st.text_input("Application Being Tested", placeholder="Enter the app (fuzzy match supported)", help="Used to focus log filtering and reporting.")

test_plan_options = setup.get_available_test_plans()
selected_plan = st.selectbox("Select Test Plan", options=test_plan_options + ["Upload Custom"], help="Choose an existing plan or upload your own.")
plan_data = None
if selected_plan == "Upload Custom":
    uploaded_plan = st.file_uploader("Upload your custom test plan (JSON)", type=["json"])
    if uploaded_plan:
        plan_data = setup.load_custom_test_plan(uploaded_plan)
else:
    plan_data = setup.get_test_plan_by_name(selected_plan)

uploaded_file = st.file_uploader("Upload ZIP of logs", type=["zip"])
if uploaded_file:
    with st.spinner("Parsing log files..."):
        zip_bytes = uploaded_file.read()
        events, metadata = analysis.parse_zip(BytesIO(zip_bytes))

    patterns = setup.get_redaction_patterns()
    redactor = redaction.Redactor(patterns)

    with st.spinner("Redacting sensitive information..."):
        redacted_events = redactor.redact_events(events)
        redacted_metadata = redactor.redact_metadata(metadata)

    st.subheader("Log Timeline")
    components = sorted(set(ev.component for ev in redacted_events))
    selected = st.selectbox("Filter by Component", ["All"] + components, help="Narrow down logs to specific components.")
    to_show = redacted_events if selected == "All" else [ev for ev in redacted_events if ev.component == selected]
    timeline_df = pd.DataFrame([{ "Timestamp": str(ev.timestamp), "Component": ev.component, "Severity": ev.severity, "Message": ev.message } for ev in to_show])
    st.dataframe(timeline_df)

    st.subheader("Errors and Warnings")
    issues = [ev for ev in redacted_events if ev.severity in ["ERROR", "CRITICAL", "WARNING"]]
    if issues:
        issue_df = pd.DataFrame([{ "Timestamp": str(ev.timestamp), "Component": ev.component, "Severity": ev.severity, "Message": ev.message } for ev in issues])
        st.dataframe(issue_df.style.map(lambda x: 'background-color: #FFDDDD', subset=['Severity']))
    else:
        st.success("No warnings or errors found.")

    st.subheader(" Test Plan Validation")
    test_results = test_plan.validate_plan(plan_data, events) if plan_data else []
    if test_results:
        st.table(pd.DataFrame(test_results))
    else:
        st.info("No test plan results available.")

    st.subheader(" Recommendations")
    recs = recommendations.generate_recommendations(events)
    if recs:
        for rec in recs:
            if isinstance(rec, dict):
                st.markdown(f"- **{rec.get('severity')}** - {rec.get('message')} _(Category: {rec.get('category')})_")
    else:
        st.write("No issues detected.")

    st.subheader("Root Cause Summary (Logic-Based)")
    rca_summaries = get_all_rca_summaries(redacted_events, redacted_metadata)
    if rca_summaries:
        for summary in rca_summaries:
            st.markdown(f"- {summary}")
    else:
        st.write("No root cause identified based on known patterns.")

    st.subheader(" Machine Learning Insights")
    st.markdown("""
    SKC Log Reader uses machine learning to help uncover hidden patterns:

    **1. Clustering (K-Means or DBSCAN)**  
    Groups similar log events together.

    **2. Severity Prediction (Decision Trees)**  
    Shows how errors evolve into critical failures.

    **3. Anomaly Detection (SVM)**  
    Flags events that deviate from the system's normal behavior.
    """)

    if st.checkbox("Run Clustering"):
        with st.spinner("Clustering events..."):
            cluster_fig = clustering_model.cluster_events(events)
            if cluster_fig:
                st.pyplot(cluster_fig)
                st.markdown("""
                ** How to Read:**
                - Each dot is a log event.
                - Colors represent clusters (behavioral groups).
                - Useful for spotting correlated failures or repeated issues.
                """)

    if st.checkbox("Run Severity Predictor"):
        with st.spinner("Analyzing severity predictions..."):
            severity_fig = decision_tree_model.analyze_event_severity(events)
            if severity_fig:
                st.pyplot(severity_fig)
                st.markdown("""
                **How to Read:**
                - This is a decision tree model.
                - Each box shows a split rule (e.g., component type, error count).
                - Leaves show predicted severity (Normal / Warning / Critical).
                - Use it to trace how certain errors escalate.
                """)

    if st.checkbox("Run Anomaly Detector"):
        with st.spinner("Detecting anomalies using SVM..."):
            anomaly_fig = anomaly_svm.detect_anomalies(events)
            if anomaly_fig:
                st.pyplot(anomaly_fig)
                st.markdown("""
                ** How to Read:**
                - X-axis: Timestamp  
                - Y-axis: Component Index (hashed)
                - Blue = Normal logs  
                - Red = Anomalies  
                - Helps identify unusual log bursts, delays, or unexpected activity.
                """)

    st.subheader(" Additional Visual Insights")
    if st.checkbox("Show Severity Distribution"):
        st.pyplot(charts.plot_severity_distribution(redacted_events))

    if st.checkbox("Show Top Error Components"):
        fig = charts.plot_top_error_components(redacted_events)
        if fig:
            st.pyplot(fig)

    if st.checkbox("Show Event Frequency by Hour"):
        st.pyplot(charts.plot_event_frequency_by_hour(redacted_events))

    st.subheader("📄 Generate Report (Choose AI Option)")

    if st.button("Download PDF Report (No AI)"):
        pdf = report.generate_pdf(redacted_events, redacted_metadata, test_results, recs, user_name=user_name, app_name=app_name, ai_summary=None)
        st.download_button("Download PDF (No AI)", data=pdf, file_name="SKC_Report_NoAI.pdf", mime="application/pdf")

    if st.button("Download PDF Report with Local AI"):
        with st.spinner("Generating summary using offline model..."):
            ai_summary = ai_rca.analyze_with_ai(redacted_events, redacted_metadata, test_results, offline=True)
            pdf = report.generate_pdf(redacted_events, redacted_metadata, test_results, recs, user_name=user_name, app_name=app_name, ai_summary=ai_summary)
            st.download_button("Download PDF (Local AI)", data=pdf, file_name="SKC_Report_LocalAI.pdf", mime="application/pdf")

    if st.button("Download PDF Report with OpenAI"):
        with st.spinner("Generating summary using OpenAI API..."):
            api_key = os.getenv("OPENAI_API_KEY")
            ai_summary = ai_rca.analyze_with_ai(redacted_events, redacted_metadata, test_results, api_key=api_key, offline=False)
            pdf = report.generate_pdf(redacted_events, redacted_metadata, test_results, recs, user_name=user_name, app_name=app_name, ai_summary=ai_summary)
            st.download_button("Download PDF (OpenAI)", data=pdf, file_name="SKC_Report_OpenAI.pdf", mime="application/pdf")

    st.text_area("Text Summary", report.generate_text_summary(redacted_events, redacted_metadata, test_results, recs), height=200)

    st.markdown("<div style='text-align:right; font-size:12px; color:gray;'>Opensource Model Dev by Subodh Kc</div>", unsafe_allow_html=True)
