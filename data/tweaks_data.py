"""
Tweak definitions.

Each tweak has:
    key         unique id (used to remember toggle state)
    name        display name
    description shown under the name / in the hover tooltip
    risk        "safe" | "moderate" | "risky"  -> drives the colored dot
    warning     optional short warning line shown in orange (None if safe)
    apply       list of command strings (run with subprocess, one per line)
    revert      list of command strings that undo the apply commands

Commands are plain Windows commands (reg.exe / powershell / powercfg / netsh / sc / fsutil).
They are executed via core.runner.run_commands().
"""

TWEAKS = {

    "Core": [
        {
            "key": "disable_telemetry",
            "name": "Disable Telemetry",
            "description": "Stops Windows from sending diagnostic usage data to Microsoft.",
            "risk": "safe", "warning": None,
            "apply": [
                r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f',
                r'sc config DiagTrack start= disabled', r'sc stop DiagTrack',
            ],
            "revert": [
                r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry /t REG_DWORD /d 3 /f',
                r'sc config DiagTrack start= auto', r'sc start DiagTrack',
            ],
        },
        {
            "key": "disable_cortana",
            "name": "Disable Cortana & Web Search",
            "description": "Removes Bing web results from Start Menu search.",
            "risk": "safe", "warning": None,
            "apply": [
                r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f',
                r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" /v BingSearchEnabled /t REG_DWORD /d 0 /f',
            ],
            "revert": [
                r'reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v AllowCortana /f',
                r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" /v BingSearchEnabled /t REG_DWORD /d 1 /f',
            ],
        },
        {
            "key": "disable_gamedvr",
            "name": "Disable Game DVR / Game Bar",
            "description": "Stops background game recording that can cause stutter/FPS loss.",
            "risk": "safe", "warning": None,
            "apply": [
                r'reg add "HKCU\System\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f',
                r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v AllowGameDVR /t REG_DWORD /d 0 /f',
            ],
            "revert": [
                r'reg add "HKCU\System\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 1 /f',
                r'reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v AllowGameDVR /f',
            ],
        },
        {
            "key": "disable_notifications",
            "name": "Disable All Notifications",
            "description": "Turns off toast notifications and Action Center popups.",
            "risk": "moderate", "warning": "May hide important system alerts.",
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\PushNotifications" /v ToastEnabled /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\PushNotifications" /v ToastEnabled /t REG_DWORD /d 1 /f'],
        },
        {
            "key": "disable_startup_delay",
            "name": "Disable Startup App Delay",
            "description": "Removes the artificial delay before startup apps launch.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Serialize" /v StartupDelayInMSec /t REG_DWORD /d 0 /f'],
            "revert": [r'reg delete "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Serialize" /v StartupDelayInMSec /f'],
        },
        {
            "key": "disable_animations",
            "name": "Disable Animations & Visual Effects",
            "description": "Switches Windows to 'best performance' visuals.",
            "risk": "safe", "warning": None,
            "apply": [
                r'reg add "HKCU\Control Panel\Desktop" /v UserPreferencesMask /t REG_BINARY /d 9012078010000000 /f',
                r'reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v MinAnimate /t REG_SZ /d 0 /f',
            ],
            "revert": [
                r'reg add "HKCU\Control Panel\Desktop" /v UserPreferencesMask /t REG_BINARY /d 9E1E078012000000 /f',
                r'reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v MinAnimate /t REG_SZ /d 1 /f',
            ],
        },
        {
            "key": "disable_search_highlights",
            "name": "Disable Search Box Suggestions & Highlights",
            "description": "Removes trending/news content and suggestions from the taskbar search box.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Policies\Microsoft\Windows\Explorer" /v DisableSearchBoxSuggestions /t REG_DWORD /d 1 /f'],
            "revert": [r'reg delete "HKCU\SOFTWARE\Policies\Microsoft\Windows\Explorer" /v DisableSearchBoxSuggestions /f'],
        },
        {
            "key": "disable_widgets",
            "name": "Disable Taskbar Widgets",
            "description": "Removes the News & Interests / Widgets button from the taskbar.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Dsh" /v AllowNewsAndInterests /t REG_DWORD /d 0 /f'],
            "revert": [r'reg delete "HKLM\SOFTWARE\Policies\Microsoft\Dsh" /v AllowNewsAndInterests /f'],
        },
        {
            "key": "disable_chat_icon",
            "name": "Disable Chat (Teams) Icon",
            "description": "Removes the Chat/Teams icon from the taskbar.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarMn /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarMn /t REG_DWORD /d 1 /f'],
        },
        {
            "key": "disable_copilot",
            "name": "Remove Copilot Button",
            "description": "Removes the Windows Copilot button from the taskbar.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowCopilotButton /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowCopilotButton /t REG_DWORD /d 1 /f'],
        },
        {
            "key": "show_file_extensions",
            "name": "Always Show File Extensions",
            "description": "Shows the .txt / .exe / .jpg part of every filename in Explorer.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v HideFileExt /t REG_DWORD /d 1 /f'],
        },
        {
            "key": "show_hidden_files",
            "name": "Show Hidden Files & Folders",
            "description": "Makes hidden system folders visible in File Explorer.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v Hidden /t REG_DWORD /d 1 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v Hidden /t REG_DWORD /d 2 /f'],
        },
        {
            "key": "mute_startup_sound",
            "name": "Mute Windows Startup Sound",
            "description": "Stops the chime that plays when Windows finishes booting.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\AppEvents\Schemes\Apps\.Default\SystemNotification\.Current" /v DisableStartupSound /t REG_DWORD /d 1 /f',
                      r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\LogonUI\BootAnimation" /v DisableStartupSound /t REG_DWORD /d 1 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\LogonUI\BootAnimation" /v DisableStartupSound /t REG_DWORD /d 0 /f'],
        },
        {
            "key": "disable_windows_spotlight",
            "name": "Disable Windows Spotlight",
            "description": "Stops the lock screen from rotating in Microsoft's curated background photos and 'Did you know' tips.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Policies\Microsoft\Windows\CloudContent" /v DisableWindowsSpotlightFeatures /t REG_DWORD /d 1 /f'],
            "revert": [r'reg delete "HKCU\SOFTWARE\Policies\Microsoft\Windows\CloudContent" /v DisableWindowsSpotlightFeatures /f'],
        },
    ],

    "Privacy": [
        {
            "key": "disable_activity_history",
            "name": "Disable Activity History",
            "description": "Stops Windows from tracking your recent activity/timeline.",
            "risk": "safe", "warning": None,
            "apply": [
                r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v EnableActivityFeed /t REG_DWORD /d 0 /f',
                r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v PublishUserActivities /t REG_DWORD /d 0 /f',
            ],
            "revert": [
                r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v EnableActivityFeed /t REG_DWORD /d 1 /f',
                r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v PublishUserActivities /t REG_DWORD /d 1 /f',
            ],
        },
        {
            "key": "disable_advertising_id",
            "name": "Disable Advertising ID",
            "description": "Stops apps from using an ID to personalize ads for you.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" /v Enabled /t REG_DWORD /d 1 /f'],
        },
        {
            "key": "disable_location",
            "name": "Disable Location Tracking",
            "description": "Turns off Windows location services system-wide.",
            "risk": "moderate", "warning": "Weather/maps apps may stop working correctly.",
            "apply": [r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location" /v Value /t REG_SZ /d Deny /f'],
            "revert": [r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location" /v Value /t REG_SZ /d Allow /f'],
        },
        {
            "key": "disable_diagnostics",
            "name": "Disable Feedback & Diagnostics Requests",
            "description": "Stops Windows from periodically asking for feedback.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Siuf\Rules" /v NumberOfSIUFInPeriod /t REG_DWORD /d 0 /f'],
            "revert": [r'reg delete "HKCU\SOFTWARE\Microsoft\Siuf\Rules" /v NumberOfSIUFInPeriod /f'],
        },
        {
            "key": "disable_clipboard_cloud_sync",
            "name": "Disable Clipboard Cloud Sync",
            "description": "Stops your clipboard history from syncing to Microsoft's cloud / other devices.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Clipboard" /v EnableCloudClipboard /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\Clipboard" /v EnableCloudClipboard /t REG_DWORD /d 1 /f'],
        },
        {
            "key": "disable_tailored_experiences",
            "name": "Disable Tailored Experiences",
            "description": "Stops Microsoft from using your diagnostic data to personalize tips and ads.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Policies\Microsoft\Windows\CloudContent" /v DisableTailoredExperiencesWithDiagnosticData /t REG_DWORD /d 1 /f'],
            "revert": [r'reg delete "HKCU\SOFTWARE\Policies\Microsoft\Windows\CloudContent" /v DisableTailoredExperiencesWithDiagnosticData /f'],
        },
        {
            "key": "disable_error_reporting",
            "name": "Disable Windows Error Reporting",
            "description": "Stops Windows from sending crash/error reports to Microsoft.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting" /v Disabled /t REG_DWORD /d 1 /f'],
            "revert": [r'reg add "HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting" /v Disabled /t REG_DWORD /d 0 /f'],
        },
        {
            "key": "disable_handwriting_sharing",
            "name": "Disable Handwriting/Typing Data Sharing",
            "description": "Stops Windows from sending your typing/handwriting patterns to Microsoft.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\InputPersonalization" /v RestrictImplicitInkCollection /t REG_DWORD /d 1 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\InputPersonalization" /v RestrictImplicitInkCollection /t REG_DWORD /d 0 /f'],
        },
        {
            "key": "disable_start_menu_ads",
            "name": "Disable Start Menu & Lock Screen Ads/Tips",
            "description": "Removes suggested apps, tips, and promotional tiles from Start and the lock screen.",
            "risk": "safe", "warning": None,
            "apply": [
                r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SystemPaneSuggestionsEnabled /t REG_DWORD /d 0 /f',
                r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v RotatingLockScreenOverlayEnabled /t REG_DWORD /d 0 /f',
            ],
            "revert": [
                r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SystemPaneSuggestionsEnabled /t REG_DWORD /d 1 /f',
                r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v RotatingLockScreenOverlayEnabled /t REG_DWORD /d 1 /f',
            ],
        },
        {
            "key": "disable_find_my_device",
            "name": "Disable Find My Device Location Sync",
            "description": "Stops Windows from periodically syncing this PC's location for the 'Find My Device' feature.",
            "risk": "moderate", "warning": "You won't be able to locate this PC remotely if it's lost or stolen.",
            "apply": [r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\FindMyDevice" /v LocationSyncEnabled /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\FindMyDevice" /v LocationSyncEnabled /t REG_DWORD /d 1 /f'],
        },
    ],

    "Power": [
        {
            "key": "ultimate_performance",
            "name": "Enable Ultimate Performance Power Plan",
            "description": "Unlocks and activates Windows' hidden max-performance plan.",
            "risk": "moderate", "warning": "Increases power draw / heat, not ideal for laptops on battery.",
            "apply": [
                r'powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61',
                r'powershell -Command "$p = (powercfg -l | Select-String \'Ultimate\'); if($p){$id=($p -split \" \")[3]; powercfg -setactive $id}"',
            ],
            "revert": [r'powercfg -setactive SCHEME_BALANCED'],
        },
        {
            "key": "disable_hibernation",
            "name": "Disable Hibernation",
            "description": "Frees disk space taken by hiberfil.sys, disables Fast Startup.",
            "risk": "safe", "warning": None,
            "apply": [r'powercfg -h off'],
            "revert": [r'powercfg -h on'],
        },
        {
            "key": "disable_usb_power_save",
            "name": "Disable USB Selective Suspend",
            "description": "Prevents Windows from powering down idle USB devices (fixes mouse/controller lag).",
            "risk": "safe", "warning": None,
            "apply": [
                r'powercfg /setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0',
                r'powercfg /setdcvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0',
            ],
            "revert": [
                r'powercfg /setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 1',
                r'powercfg /setdcvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 1',
            ],
        },
        {
            "key": "disable_fast_startup",
            "name": "Disable Fast Startup",
            "description": "Fixes cases where dual-boot/driver issues are caused by Windows' hybrid shutdown.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v HiberbootEnabled /t REG_DWORD /d 1 /f'],
        },
        {
            "key": "enable_gpu_scheduling",
            "name": "Enable Hardware-Accelerated GPU Scheduling",
            "description": "Lets your GPU manage its own memory queue instead of Windows, reducing latency in supported games.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f'],
            "revert": [r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 1 /f'],
        },
        {
            "key": "min_processor_state_100",
            "name": "Set Minimum CPU State to 100% (Active Plan)",
            "description": "Stops your CPU from downclocking under light load, for more consistent performance.",
            "risk": "moderate", "warning": "Increases idle power draw and heat — best for desktops, not battery-powered laptops.",
            "apply": [r'powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMIN 100'],
            "revert": [r'powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMIN 5'],
        },
    ],

    "Network": [
        {
            "key": "disable_nagle",
            "name": "Disable Nagle's Algorithm",
            "description": "Reduces network latency for online games by sending packets immediately.",
            "risk": "moderate", "warning": "Touches per-adapter registry keys; rarely, VPN/virtual adapters may need a re-check after.",
            "apply": [
                r'powershell -Command "Get-NetAdapter | ForEach-Object { $g=$_.InterfaceGuid; New-Item -Path (\'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\\\'+$g.Trim(\'{}\')) -Force | Out-Null; Set-ItemProperty -Path (\'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\\\'+$g.Trim(\'{}\')) -Name TcpAckFrequency -Value 1 -Type DWord; Set-ItemProperty -Path (\'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\\\'+$g.Trim(\'{}\')) -Name TCPNoDelay -Value 1 -Type DWord }"',
            ],
            "revert": [
                r'powershell -Command "Get-NetAdapter | ForEach-Object { $g=$_.InterfaceGuid; Remove-ItemProperty -Path (\'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\\\'+$g.Trim(\'{}\')) -Name TcpAckFrequency,TCPNoDelay -ErrorAction SilentlyContinue }"',
            ],
        },
        {
            "key": "set_cloudflare_dns",
            "name": "Set DNS to Cloudflare (1.1.1.1)",
            "description": "Switches your active adapter's DNS to Cloudflare's fast, private resolver.",
            "risk": "moderate", "warning": "Overrides DNS set by your router/ISP.",
            "apply": [
                r'powershell -Command "Get-DnsClientServerAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike \'*Loopback*\'} | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.InterfaceIndex -ServerAddresses (\'1.1.1.1\',\'1.0.0.1\') }"',
            ],
            "revert": [
                r'powershell -Command "Get-DnsClientServerAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike \'*Loopback*\'} | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.InterfaceIndex -ResetServerAddresses }"',
            ],
        },
        {
            "key": "disable_network_throttling",
            "name": "Disable Network Throttling Index",
            "description": "Removes Windows' artificial cap on network throughput for multimedia.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v NetworkThrottlingIndex /t REG_DWORD /d 4294967295 /f'],
            "revert": [r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v NetworkThrottlingIndex /t REG_DWORD /d 10 /f'],
        },
        {
            "key": "tcp_autotuning",
            "name": "Optimize TCP Window Auto-Tuning",
            "description": "Resets TCP auto-tuning to Normal for more consistent download speeds.",
            "risk": "safe", "warning": None,
            "apply": [r'netsh interface tcp set global autotuninglevel=normal'],
            "revert": [r'netsh interface tcp set global autotuninglevel=normal'],
        },
        {
            "key": "disable_qos_reservation",
            "name": "Disable QoS Reserved Bandwidth",
            "description": "Frees up the 20% bandwidth Windows reserves by default for QoS-tagged traffic.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Psched" /v NonBestEffortLimit /t REG_DWORD /d 0 /f'],
            "revert": [r'reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\Psched" /v NonBestEffortLimit /f'],
        },
        {
            "key": "disable_delivery_optimization",
            "name": "Disable Update Delivery Optimization",
            "description": "Stops your PC from uploading Windows Update files to other PCs on the internet (P2P sharing).",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\DeliveryOptimization\Config" /v DODownloadMode /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\DeliveryOptimization\Config" /v DODownloadMode /t REG_DWORD /d 1 /f'],
        },
    ],

    "Gaming": [
        {
            "key": "disable_fullscreen_optimizations",
            "name": "Disable Fullscreen Optimizations (Global)",
            "description": "Forces true exclusive fullscreen for older games, which can reduce input lag.",
            "risk": "moderate", "warning": "Some newer games prefer optimizations on — test per-game if issues appear.",
            "apply": [r'reg add "HKCU\System\GameConfigStore" /v GameDVR_FSEBehaviorMode /t REG_DWORD /d 2 /f'],
            "revert": [r'reg add "HKCU\System\GameConfigStore" /v GameDVR_FSEBehaviorMode /t REG_DWORD /d 0 /f'],
        },
        {
            "key": "system_responsiveness_zero",
            "name": "Set System Responsiveness to 0%",
            "description": "Tells Windows to prioritize foreground games/apps over background multimedia tasks.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v SystemResponsiveness /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v SystemResponsiveness /t REG_DWORD /d 20 /f'],
        },
        {
            "key": "games_task_priority_high",
            "name": "Give Games High Scheduling Priority",
            "description": "Tells the Windows multimedia scheduler to treat 'Games' tasks as high priority.",
            "risk": "safe", "warning": None,
            "apply": [
                r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d 6 /f',
                r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category" /t REG_SZ /d High /f',
            ],
            "revert": [
                r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d 2 /f',
                r'reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category" /t REG_SZ /d Medium /f',
            ],
        },
        {
            "key": "disable_gamebar_shortcuts",
            "name": "Disable Game Bar Keyboard Shortcuts",
            "description": "Stops Win+G and other Game Bar hotkeys from popping up mid-game.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 1 /f'],
        },
        {
            "key": "disable_mouse_accel",
            "name": "Disable Mouse Acceleration (Raw Input)",
            "description": "Turns off 'Enhance Pointer Precision' for 1:1 raw mouse movement, preferred by most gamers.",
            "risk": "safe", "warning": None,
            "apply": [
                r'reg add "HKCU\Control Panel\Mouse" /v MouseSpeed /t REG_SZ /d 0 /f',
                r'reg add "HKCU\Control Panel\Mouse" /v MouseThreshold1 /t REG_SZ /d 0 /f',
                r'reg add "HKCU\Control Panel\Mouse" /v MouseThreshold2 /t REG_SZ /d 0 /f',
            ],
            "revert": [
                r'reg add "HKCU\Control Panel\Mouse" /v MouseSpeed /t REG_SZ /d 1 /f',
                r'reg add "HKCU\Control Panel\Mouse" /v MouseThreshold1 /t REG_SZ /d 6 /f',
                r'reg add "HKCU\Control Panel\Mouse" /v MouseThreshold2 /t REG_SZ /d 10 /f',
            ],
        },
        {
            "key": "increase_mouse_hid_buffer",
            "name": "Increase Mouse Input Buffer",
            "description": "Raises the mouse data queue size so fast movements/high polling-rate mice don't get "
                            "throttled by a small OS buffer. This is not the same as changing your mouse's actual "
                            "polling rate — that's set by your mouse's own software/firmware.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\mouclass\Parameters" /v MouseDataQueueSize /t REG_DWORD /d 32 /f'],
            "revert": [r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\mouclass\Parameters" /v MouseDataQueueSize /t REG_DWORD /d 100 /f'],
        },
        {
            "key": "increase_keyboard_hid_buffer",
            "name": "Increase Keyboard Input Buffer",
            "description": "Same idea for your keyboard — raises the input queue size so fast key presses "
                            "during intense gameplay aren't dropped.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\kbdclass\Parameters" /v KeyboardDataQueueSize /t REG_DWORD /d 32 /f'],
            "revert": [r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\kbdclass\Parameters" /v KeyboardDataQueueSize /t REG_DWORD /d 100 /f'],
        },
    ],

    "Explorer & UI": [
        {
            "key": "taskbar_align_left",
            "name": "Align Taskbar Icons to the Left",
            "description": "Windows 11 defaults to centered icons — this restores the classic left alignment.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarAl /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarAl /t REG_DWORD /d 1 /f'],
        },
        {
            "key": "explorer_open_to_this_pc",
            "name": "Open File Explorer to 'This PC'",
            "description": "Skips the Home/Quick Access screen and opens straight to your drives.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v LaunchTo /t REG_DWORD /d 1 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v LaunchTo /t REG_DWORD /d 2 /f'],
        },
        {
            "key": "disable_quick_access_recents",
            "name": "Hide Recent Files in Quick Access",
            "description": "Stops recently opened files from showing up in the sidebar (useful for shared PCs).",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v Start_TrackDocs /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v Start_TrackDocs /t REG_DWORD /d 1 /f'],
        },
        {
            "key": "disable_sticky_keys_popup",
            "name": "Disable Sticky/Toggle Keys Popups",
            "description": "Stops the 'Do you want to turn on Sticky Keys?' popup from holding Shift 5x.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\Control Panel\Accessibility\StickyKeys" /v Flags /t REG_SZ /d 506 /f'],
            "revert": [r'reg add "HKCU\Control Panel\Accessibility\StickyKeys" /v Flags /t REG_SZ /d 510 /f'],
        },
        {
            "key": "disable_lock_screen",
            "name": "Disable Lock Screen",
            "description": "Goes straight to the sign-in password prompt, skipping the lock screen image.",
            "risk": "moderate", "warning": "Some enterprise/education accounts require the lock screen for policy reasons.",
            "apply": [r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Personalization" /v NoLockScreen /t REG_DWORD /d 1 /f'],
            "revert": [r'reg delete "HKLM\SOFTWARE\Policies\Microsoft\Windows\Personalization" /v NoLockScreen /f'],
        },
        {
            "key": "disable_snap_assist_flyout",
            "name": "Disable Snap Layouts Hover Popup",
            "description": "Stops the layout picker from popping up when you hover over a window's maximize button.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v EnableSnapAssistFlyout /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v EnableSnapAssistFlyout /t REG_DWORD /d 1 /f'],
        },
    ],

    "Storage": [
        {
            "key": "enable_storage_sense",
            "name": "Enable Storage Sense",
            "description": "Turns on Windows' built-in automatic cleanup of temp files and Recycle Bin.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy" /v 01 /t REG_DWORD /d 1 /f'],
            "revert": [r'reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy" /v 01 /t REG_DWORD /d 0 /f'],
        },
        {
            "key": "enable_ssd_trim",
            "name": "Enable SSD TRIM",
            "description": "Makes sure Windows tells your SSD which blocks are free, keeping it fast long-term.",
            "risk": "safe", "warning": None,
            "apply": [r'fsutil behavior set DisableDeleteNotify 0'],
            "revert": [r'fsutil behavior set DisableDeleteNotify 1'],
        },
        {
            "key": "disable_search_indexing",
            "name": "Disable Windows Search Indexing",
            "description": "Stops the background indexer that powers instant search — frees CPU/disk I/O.",
            "risk": "moderate", "warning": "Start Menu and File Explorer search will be noticeably slower.",
            "apply": [r'sc config WSearch start= disabled', r'sc stop WSearch'],
            "revert": [r'sc config WSearch start= delayed-auto', r'sc start WSearch'],
        },
        {
            "key": "disable_sysmain",
            "name": "Disable SysMain (Superfetch)",
            "description": "Stops Windows from pre-loading apps into RAM based on usage patterns.",
            "risk": "moderate", "warning": "Can help on SSDs but may increase load times from cold-boot on HDDs.",
            "apply": [r'sc config SysMain start= disabled', r'sc stop SysMain'],
            "revert": [r'sc config SysMain start= auto', r'sc start SysMain'],
        },
        {
            "key": "disable_reserved_storage",
            "name": "Disable Reserved Storage",
            "description": "Frees up several GB Windows sets aside for its own updates.",
            "risk": "risky", "warning": "Can make future feature updates fail or install more slowly if disk space gets tight again.",
            "apply": [r'DISM /Online /Set-ReservedStorageState /State:Disabled'],
            "revert": [r'DISM /Online /Set-ReservedStorageState /State:Enabled'],
        },
        {
            "key": "enable_long_paths",
            "name": "Enable Long File Paths",
            "description": "Removes the old 260-character path length limit, fixing 'path too long' errors "
                            "with deeply nested folders or some dev tools.",
            "risk": "safe", "warning": None,
            "apply": [r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f'],
            "revert": [r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 0 /f'],
        },
    ],

    "Advanced": [
        {
            "key": "disable_defender_realtime",
            "name": "Disable Windows Defender Real-Time Protection",
            "description": "Turns off live malware scanning. Some tweakers do this for a small performance gain.",
            "risk": "risky",
            "warning": "Leaves your PC without active antivirus protection until you turn this back on. "
                       "Only disable temporarily and only if you know what you're doing.",
            "apply": [r'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"'],
            "revert": [r'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $false"'],
        },
        {
            "key": "disable_uac",
            "name": "Disable User Account Control (UAC)",
            "description": "Stops Windows from prompting for permission before apps make system changes.",
            "risk": "risky", "warning": "Any program (including malware) can silently make admin-level changes with no prompt. Not recommended.",
            "apply": [r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA /t REG_DWORD /d 1 /f'],
        },
        {
            "key": "disable_smartscreen",
            "name": "Disable Windows SmartScreen",
            "description": "Stops Windows from warning you before running unrecognized downloaded apps.",
            "risk": "risky",
            "warning": "Removes a real layer of protection against malicious downloads. Only for advanced users.",
            "apply": [r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v EnableSmartScreen /t REG_DWORD /d 0 /f'],
            "revert": [r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v EnableSmartScreen /t REG_DWORD /d 1 /f'],
        },
        {
            "key": "disable_windows_update",
            "name": "Disable Windows Update",
            "description": "Stops Windows from automatically checking for and installing updates.",
            "risk": "risky",
            "warning": "You'll stop receiving security patches. Only recommended if you plan to update manually and regularly.",
            "apply": [r'sc config wuauserv start= disabled', r'sc stop wuauserv'],
            "revert": [r'sc config wuauserv start= auto', r'sc start wuauserv'],
        },
    ],
}
