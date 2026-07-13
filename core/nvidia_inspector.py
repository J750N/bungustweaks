"""
Integration with nvidiaProfileInspector (a well-known free third-party tool
by Orbmu2k for editing/importing NVIDIA driver profiles). We do NOT bundle
that .exe ourselves - the user points us at their own copy once, and after
that we can import one of our bundled .nip profiles into it with one click.

Get nvidiaProfileInspector: https://github.com/Orbmu2k/nvidiaProfileInspector
"""

import os
import subprocess
from core import launchers

PROFILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "nvidia_profiles")

BUNDLED_PROFILES = {
    "Desktop": os.path.join(PROFILES_DIR, "Desktop.nip"),
    "Laptop": os.path.join(PROFILES_DIR, "Laptop.nip"),
}


def get_inspector_path() -> str:
    """Checks the bundled tools/nvidiaProfileInspector/ folder first (zero-config),
    then falls back to whatever path the user manually set in Settings."""
    bundled = launchers.BUNDLED_PATHS.get("nvidia_profile_inspector")
    if bundled and os.path.exists(bundled):
        return bundled
    from core import state
    return state.load_state().get("nvidia_inspector_path", "")


def is_bundled() -> bool:
    bundled = launchers.BUNDLED_PATHS.get("nvidia_profile_inspector")
    return bool(bundled and os.path.exists(bundled))


def set_inspector_path(path: str):
    from core import state
    s = state.load_state()
    s["nvidia_inspector_path"] = path
    state.save_state(s)


def is_configured() -> bool:
    path = get_inspector_path()
    return bool(path) and os.path.exists(path)


def apply_profile(profile_name: str):
    """Runs nvidiaProfileInspector.exe -import <profile>.nip. Returns (success, message)."""
    inspector = get_inspector_path()
    if not inspector or not os.path.exists(inspector):
        return False, "NVIDIA Profile Inspector path isn't set. Configure it in Settings first."

    profile_path = BUNDLED_PROFILES.get(profile_name)
    if not profile_path or not os.path.exists(profile_path):
        return False, f"Profile '{profile_name}' not found."

    try:
        result = subprocess.run(
            f'"{inspector}" -silent -import "{profile_path}"',
            shell=True, capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return True, f"Applied the {profile_name} NVIDIA profile."
        return False, result.stderr.strip() or "Import failed - is the path to nvidiaProfileInspector.exe correct?"
    except Exception as e:
        return False, str(e)
