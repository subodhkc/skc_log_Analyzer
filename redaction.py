"""
redaction.py - Redaction engine for masking sensitive info from logs
"""

import re
import zipfile
from io import BytesIO
from analysis import InstallEvent

class Redactor:
    def __init__(self, patterns):
        self.patterns = patterns

    def redact_string(self, text):
        """Apply all redaction patterns to a single string."""
        if not isinstance(text, str):
            return text
        for pattern in self.patterns:
            if isinstance(pattern, dict) and "pattern" in pattern and "replacement" in pattern:
                text = re.sub(pattern["pattern"], pattern["replacement"], text, flags=re.IGNORECASE)
        return text

    def redact_events(self, events):
        """Apply redaction to all InstallEvent objects."""
        redacted = []
        for ev in events:
            redacted.append(InstallEvent(
                timestamp=ev.timestamp,
                component=self.redact_string(ev.component),
                message=self.redact_string(ev.message),
                severity=ev.severity
            ))
        return redacted

    def redact_metadata(self, metadata):
        """Redact fields in system metadata."""
        redacted_meta = {}
        for k, v in metadata.items():
            redacted_meta[k] = self.redact_string(str(v))
        return redacted_meta

    def redact_text(self, text):
        """Redact a raw log file content (string)."""
        return self.redact_string(text)


def get_redacted_zip(zipfile_obj, redactor):
    """Redacts log/txt files inside a ZIP and returns a new redacted ZIP as BytesIO."""
    redacted_zip = BytesIO()
    with zipfile.ZipFile(redacted_zip, mode="w") as zout:
        with zipfile.ZipFile(zipfile_obj) as zin:
            for file in zin.namelist():
                if file.endswith(".log") or file.endswith(".txt"):
                    with zin.open(file) as f:
                        try:
                            raw = f.read().decode("utf-8", errors="ignore")
                            clean = redactor.redact_string(raw)
                            zout.writestr(file, clean)
                        except Exception:
                            continue
    redacted_zip.seek(0)
    return redacted_zip
