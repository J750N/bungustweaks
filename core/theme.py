"""
Theme manager. Each preset now controls both the accent gradient AND the
background palette (sidebar / content / card), so "dark theme" really means
a different dark palette, not just a different accent color.

Changing the theme is saved to state.json; picking it up fully requires an
app restart (kept simple on purpose - avoids live-restyling every widget).
"""

from core import state

PRESETS = {
    "Violet Frost": {
        "accent": "#8B5CF6", "accent2": "#38BDF8",
        "bg_sidebar": "#141416", "bg_content": "#0E0E10", "bg_card": "#1C1C1F",
    },
    "Cyber Blue": {
        "accent": "#38BDF8", "accent2": "#8B5CF6",
        "bg_sidebar": "#141416", "bg_content": "#0E0E10", "bg_card": "#1C1C1F",
    },
    "Crimson Rush": {
        "accent": "#EF4444", "accent2": "#F59E0B",
        "bg_sidebar": "#161213", "bg_content": "#100D0E", "bg_card": "#1F1B1C",
    },
    "Emerald Node": {
        "accent": "#22C55E", "accent2": "#38BDF8",
        "bg_sidebar": "#111614", "bg_content": "#0C100E", "bg_card": "#1A211E",
    },
    "Neon Magenta": {
        "accent": "#EC4899", "accent2": "#8B5CF6",
        "bg_sidebar": "#160F16", "bg_content": "#0F0A10", "bg_card": "#211A22",
    },
    "OLED Black": {
        "accent": "#8B5CF6", "accent2": "#38BDF8",
        "bg_sidebar": "#000000", "bg_content": "#000000", "bg_card": "#0A0A0A",
    },
    "Dracula": {
        "accent": "#BD93F9", "accent2": "#FF79C6",
        "bg_sidebar": "#1E1F29", "bg_content": "#282A36", "bg_card": "#343746",
    },
    "Nord Frost": {
        "accent": "#88C0D0", "accent2": "#5E81AC",
        "bg_sidebar": "#2E3440", "bg_content": "#3B4252", "bg_card": "#434C5E",
    },
    "Midnight Purple": {
        "accent": "#A78BFA", "accent2": "#7C3AED",
        "bg_sidebar": "#0F0B1A", "bg_content": "#150F24", "bg_card": "#1E1533",
    },
    "Midnight Blue": {
        "accent": "#60A5FA", "accent2": "#2563EB",
        "bg_sidebar": "#0A0E1A", "bg_content": "#0D1220", "bg_card": "#141B2E",
    },
}

DEFAULT_THEME = "Violet Frost"


def get_theme_name() -> str:
    return state.load_state().get("theme", DEFAULT_THEME)


def get_theme() -> dict:
    return PRESETS.get(get_theme_name(), PRESETS[DEFAULT_THEME])


def get_accent_colors():
    t = get_theme()
    return t["accent"], t["accent2"]


def get_bg_colors():
    t = get_theme()
    return t["bg_sidebar"], t["bg_content"], t["bg_card"]


def set_theme(name: str):
    if name not in PRESETS:
        return
    s = state.load_state()
    s["theme"] = name
    state.save_state(s)
