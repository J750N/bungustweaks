"""
Adds/removes a 'launch on Windows startup' registry entry (HKCU Run key -
no admin required, applies to the current user only).
"""

import subprocess
import sys
import os

RUN_KEY = r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "BungusTweaks"


def _launch_command() -> str:
    """Best-effort command to relaunch this app. Works perfectly once packaged
    as a .exe (PyInstaller); in dev mode it re-invokes the current script with
    the current interpreter."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    script = os.path.abspath(sys.argv[0])
    return f'"{sys.executable}" "{script}"'


def enable_startup() -> bool:
    cmd = f'reg add "{RUN_KEY}" /v {VALUE_NAME} /t REG_SZ /d {_launch_command()} /f'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0


def disable_startup() -> bool:
    cmd = f'reg delete "{RUN_KEY}" /v {VALUE_NAME} /f'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0


def is_startup_enabled() -> bool:
    cmd = f'reg query "{RUN_KEY}" /v {VALUE_NAME}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0
