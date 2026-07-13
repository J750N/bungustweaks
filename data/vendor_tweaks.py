"""
Vendor-specific GPU tweaks and general CPU tweaks, shown on the Gaming
page's GPU/CPU sections based on detected hardware.
"""

NVIDIA_TWEAKS = [
    {
        "key": "disable_nvidia_telemetry",
        "name": "Disable NVIDIA Telemetry",
        "description": "Stops the background service NVIDIA uses to collect usage data from its apps.",
        "risk": "safe", "warning": None,
        "apply": [r'sc config NvTelemetryContainer start= disabled', r'sc stop NvTelemetryContainer'],
        "revert": [r'sc config NvTelemetryContainer start= demand', r'sc start NvTelemetryContainer'],
    },
]

AMD_TWEAKS = [
    {
        "key": "disable_amd_external_events",
        "name": "Disable AMD External Events Utility",
        "description": "A background AMD service for hotkeys/events most people never use. "
                        "Only takes effect if this service exists on your system.",
        "risk": "safe", "warning": None,
        "apply": [r'sc config AMDExternalEventUtility start= disabled', r'sc stop AMDExternalEventUtility'],
        "revert": [r'sc config AMDExternalEventUtility start= demand', r'sc start AMDExternalEventUtility'],
    },
]

CPU_TWEAKS = [
    {
        "key": "disable_core_parking",
        "name": "Disable CPU Core Parking",
        "description": "Keeps all CPU cores active instead of Windows periodically 'parking' idle ones - "
                        "can reduce micro-stutter in games on the active power plan.",
        "risk": "moderate", "warning": "Slightly higher idle power draw and heat.",
        "apply": [
            r'powercfg /setacvalueindex scheme_current sub_processor 0cc5b647-c1df-4637-891a-dec35c318583 100',
            r'powercfg /setactive scheme_current',
        ],
        "revert": [
            r'powercfg /setacvalueindex scheme_current sub_processor 0cc5b647-c1df-4637-891a-dec35c318583 5',
            r'powercfg /setactive scheme_current',
        ],
    },
]
