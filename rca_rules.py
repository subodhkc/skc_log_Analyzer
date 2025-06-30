# rca_rules.py - Pattern-based Root Cause Analysis logic engine for SKC Log Reader

from typing import List, Dict

def detect_os_incompatibility(events: List, metadata: Dict) -> str:
    os_build = (metadata.get("OS", "") + " " + metadata.get("Build", "")).lower()
    os_detected = "25h2" in os_build or any("25h2" in ev.message.lower() for ev in events)
    failure_related = any(
        "unsupported" in ev.message.lower()
        or "failed to install" in ev.message.lower()
        or "not compatible" in ev.message.lower()
        or "version mismatch" in ev.message.lower()
        or "install failed" in ev.message.lower()
        for ev in events
    )
    if os_detected and failure_related:
        return "Detected possible incompatibility between the build and Windows 25H2 target system."
    return ""

def detect_driver_conflict(events: List) -> str:
    conflict_keywords = [
        "driver conflict", "conflicting drivers", "driver failed",
        "unable to load driver", "driver installation failed",
        "missing driver"
    ]
    if any(any(kw in ev.message.lower() for kw in conflict_keywords) for ev in events):
        return "Detected possible driver conflict during installation."
    return ""

def detect_network_failure(events: List) -> str:
    if any(
        "network timeout" in ev.message.lower()
        or "connection failed" in ev.message.lower()
        or "unable to reach server" in ev.message.lower()
        or "dns error" in ev.message.lower()
        or "network unreachable" in ev.message.lower()
        for ev in events
    ):
        return "Network failure detected — logs indicate timeouts or server connectivity issues."
    return ""

def detect_corrupt_media(events: List) -> str:
    keywords = [
        "corrupt iso", "media unreadable", "checksum failed",
        "bad block", "unexpected eof", "invalid media",
        "file read error", "media error"
    ]
    if any(any(kw in ev.message.lower() for kw in keywords) for ev in events):
        return "Installation media appears to be corrupted or incomplete."
    return ""

def detect_permission_issue(events: List) -> str:
    if any(
        "access denied" in ev.message.lower()
        or "permission denied" in ev.message.lower()
        or "requires admin privileges" in ev.message.lower()
        or "not authorized" in ev.message.lower()
        or "elevation required" in ev.message.lower()
        for ev in events
    ):
        return "Permission issue detected — process may require administrative access."
    return ""

def detect_unsupported_hardware(events: List) -> str:
    if any(
        "unsupported hardware" in ev.message.lower()
        or "cpu not supported" in ev.message.lower()
        or "incompatible chipset" in ev.message.lower()
        or "hardware requirement not met" in ev.message.lower()
        or "unsupported platform" in ev.message.lower()
        for ev in events
    ):
        return "Detected unsupported or incompatible hardware."
    return ""

def get_all_rca_summaries(events: List, metadata: Dict) -> List[str]:
    summaries = [
        detect_os_incompatibility(events, metadata),
        detect_driver_conflict(events),
        detect_network_failure(events),
        detect_corrupt_media(events),
        detect_permission_issue(events),
        detect_unsupported_hardware(events)
    ]
    return [s for s in summaries if s]
