"""
Windows background services people commonly disable to reduce clutter/RAM.
Split into "Safe" (low downside for most people) and "Advanced" (real
tradeoffs - only disable if you understand what you're giving up).

Same shape as a tweak entry so it plugs straight into TweakCategoryPage.
"""

SERVICES = {

    "Safe": [
        {
            "key": "svc_fax",
            "name": "Fax Service",
            "description": "Lets Windows send/receive faxes through a modem. Virtually nobody uses this anymore.",
            "risk": "safe", "warning": None,
            "apply": [r'sc config Fax start= disabled', r'sc stop Fax'],
            "revert": [r'sc config Fax start= demand', r'sc start Fax'],
        },
        {
            "key": "svc_remote_registry",
            "name": "Remote Registry",
            "description": "Lets other computers on the network edit your registry remotely. Off by default on most home PCs anyway.",
            "risk": "safe", "warning": None,
            "apply": [r'sc config RemoteRegistry start= disabled', r'sc stop RemoteRegistry'],
            "revert": [r'sc config RemoteRegistry start= demand', r'sc start RemoteRegistry'],
        },
        {
            "key": "svc_retail_demo",
            "name": "Retail Demo Service",
            "description": "Powers the in-store 'demo mode' kiosk experience. Irrelevant on a personal PC.",
            "risk": "safe", "warning": None,
            "apply": [r'sc config RetailDemo start= disabled', r'sc stop RetailDemo'],
            "revert": [r'sc config RetailDemo start= demand', r'sc start RetailDemo'],
        },
        {
            "key": "svc_maps_broker",
            "name": "Downloaded Maps Manager",
            "description": "Manages offline maps for the Windows Maps app.",
            "risk": "safe", "warning": None,
            "apply": [r'sc config MapsBroker start= disabled', r'sc stop MapsBroker'],
            "revert": [r'sc config MapsBroker start= demand', r'sc start MapsBroker'],
        },
        {
            "key": "svc_wmp_network_sharing",
            "name": "Windows Media Player Network Sharing",
            "description": "Streams your media library to other devices on your network via Windows Media Player.",
            "risk": "safe", "warning": None,
            "apply": [r'sc config WMPNetworkSvc start= disabled', r'sc stop WMPNetworkSvc'],
            "revert": [r'sc config WMPNetworkSvc start= demand', r'sc start WMPNetworkSvc'],
        },
        {
            "key": "svc_program_compat_assistant",
            "name": "Program Compatibility Assistant",
            "description": "Monitors older programs for compatibility issues and shows warning popups.",
            "risk": "safe", "warning": None,
            "apply": [r'sc config PcaSvc start= disabled', r'sc stop PcaSvc'],
            "revert": [r'sc config PcaSvc start= auto', r'sc start PcaSvc'],
        },
    ],

    "Advanced": [
        {
            "key": "svc_print_spooler",
            "name": "Print Spooler",
            "description": "Manages all printing on your PC.",
            "risk": "risky", "warning": "Disabling this means you can't print anything until it's turned back on.",
            "apply": [r'sc config Spooler start= disabled', r'sc stop Spooler'],
            "revert": [r'sc config Spooler start= auto', r'sc start Spooler'],
        },
        {
            "key": "svc_geolocation",
            "name": "Geolocation Service",
            "description": "The background service behind Windows location features (separate from the location privacy tweak).",
            "risk": "moderate", "warning": "Weather, Maps, and 'Find My Device' style features may stop working.",
            "apply": [r'sc config lfsvc start= disabled', r'sc stop lfsvc'],
            "revert": [r'sc config lfsvc start= demand', r'sc start lfsvc'],
        },
        {
            "key": "svc_xbox_live",
            "name": "Xbox Live Services",
            "description": "Powers Xbox/Game Pass sign-in and Xbox Live networking used by some multiplayer games.",
            "risk": "moderate", "warning": "Can break sign-in or multiplayer for games that rely on Xbox Live/Game Pass.",
            "apply": [
                r'sc config XblAuthManager start= disabled', r'sc stop XblAuthManager',
                r'sc config XboxNetApiSvc start= disabled', r'sc stop XboxNetApiSvc',
            ],
            "revert": [
                r'sc config XblAuthManager start= demand', r'sc start XblAuthManager',
                r'sc config XboxNetApiSvc start= demand', r'sc start XboxNetApiSvc',
            ],
        },
        {
            "key": "svc_tablet_input",
            "name": "Touch Keyboard & Handwriting Panel",
            "description": "Powers the on-screen touch keyboard and handwriting input panel.",
            "risk": "moderate", "warning": "Needed if you use a touchscreen, tablet mode, or a pen.",
            "apply": [r'sc config TabletInputService start= disabled', r'sc stop TabletInputService'],
            "revert": [r'sc config TabletInputService start= demand', r'sc start TabletInputService'],
        },
        {
            "key": "svc_diagnostic_policy",
            "name": "Diagnostic Policy Service",
            "description": "Runs Windows' built-in troubleshooters (network, audio, etc).",
            "risk": "risky", "warning": "Breaks most 'Troubleshoot' buttons in Windows Settings.",
            "apply": [r'sc config DPS start= disabled', r'sc stop DPS'],
            "revert": [r'sc config DPS start= auto', r'sc start DPS'],
        },
    ],
}
