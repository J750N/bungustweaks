"""
Best-effort launchers for existing vendor tools. We never reimplement what
these already do safely (especially overclocking) - we just try to open
them if they're installed, and point to the download page if not.

BUNDLING YOUR OWN COPIES (recommended):
We can't ship NVIDIA's/AMD's/MSI's own installers ourselves (no way to
fetch third-party binaries in development, and redistributing vendor
software isn't ours to just decide). But if YOU drop the real files into
the `tools/` folder next to this app, once, they'll be auto-detected and
launched with zero settings needed - see tools/README.md for exactly where
each one goes.
"""

import os
import subprocess
import sys

BUNDLED_TOOLS_DIR = os.path.join(
    getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools"
)

BUNDLED_PATHS = {
    "nvidia_app": os.path.join(BUNDLED_TOOLS_DIR, "NVIDIAApp", "NVIDIA app.exe"),
    "nvidia_control_panel": os.path.join(BUNDLED_TOOLS_DIR, "NVIDIAApp", "nvcplui.exe"),
    "amd_adrenalin": os.path.join(BUNDLED_TOOLS_DIR, "AMDAdrenalin", "RadeonSoftware.exe"),
    "intel_graphics": os.path.join(BUNDLED_TOOLS_DIR, "IntelGraphics", "IGCC.exe"),
    "msi_afterburner": os.path.join(BUNDLED_TOOLS_DIR, "MSIAfterburner", "MSIAfterburner.exe"),
    "nvidia_profile_inspector": os.path.join(BUNDLED_TOOLS_DIR, "nvidiaProfileInspector", "nvidiaProfileInspector.exe"),
}

COMMON_PATHS = {
    "nvidia_app": [
        r"C:\Program Files\NVIDIA Corporation\NVIDIA app\CEF\NVIDIA app.exe",
        r"C:\Program Files\WindowsApps\NVIDIACorp.NVIDIAControlPanel_*\nvcplui.exe",
    ],
    "nvidia_control_panel": [
        r"C:\Windows\System32\nvcplui.exe",
    ],
    "amd_adrenalin": [
        r"C:\Program Files\AMD\CNext\CNext\RadeonSoftware.exe",
    ],
    "intel_graphics": [
        r"C:\Program Files\Intel\Intel(R) Graphics Command Center\IGCC.exe",
    ],
    "msi_afterburner": [
        r"C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe",
        r"C:\Program Files\MSI Afterburner\MSIAfterburner.exe",
    ],
}

DOWNLOAD_URLS = {
    "nvidia_app": "https://www.nvidia.com/en-us/software/nvidia-app/",
    "nvidia_control_panel": "https://www.nvidia.com/en-us/software/nvidia-app/",
    "amd_adrenalin": "https://www.amd.com/en/support",
    "intel_graphics": "https://www.intel.com/content/www/us/en/support/detect.html",
    "msi_afterburner": "https://www.msi.com/Landing/afterburner",
    "nvidia_profile_inspector": "https://github.com/Orbmu2k/nvidiaProfileInspector/releases",
}


def _find_installed(tool_key: str):
    import glob

    # 1. Bundled copy next to the app - zero config, checked first
    bundled = BUNDLED_PATHS.get(tool_key)
    if bundled and os.path.exists(bundled):
        return bundled

    # 2. A normal system install
    for path in COMMON_PATHS.get(tool_key, []):
        if "*" in path:
            matches = glob.glob(path)
            if matches:
                return matches[0]
        elif os.path.exists(path):
            return path
    return None


def launch_tool(tool_key: str):
    """Returns (success, message). If not installed, opens the download page instead."""
    path = _find_installed(tool_key)
    if path:
        try:
            subprocess.Popen(f'"{path}"', shell=True)
            return True, "Launched."
        except Exception as e:
            return False, str(e)

    url = DOWNLOAD_URLS.get(tool_key)
    if url:
        import webbrowser
        webbrowser.open(url)
        return False, "Not found on this PC - opened the download page instead."
    return False, "Not found and no download link available."
