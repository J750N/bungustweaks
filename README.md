# BungusTweaks

A free, beginner-friendly Windows tuning tool with a real interactive GUI
(no black CMD window) — inspired by tools like LuminApp / EXM Tweaks.

## Features

- **Home** — live rolling line graphs for CPU, Memory, and Disk, plus PC specs
  and quick actions
- **Sidebar-first navigation** — every tweak category (Core, Privacy, Power,
  Network, Explorer & UI, Storage, Services, Advanced) is its own sidebar
  entry grouped under "Tweaks", instead of being buried in tabs
- **Services** — a dedicated page for background Windows services, split into
  "Safe" (low downside) and "Advanced" (real tradeoffs) groups
- **Gaming** — detects your GPU/CPU vendor, one-click launches into NVIDIA
  App / AMD Adrenalin / Intel Graphics Center / MSI Afterburner, imports
  bundled NVIDIA Profile Inspector driver profiles, plus gaming + input
  device tweaks
- **Debloat** — one-click removal of pre-installed Windows apps
- **Backup** — System Restore Points or registry key exports, so you can
  always undo everything
- **Fixes** — one-click repairs: reset network, fix audio, fix Windows
  Update, run SFC/DISM, clear temp files, restore Bluetooth/clipboard
- **System Info** — dedicated page with clean label/value rows for every
  piece of hardware/software info
- **Settings** — 8 accent + dark-palette theme presets, "Launch with
  Windows" toggle, restart-prompt toggle, DISM/SFC health scan, and a
  Discord link
- **Restart-on-close prompts** — closing the app checks if anything changed
  this session and asks to restart (or tells you it's safe to just close)
- **Custom icon & branding** — transparent silver-gradient "B" monogram that
  matches any theme color behind it

## GPU auto-tuning — why there's no built-in overclock scanner

We intentionally don't build a homemade "test values and pick the best one"
GPU/CPU overclocker. Doing that safely needs direct NVAPI/ADL vendor driver
access, and pushing voltage/clock combinations automatically can crash or
occasionally stress hardware if done wrong — not something a hobby tool
should reinvent. Instead, the Gaming page detects your GPU vendor and gives
you one-click launchers straight into the tools built for this (MSI
Afterburner, the NVIDIA App's Scanner, AMD Adrenalin's auto-tuning) — same
convenience, none of the homemade risk.

## Setting up NVIDIA Profile Inspector (optional)

The Gaming page can import pre-built driver profiles (texture filtering,
shader cache, sharpening, etc.) using
[nvidiaProfileInspector](https://github.com/Orbmu2k/nvidiaProfileInspector) —
a well-known free third-party tool. We don't bundle its `.exe` (that's
Orbmu2k's project, not ours) — download it yourself, then in
**Settings → System Tools → NVIDIA Profile Inspector path**, browse to
wherever you saved `nvidiaProfileInspector.exe`. After that, the "Apply
Desktop Profile" / "Apply Laptop Profile" buttons on the Gaming page will
work.

## Requirements

- Windows 10 or 11
- Python 3.10+
- Run the app **as Administrator** so registry/service tweaks actually apply
  (the app shows a warning and lets you elevate with one click if you didn't)

## Setup

```powershell
cd pc-tweaker
pip install -r requirements.txt
python app.py
```

The app will detect if it's not running elevated and show a button in the
bottom-left of the sidebar to relaunch as Administrator.

## Running it in VS Code

1. **Open the folder** — `File → Open Folder…` and select the `pc-tweaker`
   folder (the one containing `app.py`).
2. **Install the Python extension** (by Microsoft) if you don't already have
   it — VS Code will usually prompt you to install it automatically when it
   opens a `.py` file.
3. **Select a Python interpreter** — press `Ctrl+Shift+P`, type
   `Python: Select Interpreter`, and choose your installed Python 3.10+
   (make sure it's the Windows Python, not WSL, so the Windows-only
   commands work).
4. **Open a terminal in VS Code** — `` Ctrl+` `` (backtick), or
   `Terminal → New Terminal`. This opens a terminal already inside the
   project folder.
5. **Install dependencies** — in that terminal run:
   ```powershell
   pip install -r requirements.txt
   ```
6. **Run it** — either:
   - Open `app.py` and press the ▶ "Run Python File" button in the top-right, **or**
   - Type in the terminal:
     ```powershell
     python app.py
     ```
7. **For tweaks to actually apply**, close the app, then reopen your VS Code
   terminal **as Administrator** (search "VS Code" in the Start Menu, right
   click → "Run as administrator", then re-open the folder) and run
   `python app.py` again from that elevated terminal — or just click the
   "⚠ Not Admin — click to elevate" button in the app's sidebar, which
   relaunches the whole app elevated for you.

> Tip: if VS Code shows a squiggly underline under `import customtkinter`
> before you've installed dependencies, that's expected — it'll go away
> once step 5 finishes.

## Project structure

```
pc-tweaker/
  app.py                 # main window + sidebar navigation
  core/
    runner.py             # runs commands in a background thread, admin check/elevate
    state.py               # remembers which tweaks are on/off between launches
    backup.py               # restore point + registry export/import
    system_info.py           # psutil-based live stats for the Home page
  data/
    tweaks_data.py          # the actual reg/powershell commands per tweak
    debloat_data.py           # list of removable bundled apps
    fixes_data.py               # one-click repair command sets
  pages/
    home.py, tweaks.py, debloat.py, backup_page.py, fixes.py
    widgets.py               # shared Card/TweakRow/LogConsole/ConfirmDialog components
```

## Adding your own tweak

Open `data/tweaks_data.py` and add an entry to the right category list:

```python
{
    "key": "my_unique_key",
    "name": "My Tweak Name",
    "description": "One sentence explaining what it does.",
    "warning": None,               # or a short string shown in orange
    "apply":  ['reg add "HKCU\\..." /v X /t REG_DWORD /d 1 /f'],
    "revert": ['reg add "HKCU\\..." /v X /t REG_DWORD /d 0 /f'],
},
```

The toggle switch, on/off state persistence, and log console are handled
automatically — no UI code needed.

Adding a debloat entry or a fix works the same way: add a dict to
`debloat_data.py` / `fixes_data.py`.

## Do people need to install Python / tkinter to run this?

**While you're developing it** (running `python app.py`) — yes, they need
Python with tkinter, plus `pip install -r requirements.txt`. That's what
you've been doing in VS Code.

**Once you package it as an .exe** — no. A packaged `.exe` has Python,
tkinter, customtkinter, and everything else bundled inside it. Anyone can
double-click it on any Windows 10/11 PC with nothing pre-installed, exactly
like LuminApp.exe or EXM.exe in your screenshots.

### How to package it into BungusTweaks.exe

From inside the `pc-tweaker` folder, just double-click:

```
build_exe.bat
```

(or run it from a terminal: `.\build_exe.bat`). It will:
1. Install PyInstaller if you don't have it
2. Bundle the whole app + icon + assets into one file
3. Add `--uac-admin` so Windows automatically prompts for Administrator
   when someone double-clicks it (no manual "elevate" click needed)

When it finishes, your standalone app is at:

```
dist\BungusTweaks.exe
```

That single file is everything — copy it anywhere, send it to a friend, put
it on a USB stick. No Python, no pip, no tkinter needed on the other end.

> First build takes a minute or two and the .exe will be ~40-60MB (Python +
> tkinter + customtkinter all bundled in). That's normal for PyInstaller.

## Publishing this as an open-source project with a real installer

The full pipeline, once you're happy with the tweak list:

1. **Create the repo on GitHub** — go to https://github.com/J750N, click
   **New repository**, name it `bungustweaks` (public, so it's actually
   open source), and don't initialize it with a README (you already have one).

2. **Push the source**:
   ```powershell
   git init
   git add .
   git commit -m "Initial release"
   git branch -M main
   git remote add origin https://github.com/J750N/bungustweaks.git
   git push -u origin main
   ```
   The `.gitignore` already excludes build artifacts (`dist/`, `build/`,
   `Output/`) so only your actual source code gets committed — not the
   multi-megabyte compiled files. Anyone visiting
   `github.com/J750N/bungustweaks` will see every `.py` file, fully readable —
   that's what makes it genuinely open source, not just "free."

3. **Build the standalone exe** — run `build_exe.bat`. This creates
   `dist\BungusTweaks.exe`.

4. **Build the installer** — install [Inno Setup](https://jrsoftware.org/isdl.php)
   (free), then open `installer.iss` and press `Ctrl+F9` (Build → Compile).
   This produces `Output\BungusTweaks-Setup.exe` — a proper installer that:
   - Installs to `C:\Program Files\BungusTweaks`
   - Adds a Start Menu shortcut
   - Adds a Desktop shortcut (opt-out checkbox during install)
   - Has two **optional** checkboxes (unchecked by default) for companion
     apps: **installing MSI Afterburner via winget** (a real winget package,
     fetched live from its own source at install time - nothing bundled in
     this repo), and **opening the NVIDIA App's official download page**
     after setup. Note: the actual "NVIDIA App" isn't in the winget
     repository yet — NVIDIA's own manifest is blocked on their hardware-
     validation requirement (see
     [winget-pkgs#140696](https://github.com/microsoft/winget-pkgs/issues/140696)),
     so a fully silent NVIDIA App install isn't possible right now; opening
     the official page is the honest alternative to guessing at a
     direct-download URL that would go stale with every NVIDIA update.
   - Launches the app automatically once install finishes
   - Comes with a matching uninstaller (shows up in "Add or Remove Programs")

5. **Publish the installer as a GitHub Release** — go to
   `github.com/J750N/bungustweaks` → **Releases** → **Draft a new release** →
   attach `Output\BungusTweaks-Setup.exe` as a binary asset → publish.
   Now anyone can go to your GitHub page, click the Release, download
   `BungusTweaks-Setup.exe`, and double-click it — no Python, no manual
   copying files, no terminal. That single download IS the "setup" experience
   you're picturing, same as LuminApp/EXM's installers.

Your GitHub repo page shows the source code (fully open source, MIT
licensed via `LICENSE`), while the **Release** section is where people
actually get the installer to run it.

## Safety notes

- Every tweak has a colored risk dot and a hover tooltip explaining exactly
  what it does and how safe it is (🟢 safe / 🟡 moderate / 🔴 risky).
- The Backup page should be used before your first tweaking session —
  encourage users to click "Create Restore Point" first.
- All commands are plain, auditable strings in the `data/` files — nothing
  is downloaded or run from the internet, unlike some existing "tweak" tools.
