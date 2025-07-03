# SKC Log Reader

SKC Log Reader is a modular log analysis tool built using Python + Streamlit. Designed for TPMs and QA engineers, it helps identify root causes behind provisioning failures (BIOS, SoftPaqs, Fusion, OS mismatches, etc.) across Windows-based systems.

“This tool is developed and maintained by Subodh Kc, It does not store or access internal data unless shared by the user. Participation is voluntary and exploratory.”

## 🔍 Key Features
- Upload ZIP logs and parse events across multiple files
- Structured Pre-AI RCA with error detection and rule-based recommendations
- Interactive timeline, test plan validation, log filtering
- Visuals via charts, clustering, decision trees, and anomaly detection (SVM)
- Redaction engine with built-in patterns for PII
- PDF report export (with visual summaries)
- Optional LLM-powered analysis (offline or via OpenAI API)

## 🧰 Setup Instructions

### 1. Clone and Setup
```bash
git clone https://github.com/your-repo/skc-log-reader.git
cd skc-log-reader
pip install -r requirements.txt
```

### 2. Folder Structure
```
├── app.py
├── analysis.py
├── redaction.py
├── test_plan.py
├── recommendations.py
├── ai_rca.py
├── report.py
├── setup.py
├── clustering_model.py
├── decision_tree_model.py
├── anomaly_svm.py
├── utils.py
├── requirements.txt
├── plans/
│   ├── dash_test_plan.json
│   └── softpaq_test_plan.json
├── config/
│   └── redact.json  (optional)
```

### 3. Run Locally
```bash
streamlit run app.py
```

## 🔐 Security Notes
- API keys are embedded securely in `setup.py` for private use only
- Only **redacted** logs are sent to LLMs
- All log parsing and visualization happen **locally**

## 📦 Deployment
You can host this on:
- **Streamlit Cloud** (recommended for light usage)
- **GitHub Pages** (for static version with limited features)
- **Internal Server** for full control and offline models

## 🧠 LLM Support
- Offline model (e.g. transformers-based): Used for quick diagnostics
- OpenAI API: Enabled optionally via checkbox. Uses redacted logs only

---




## Credits

Built by Subodh Kc  
Powered by Python, Streamlit, and open-source intelligence

Footer in report: "Opensource Model Dev by Subodh Kc"
"# skc_log_Analyzer" 
