# BungusTweaks

A free, open-source Windows tuning tool with a real interactive GUI (no
black CMD window) — inspired by tools like LuminApp / EXM Tweaks.

## Download & Run

**[⬇ Download the latest release](https://github.com/J750N/bungustweaks/releases/latest)**

1. Download `BungusTweaks.exe` from the Releases page above
2. Run it — if Windows shows a "Windows protected your PC" SmartScreen
   warning, click **More info → Run anyway** (this just means the exe isn't
   code-signed, not that anything's wrong)
3. For tweaks/services/fixes to actually apply, click the **"⚠ Not Admin —
   click to elevate"** button in the sidebar the first time you open it (or
   just say yes when it prompts you on launch)

No Python, no installers, no dependencies — the exe has everything bundled
inside it.

## Features

- **Home** — live rolling line graphs for CPU, Memory, and Disk, plus PC
  specs, recent change history, and quick actions
- **Sidebar-first navigation** — every tweak category (Core, Privacy, Power,
  Network, Explorer & UI, Storage, Services, Advanced) is its own sidebar
  entry, instead of being buried in tabs
- **Services** — a dedicated page for background Windows services, split
  into "Safe" (low downside) and "Advanced" (real tradeoffs) groups
- **Gaming** — detects your GPU/CPU vendor, one-click launches into NVIDIA
  App / AMD Adrenalin / Intel Graphics Center / MSI Afterburner, imports
  NVIDIA Profile Inspector driver profiles, plus gaming + input device tweaks
- **Debloat** — one-click removal of pre-installed Windows apps, with a
  Reinstall button (opens the Microsoft Store) if you remove something by
  accident
- **Install Apps** — one-click installs of common apps (Chrome, Discord,
  Steam, VLC, etc.) via winget, with an Uninstall option too
- **History** — every tweak/service change is logged with a timestamp and a
  one-click Revert/Re-Apply, so nothing you do is permanent by accident
- **Backup** — System Restore Points or registry key exports
- **Fixes** — one-click repairs: reset network, fix audio, fix Windows
  Update, run SFC/DISM, clear temp files, restore Bluetooth/clipboard
- **System Info** — clean label/value rows for every piece of
  hardware/software info (real CPU model name, OS build, GPU driver version,
  RAM stick/speed summary)
- **Settings** — 10 accent + dark-palette theme presets (applies instantly,
  no restart needed), "Launch with Windows" toggle, restart-prompt toggle,
  DISM/SFC health scan
- **Restart-on-close prompts** — closing the app shows exactly what changed
  this session and asks if you want to restart (or tells you it's safe to
  just close)
- Every tweak shows a colored risk dot (🟢 safe / 🟡 moderate / 🔴 risky), a
  hover tooltip explaining what it does, and a "PC default → Recommended"
  value comparison

## Why there's no built-in GPU/CPU overclock scanner

We intentionally don't build a homemade "test values and pick the best one"
overclocker. Doing that safely needs direct NVAPI/ADL vendor driver access,
and pushing voltage/clock combinations automatically can crash or stress
hardware if done wrong. Instead, the Gaming page detects your GPU vendor and
gives you one-click launchers into the tools built for this (MSI Afterburner,
the NVIDIA App's Scanner, AMD Adrenalin's auto-tuning) — same convenience,
none of the homemade risk.

## Setting up NVIDIA Profile Inspector (optional)

The Gaming page can import driver-level profiles (texture filtering, shader
cache, sharpening) using
[nvidiaProfileInspector](https://github.com/Orbmu2k/nvidiaProfileInspector),
a free third-party tool we don't bundle ourselves. Drop it into
`tools/nvidiaProfileInspector/` next to the exe (see `tools/README.md`) and
it's auto-detected with zero settings — or set a custom path in
**Settings → System Tools**.

## Safety notes

- The Backup page should be used before your first tweaking session —
  click "Create Restore Point" first.
- All commands are plain, auditable strings in the `data/` files — nothing
  is downloaded or run from the internet, unlike some existing "tweak" tools.
- Everything you change is logged in **History** with one-click revert.

---

## For Developers

Want to read the code, modify a tweak, or build your own release? Everything
below is for running BungusTweaks from source rather than the packaged exe.

### Requirements to run from source

- Windows 10 or 11
- Python 3.10+ (with tkinter — the standard python.org installer includes
  this by default)

### Running it

```powershell
git clone https://github.com/J750N/bungustweaks.git
cd bungustweaks
pip install -r requirements.txt
python app.py
```

### Running it in VS Code

1. Open the folder (`File → Open Folder…`)
2. Install the Python extension if prompted
3. `Ctrl+Shift+P` → `Python: Select Interpreter` → pick your Windows Python 3.10+
4. Open a terminal (`` Ctrl+` ``) and run `pip install -r requirements.txt`
5. Run `python app.py`, or press ▶ on `app.py`
6. For tweaks to actually apply, either click the elevate button in-app, or
   reopen your VS Code terminal as Administrator first

### Project structure

```
bungustweaks/
  app.py                        # main window + sidebar navigation
  core/
    runner.py                    # runs commands in a background thread, admin check/elevate
    state.py                      # persisted on/off state for every tweak
    history.py                     # tweak change log (History page)
    tweak_registry.py               # flat key -> tweak lookup across all data sources
    value_extract.py                 # derives "PC default / Recommended" labels from real commands
    theme.py                          # accent + dark-palette theme presets
    system_info.py                     # CPU/GPU/RAM/OS/network/disk info
    launchers.py                        # vendor tool detection + launching
    nvidia_inspector.py                  # NVIDIA Profile Inspector integration
    startup.py                            # "launch with Windows" registry entry
    backup.py                              # restore point + registry export/import
  data/
    tweaks_data.py                # every tweak's real reg/powershell commands, by category
    services_data.py               # Windows services (Safe/Advanced)
    vendor_tweaks.py                 # NVIDIA/AMD/CPU-specific tweaks (Gaming page)
    debloat_data.py                    # removable bundled apps
    install_apps_data.py                # winget-installable apps
    fixes_data.py                        # one-click repair command sets
    nvidia_profiles/                      # bundled .nip driver profiles
  pages/
    home.py, gaming.py, debloat.py, install_apps.py, history_page.py,
    backup_page.py, fixes.py, system_info.py, settings.py,
    tweak_category_page.py        # generic page shared by every tweak category
    widgets.py                     # shared Card/TweakRow/Tooltip/HistoryGraph/etc.
  tools/                          # optional: drop real vendor tools here for zero-config detection
  assets/                         # icon + font
```

### Adding your own tweak

Open `data/tweaks_data.py` and add an entry to the right category list:

```python
{
    "key": "my_unique_key",
    "name": "My Tweak Name",
    "description": "One sentence explaining what it does.",
    "risk": "safe",                # "safe" | "moderate" | "risky"
    "warning": None,               # or a short string shown in orange
    "apply":  ['reg add "HKCU\\..." /v X /t REG_DWORD /d 1 /f'],
    "revert": ['reg add "HKCU\\..." /v X /t REG_DWORD /d 0 /f'],
},
```

The toggle switch, risk dot, tooltip, default/recommended labels, state
persistence, and history logging are all handled automatically — no UI code
needed. Services, debloat entries, installable apps, and fixes work the same
way in their respective `data/*.py` files.

### Building the standalone exe

```powershell
.\build_exe.bat
```

Bundles everything (Python, tkinter, customtkinter, your code, the icon)
into one file at `dist\BungusTweaks.exe`, with `--uac-admin` so it prompts
for elevation automatically.

### Building the full installer

Install [Inno Setup](https://jrsoftware.org/isdl.php) (free), open
`installer.iss`, press `Ctrl+F9`. Produces `Output\BungusTweaks-Setup.exe`:
installs to Program Files, adds Start Menu + Desktop shortcuts, optionally
installs MSI Afterburner via winget, optionally opens the NVIDIA App
download page, launches the app after setup, and registers a proper
uninstaller.

### Publishing a new release

1. Bump the version in `installer.iss` (`MyAppVersion`) and `pages/settings.py` (`APP_VERSION`)
2. `git add . && git commit -m "..." && git push`
3. Run `build_exe.bat` (and optionally compile `installer.iss`)
4. GitHub repo → **Releases** → **Create a new release** → tag it (e.g. `v1.1.0`)
   → attach `dist\BungusTweaks.exe` (or `Output\BungusTweaks-Setup.exe`) →
   **Publish release**
