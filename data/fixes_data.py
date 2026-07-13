"""
One-click fixes. These are not toggles - clicking Fix just runs the commands once.
"""

FIXES = [
    {
        "key": "fix_network",
        "name": "Reset Network",
        "description": "Fixes 'no internet', DNS issues, and broken Wi-Fi/Ethernet adapters.",
        "commands": [
            "netsh winsock reset",
            "netsh int ip reset",
            "ipconfig /flushdns",
            "ipconfig /release",
            "ipconfig /renew",
        ],
        "needs_restart": True,
    },
    {
        "key": "fix_audio",
        "name": "Fix Audio Issues",
        "description": "Restarts the Windows Audio services (fixes no-sound / stuck volume issues).",
        "commands": [
            "net stop Audiosrv",
            "net stop AudioEndpointBuilder",
            "net start AudioEndpointBuilder",
            "net start Audiosrv",
        ],
        "needs_restart": False,
    },
    {
        "key": "fix_windows_update",
        "name": "Fix Windows Update",
        "description": "Resets the Windows Update cache when updates fail or get stuck.",
        "commands": [
            "net stop wuauserv",
            "net stop bits",
            "net stop cryptsvc",
            r'ren "%windir%\SoftwareDistribution" SoftwareDistribution.old',
            "net start wuauserv",
            "net start bits",
            "net start cryptsvc",
        ],
        "needs_restart": False,
    },
    {
        "key": "fix_system_files",
        "name": "Scan & Repair System Files",
        "description": "Runs SFC and DISM to find and repair corrupted Windows files. Can take 10-20 minutes.",
        "commands": [
            "DISM /Online /Cleanup-Image /RestoreHealth",
            "sfc /scannow",
        ],
        "needs_restart": False,
    },
    {
        "key": "fix_clipboard",
        "name": "Fix Clipboard",
        "description": "Re-enables Windows clipboard history and cross-device clipboard sync.",
        "commands": [
            r'reg add "HKCU\SOFTWARE\Microsoft\Clipboard" /v EnableClipboardHistory /t REG_DWORD /d 1 /f',
        ],
        "needs_restart": False,
    },
    {
        "key": "fix_bluetooth",
        "name": "Restore Bluetooth",
        "description": "Restarts Bluetooth support services if Bluetooth stopped working.",
        "commands": [
            "net stop bthserv",
            "net start bthserv",
        ],
        "needs_restart": False,
    },
    {
        "key": "fix_disk_cleanup",
        "name": "Clean Temp & Cache Files",
        "description": "Deletes temporary files, Windows Update leftovers, and old error reports.",
        "commands": [
            r'del /q /f /s "%temp%\*"',
            r'del /q /f /s "C:\Windows\Temp\*"',
            r'del /q /f /s "C:\Windows\Prefetch\*"',
        ],
        "needs_restart": False,
    },
]
