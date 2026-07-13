"""
Backup / safety net:
  - create_restore_point(): a full Windows System Restore Point
  - export_registry(): dumps the whole HKCU + relevant HKLM policy trees
    to a timestamped .reg file before any tweak touches them, so the
    user can always double-click to restore.
"""

import subprocess
import os
import datetime

APP_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "BungusTweaks")
BACKUP_DIR = os.path.join(APP_DIR, "backups")

REG_ROOTS_TO_BACKUP = [
    r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion",
    r"HKLM\SOFTWARE\Policies\Microsoft\Windows",
    r"HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
]


def _ensure_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def create_restore_point(description="PC Tweaker Restore Point"):
    """Creates a Windows System Restore Point. Requires admin."""
    cmd = (
        'powershell -NoProfile -Command '
        f'"Checkpoint-Computer -Description \'{description}\' -RestorePointType \'MODIFY_SETTINGS\'"'
    )
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def export_registry():
    """Exports key registry trees to timestamped .reg files. Returns list of file paths."""
    _ensure_dir()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    exported = []
    for root in REG_ROOTS_TO_BACKUP:
        safe_name = root.replace("\\", "_").replace(" ", "")
        out_path = os.path.join(BACKUP_DIR, f"{safe_name}_{timestamp}.reg")
        cmd = f'reg export "{root}" "{out_path}" /y'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            exported.append(out_path)
    return exported


def list_backups():
    _ensure_dir()
    return sorted(
        [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.endswith(".reg")],
        reverse=True,
    )


def restore_from_file(path):
    """Re-imports a previously exported .reg backup file."""
    cmd = f'reg import "{path}"'
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def open_restore_ui():
    """Opens the native Windows System Restore wizard."""
    subprocess.Popen("rstrui.exe", shell=True)
