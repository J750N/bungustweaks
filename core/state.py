"""
Small JSON-backed store so the app remembers which tweaks are already
applied when it's reopened (so toggles show the correct on/off state).
"""

import json
import os

APP_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "BungusTweaks")
STATE_FILE = os.path.join(APP_DIR, "state.json")


def _ensure_dir():
    os.makedirs(APP_DIR, exist_ok=True)


def load_state() -> dict:
    _ensure_dir()
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state: dict):
    _ensure_dir()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def set_tweak_applied(key: str, applied: bool):
    state = load_state()
    state[key] = applied
    save_state(state)


def is_tweak_applied(key: str) -> bool:
    return load_state().get(key, False)
