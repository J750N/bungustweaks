"""
Runs Windows shell commands (reg.exe, powershell, powercfg, netsh, etc.)
and reports success/failure back to the UI thread.
"""

import subprocess
import threading
import ctypes
import sys
import os


def is_admin() -> bool:
    """Check if the app is running with Administrator privileges."""
    if os.name != "nt":
        return False
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def relaunch_as_admin():
    """Re-launch this app elevated, then exit the current (non-admin) process.
    Returns False if elevation failed OR if the user clicked 'No' on the UAC prompt -
    ShellExecuteW never raises for that, it just returns a small integer (<=32)."""
    if os.name != "nt":
        return False
    try:
        if getattr(sys, "frozen", False):
            # Packaged .exe: relaunch itself directly, no script path needed.
            target = sys.executable
            args = " ".join(f'"{a}"' for a in sys.argv[1:])
        else:
            script = os.path.abspath(sys.argv[0])
            target = sys.executable
            args = f'"{script}" ' + " ".join(f'"{a}"' for a in sys.argv[1:])

        result = ctypes.windll.shell32.ShellExecuteW(None, "runas", target, args.strip(), None, 1)
        return result > 32
    except Exception:
        return False


# sc.exe exit codes that mean "already in the state you wanted" or "doesn't exist on
# this system" - not real failures, just sc.exe being pedantic. Treating these as hard
# errors was causing tweaks to be wrongly reported as failed (and their toggle flipped
# back off) even when the actual change succeeded.
BENIGN_SC_CODES = {
    1062: "service was already stopped",
    1056: "service was already running",
    1060: "service doesn't exist on this system (may not apply to your Windows edition/build)",
}


def _is_sc_command(cmd: str) -> bool:
    c = cmd.strip().lower()
    return c.startswith("sc stop") or c.startswith("sc start") or c.startswith("sc config")


def run_commands(commands, on_line=None, on_done=None):
    """
    Run a list of shell command strings sequentially in a background thread.

    on_line(str)         called for every line of stdout/stderr as it streams in
    on_done(success:bool, errors:list[str]) called once all commands finish
    """

    def worker():
        errors = []
        for cmd in commands:
            if on_line:
                on_line(f"$ {cmd}")
            try:
                proc = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=600,
                )
                if proc.stdout:
                    for line in proc.stdout.splitlines():
                        if on_line and line.strip():
                            on_line(line)
                if proc.returncode != 0:
                    benign_reason = BENIGN_SC_CODES.get(proc.returncode) if _is_sc_command(cmd) else None
                    if benign_reason:
                        if on_line:
                            on_line(f"  · {benign_reason} — not a real failure, continuing")
                    else:
                        msg = proc.stderr.strip() or f"Exited with code {proc.returncode}"
                        errors.append(f"{cmd} -> {msg}")
                        if on_line:
                            on_line(f"  ! {msg}")
            except Exception as e:
                errors.append(f"{cmd} -> {e}")
                if on_line:
                    on_line(f"  ! {e}")
        if on_done:
            on_done(len(errors) == 0, errors)

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return t
