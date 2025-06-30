# ai_rca.py - Hybrid AI RCA using offline LLM and OpenAI fallback

from transformers import pipeline
import openai
import traceback
import logging

# ----- Internal Setup -----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AI_RCA")

# Local offline model (transformers)
offline_model = None
try:
    logger.info("Loading offline model (distilgpt2)...")
    offline_model = pipeline("text-generation", model="distilgpt2", model_kwargs={"pad_token_id": 50256})
except Exception as e:
    logger.warning(f"Failed to load offline model: {e}")

# ----- Helper Functions -----
def format_logs_for_ai(events, metadata=None, test_results=None):
    lines = []
    if metadata:
        lines.append("System Metadata:")
        for k, v in metadata.items():
            lines.append(f"- {k}: {v}")
        lines.append("")

    if test_results:
        lines.append("Test Plan Summary:")
        for result in test_results:
            step = result.get("Step", "")
            status = result.get("Status", "")
            actual = result.get("Actual Result", "")
            lines.append(f"- Step: {step}, Status: {status}, Observed: {actual}")
        lines.append("")

    lines.append("Error & Critical Events:")
    filtered = [ev for ev in events if ev.severity in ("ERROR", "CRITICAL")]
    for ev in filtered:
        ts = ev.timestamp.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ev.timestamp, "strftime") else str(ev.timestamp)
        lines.append(f"[{ts}] [{ev.severity}] [{ev.component}] {ev.message}")

    return "\n".join(lines)

def analyze_with_ai(events, metadata=None, test_results=None, api_key=None, offline=True):
    prompt = (
        "You are a senior QA systems expert. Analyze the following log extracts and provide a summary of any "
        "critical issues, root causes, and proposed remediations. Focus on install/configuration issues.\n\n"
    )
    log_text = format_logs_for_ai(events, metadata, test_results)
    safe_prompt = log_text[:1024]
    prompt += safe_prompt

    # ----- OFFLINE MODE -----
    if offline:
        if not offline_model:
            return "Offline model not available. Please install `transformers` and retry."
        logger.info("Running offline RCA model...")
        try:
            result = offline_model(safe_prompt, max_new_tokens=250)[0]["generated_text"]
            return result.split("\n", 1)[-1].strip()
        except Exception as e:
            logger.error(f"Offline model failed: {e}")
            return "Offline model failed. Try enabling OpenAI fallback if available."

    # ----- OPENAI MODE -----
    if api_key:
        try:
            openai.api_key = api_key
            logger.info("Using OpenAI for RCA...")
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                temperature=0.4,
                messages=[
                    {"role": "system", "content": "You are a helpful QA and RCA assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"OpenAI RCA failed: {traceback.format_exc()}")
            return f"OpenAI RCA failed: {e}"

    # ----- FAILOVER -----
    return "No valid AI engine configured. Please set an API key or enable offline LLM."

# For standalone testing only
if __name__ == "__main__":
    class DummyEvent:
        def __init__(self, ts, sev, comp, msg):
            self.timestamp = ts
            self.severity = sev
            self.component = comp
            self.message = msg

    dummy_logs = [
        DummyEvent("2025-06-30 10:00:00", "ERROR", "Installer", "Failed to initialize deployment."),
        DummyEvent("2025-06-30 10:01:00", "INFO", "Service", "Restarted successfully."),
        DummyEvent("2025-06-30 10:02:00", "CRITICAL", "Boot", "System halted due to invalid signature.")
    ]
    dummy_meta = {"OS": "Win25H2", "Build": "26000"}
    dummy_results = [{"Step": "Install BIOS", "Status": "Fail", "Actual Result": "BIOS not detected"}]
    print(analyze_with_ai(dummy_logs, dummy_meta, dummy_results, offline=True))
