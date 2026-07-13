"""
Apps installable via winget (Windows Package Manager - built into Windows
10/11). No bundled installers needed; winget fetches the real thing
straight from the vendor/Microsoft Store backend.
"""

INSTALL_APPS = [
    {"key": "chrome", "name": "Google Chrome", "winget_id": "Google.Chrome",
     "description": "The most widely used web browser."},
    {"key": "firefox", "name": "Mozilla Firefox", "winget_id": "Mozilla.Firefox",
     "description": "Privacy-focused open-source web browser."},
    {"key": "discord", "name": "Discord", "winget_id": "Discord.Discord",
     "description": "Voice, video, and text chat built for gamers and communities."},
    {"key": "steam", "name": "Steam", "winget_id": "Valve.Steam",
     "description": "The biggest PC gaming storefront and launcher."},
    {"key": "vlc", "name": "VLC Media Player", "winget_id": "VideoLAN.VLC",
     "description": "Plays virtually any video/audio format, no codecs needed."},
    {"key": "7zip", "name": "7-Zip", "winget_id": "7zip.7zip",
     "description": "Free, fast file archiver — zip/rar/7z and more."},
    {"key": "notepadpp", "name": "Notepad++", "winget_id": "Notepad++.Notepad++",
     "description": "Lightweight code and text editor."},
    {"key": "spotify", "name": "Spotify", "winget_id": "Spotify.Spotify",
     "description": "Music streaming."},
    {"key": "msiafterburner", "name": "MSI Afterburner", "winget_id": "Guru3D.Afterburner",
     "description": "GPU monitoring and overclocking (see the Gaming page for one-click launch)."},
    {"key": "obs", "name": "OBS Studio", "winget_id": "OBSProject.OBSStudio",
     "description": "Free screen recording and live streaming software."},
    {"key": "epicgames", "name": "Epic Games Launcher", "winget_id": "EpicGames.EpicGamesLauncher",
     "description": "Storefront/launcher for Epic Games titles and free weekly games."},
]
