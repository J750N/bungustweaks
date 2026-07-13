"""
Every tweak's revert command already restores the Windows default, and its
apply command already sets the recommended/optimized value - so we can
derive readable "Default" / "Recommended" labels straight from the real
commands instead of hand-annotating every tweak (which would drift out of
sync over time).
"""

import re

SC_START_LABELS = {
    "auto": "Automatic",
    "demand": "Manual",
    "disabled": "Disabled",
    "delayed-auto": "Automatic (Delayed)",
}


def _describe(cmd: str) -> str:
    cmd_lower = cmd.lower()

    if "reg delete" in cmd_lower:
        return "key removed"

    if "reg add" in cmd_lower:
        m = re.search(r"/d\s+\"?([^\"/\s]+)\"?", cmd, re.IGNORECASE)
        if m:
            return m.group(1)
        return "custom value"

    if "sc config" in cmd_lower:
        m = re.search(r"start=\s*(\S+)", cmd, re.IGNORECASE)
        if m:
            return SC_START_LABELS.get(m.group(1).lower(), m.group(1))
        return "changed"

    if "powercfg -h off" in cmd_lower:
        return "Off"
    if "powercfg -h on" in cmd_lower:
        return "On"
    if "powercfg" in cmd_lower and "setacvalueindex" in cmd_lower:
        m = re.search(r"(\d+)\s*$", cmd.strip())
        if m:
            return f"{m.group(1)}%" if int(m.group(1)) <= 100 else m.group(1)
    if "setmppreference" in cmd_lower:
        return "Off" if "$true" in cmd_lower else "On"

    return "changed"


def get_default_and_recommended(tweak: dict):
    """Returns (default_value_str, recommended_value_str)."""
    default = _describe(tweak["revert"][0]) if tweak.get("revert") else "Windows default"
    recommended = _describe(tweak["apply"][0]) if tweak.get("apply") else "tweaked"
    return default, recommended
