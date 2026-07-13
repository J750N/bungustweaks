"""
Tracks every tweak/service apply/revert so the History page can show what
changed and when, and re-run the opposite command if the person wants to
undo something from days ago (not just this session).
"""

import json
import os
import datetime
from core.state import APP_DIR

HISTORY_FILE = os.path.join(APP_DIR, "history.json")
MAX_ENTRIES = 300


def _ensure_dir():
    os.makedirs(APP_DIR, exist_ok=True)


def load_history() -> list:
    _ensure_dir()
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def log_change(key: str, name: str, action: str, category: str, default_value: str, new_value: str):
    """action is 'applied' or 'reverted'."""
    _ensure_dir()
    history = load_history()
    history.insert(0, {
        "key": key,
        "name": name,
        "action": action,
        "category": category,
        "default_value": default_value,
        "new_value": new_value,
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
    })
    history = history[:MAX_ENTRIES]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def clear_history():
    _ensure_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)


def format_timestamp(iso_string: str) -> str:
    try:
        dt = datetime.datetime.fromisoformat(iso_string)
        return dt.strftime("%b %d, %I:%M %p")
    except Exception:
        return iso_string
