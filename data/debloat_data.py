"""
List of common bundled ("bloat") Windows apps.
Each entry removes the Appx package for the current user and, where relevant,
the provisioned package so it doesn't come back for new users.
"""

BLOAT_APPS = [
    {"key": "xbox", "name": "Xbox App & Services", "package": "Microsoft.XboxApp",
     "description": "Xbox Console Companion. Safe to remove if you don't use Xbox/Game Pass."},
    {"key": "xbox_gamebar", "name": "Xbox Game Bar", "package": "Microsoft.XboxGamingOverlay",
     "description": "The overlay opened with Win+G."},
    {"key": "weather", "name": "Weather App", "package": "Microsoft.BingWeather",
     "description": "MSN Weather app."},
    {"key": "news", "name": "News App", "package": "Microsoft.BingNews",
     "description": "Microsoft News app."},
    {"key": "people", "name": "People App", "package": "Microsoft.People",
     "description": "Contacts hub, rarely used outside Outlook integration."},
    {"key": "skype", "name": "Skype (built-in)", "package": "Microsoft.SkypeApp",
     "description": "Pre-installed Skype app (not the desktop client you install manually)."},
    {"key": "zune_music", "name": "Groove Music", "package": "Microsoft.ZuneMusic",
     "description": "Windows' built-in music player."},
    {"key": "zune_video", "name": "Movies & TV", "package": "Microsoft.ZuneVideo",
     "description": "Windows' built-in video player."},
    {"key": "solitaire", "name": "Microsoft Solitaire Collection", "package": "Microsoft.MicrosoftSolitaireCollection",
     "description": "Pre-installed card games."},
    {"key": "your_phone", "name": "Phone Link", "package": "Microsoft.YourPhone",
     "description": "Phone Link / Your Phone companion app."},
    {"key": "office_hub", "name": "Get Office / Office Hub", "package": "Microsoft.MicrosoftOfficeHub",
     "description": "Promotional shortcut to buy Office."},
    {"key": "feedback_hub", "name": "Feedback Hub", "package": "Microsoft.WindowsFeedbackHub",
     "description": "Sends feedback to Microsoft."},
    {"key": "mixed_reality", "name": "Mixed Reality Portal", "package": "Microsoft.MixedReality.Portal",
     "description": "VR headset setup app, unnecessary without a headset."},
    {"key": "3dviewer", "name": "3D Viewer / Paint 3D", "package": "Microsoft.Microsoft3DViewer",
     "description": "3D model viewer, rarely used."},
]
