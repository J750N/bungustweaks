"""
BungusTweaks — a free, beginner-friendly Windows tuning tool.
Run with: python app.py   (Windows only, run as Administrator for full effect)
"""

import sys
import os
import importlib

# --- Startup guard: catch missing tkinter/customtkinter early with a clear message
# instead of letting the console flash and close instantly. ---
try:
    import tkinter  # noqa: F401
except ImportError:
    print("=" * 60)
    print("ERROR: 'tkinter' is missing from this Python installation.")
    print()
    print("This usually happens with the Microsoft Store version of Python.")
    print("Fix:")
    print("  1. Uninstall the Store version of Python (optional but recommended)")
    print("  2. Install Python from https://www.python.org/downloads/")
    print("  3. During install, click 'Customize installation' and make sure")
    print("     'tcl/tk and IDLE' is checked")
    print("  4. Re-select this Python as your interpreter in VS Code")
    print("  5. Run: pip install -r requirements.txt")
    print("  6. Run: python app.py")
    print("=" * 60)
    input("\nPress Enter to close...")
    sys.exit(1)

try:
    import customtkinter as ctk
except ImportError:
    print("=" * 60)
    print("ERROR: 'customtkinter' is not installed.")
    print()
    print("Fix: run this in your terminal, inside the project folder:")
    print("  pip install -r requirements.txt")
    print("=" * 60)
    input("\nPress Enter to close...")
    sys.exit(1)


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import runner, state, backup, system_info, theme
from data.tweaks_data import TWEAKS
from data.debloat_data import BLOAT_APPS
from data.fixes_data import FIXES
from data.services_data import SERVICES

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT, ACCENT2 = theme.get_accent_colors()
SIDEBAR_BG, CONTENT_BG, CARD_BG = theme.get_bg_colors()
WARNING_COLOR = "#F59E0B"

# Category pages that get their own individual sidebar entry under "Tweaks"
# (Gaming is intentionally excluded here - it gets a richer dedicated page)
TWEAK_NAV_CATEGORIES = ["Core", "Privacy", "Power", "Network", "Explorer & UI", "Storage", "Advanced"]


def resource_path(relative_path):
    """Get an absolute path to a bundled resource, working both when run as a
    normal .py script and when packaged into a PyInstaller .exe."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def _mix_bg(color_hex):
    """Blends a status color into the sidebar background for a subtle 'pill' fill."""
    from pages.widgets import _mix
    return _mix(color_hex, SIDEBAR_BG, 0.82)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BungusTweaks")
        icon_path = resource_path(os.path.join("assets", "icon.ico"))
        if os.name == "nt" and os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass
        self.geometry("1200x760")
        self.minsize(980, 620)
        self.configure(fg_color=CONTENT_BG)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Tracks whether anything was changed this session, to decide what
        # to show when the user closes the app (restart prompt vs "all good").
        self.changes_made_this_session = False
        self.session_change_log = []

        self._build_sidebar()
        self._build_content_area()

        self.pages = {}
        self.current_page_name = "Home"
        self._register_pages()
        self.show_page("Home")

        self.protocol("WM_DELETE_WINDOW", self._on_close_request)
        self.after(400, self._maybe_prompt_elevate_on_launch)
        self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_out(self, event=None):
        # Only care about the whole app losing focus (e.g. Alt-Tab to another
        # program), not focus moving between widgets inside our own window.
        if event is not None and event.widget is not self:
            return
        from pages.widgets import close_all_tooltips
        close_all_tooltips()

    # ---------- state tracking ----------

    def mark_changed(self, description=None):
        """Call this whenever a tweak/fix/debloat action successfully changes something."""
        self.changes_made_this_session = True
        if description:
            self.session_change_log.append(description)

    # ---------- layout ----------

    def _nav_button(self, parent, name, icon):
        btn = ctk.CTkButton(
            parent, text=f"{icon}  {name}", anchor="w",
            fg_color="transparent", hover_color="#26262b",
            font=("Segoe UI", 13), height=36, corner_radius=8,
            command=lambda n=name: self.show_page(n),
        )
        btn.pack(fill="x", padx=12, pady=1)
        self.nav_buttons[name] = btn

    def _section_label(self, parent, text):
        ctk.CTkLabel(
            parent, text=text.upper(), font=("Segoe UI", 10, "bold"), text_color="#6B7280",
        ).pack(anchor="w", padx=16, pady=(16, 4))

    def _build_sidebar(self):
        from pages.widgets import GradientBar

        self.sidebar_scroll = ctk.CTkScrollableFrame(
            self, width=230, corner_radius=0, fg_color=SIDEBAR_BG,
        )
        self.sidebar_scroll.grid(row=0, column=0, sticky="nsew")

        logo_row = ctk.CTkFrame(self.sidebar_scroll, fg_color="transparent")
        logo_row.pack(fill="x", padx=16, pady=(18, 4))
        ctk.CTkLabel(logo_row, text="⬡", font=("Segoe UI", 20), text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(logo_row, text=" BUNGUSTWEAKS", font=("Segoe UI", 15, "bold")).pack(side="left")
        GradientBar(self.sidebar_scroll, height=3, bg=SIDEBAR_BG).pack(fill="x", padx=16, pady=(6, 8))

        # Admin status pill - right under the logo, the first thing you see
        is_admin_now = runner.is_admin()
        admin_text = "✔ Running as Administrator" if is_admin_now else "⚠ Not Admin — click to elevate"
        admin_color = "#22C55E" if is_admin_now else WARNING_COLOR
        self.admin_label = ctk.CTkButton(
            self.sidebar_scroll, text=admin_text, fg_color=_mix_bg(admin_color),
            text_color=admin_color, hover_color="#26262b",
            font=("Segoe UI", 11, "bold"), height=32, corner_radius=8,
            command=self._elevate_clicked,
        )
        self.admin_label.pack(fill="x", padx=16, pady=(0, 14))

        self.nav_buttons = {}

        self._section_label(self.sidebar_scroll, "General")
        for name, icon in [("Home", "⌂"), ("System Info", "▤"), ("Backup", "⇩"), ("Fixes", "◇")]:
            self._nav_button(self.sidebar_scroll, name, icon)

        self._section_label(self.sidebar_scroll, "Tweaks")
        category_icons = {
            "Core": "◆", "Privacy": "◐", "Power": "▲", "Network": "◎",
            "Explorer & UI": "▣", "Storage": "▥", "Services": "◉", "Advanced": "▨",
        }
        for name in TWEAK_NAV_CATEGORIES:
            self._nav_button(self.sidebar_scroll, name, category_icons.get(name, "•"))
        self._nav_button(self.sidebar_scroll, "Services", category_icons["Services"])
        self._nav_button(self.sidebar_scroll, "Debloat", "▽")
        self._nav_button(self.sidebar_scroll, "Install Apps", "⊕")
        self._nav_button(self.sidebar_scroll, "History", "↺")

        self._section_label(self.sidebar_scroll, "Gaming")
        self._nav_button(self.sidebar_scroll, "Gaming", "◈")

        self._section_label(self.sidebar_scroll, "App")
        self._nav_button(self.sidebar_scroll, "Changelog", "☰")
        self._nav_button(self.sidebar_scroll, "Settings", "▩")

    def _elevate_clicked(self):
        if runner.is_admin():
            return
        if runner.relaunch_as_admin():
            self.destroy()
        else:
            self._show_elevation_failed_dialog()

    def _show_elevation_failed_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Elevation cancelled")
        win.geometry("380x160")
        win.grab_set()
        ctk.CTkLabel(win, text="Couldn't restart as Administrator", font=("Segoe UI", 15, "bold")).pack(
            padx=20, pady=(20, 6), anchor="w"
        )
        ctk.CTkLabel(
            win, text="You may have clicked 'No' on the Windows permission prompt. "
                      "Click the button again and select 'Yes' this time.",
            font=("Segoe UI", 12), text_color="#9CA3AF", wraplength=340, justify="left",
        ).pack(padx=20, anchor="w")
        ctk.CTkButton(win, text="OK", fg_color=ACCENT, command=win.destroy).pack(
            padx=20, pady=20, fill="x"
        )

    def _maybe_prompt_elevate_on_launch(self):
        if runner.is_admin():
            return
        win = ctk.CTkToplevel(self)
        win.title("Administrator recommended")
        win.geometry("420x220")
        win.grab_set()
        ctk.CTkLabel(
            win, text="Run as Administrator?", font=("Segoe UI", 16, "bold"),
        ).pack(padx=24, pady=(24, 6), anchor="w")
        ctk.CTkLabel(
            win,
            text="Most tweaks, services, and fixes need Administrator privileges to actually apply. "
                 "You can restart elevated now, or continue and elevate later from the sidebar.",
            font=("Segoe UI", 12), text_color="#9CA3AF", wraplength=370, justify="left",
        ).pack(padx=24, anchor="w")

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(padx=24, pady=24, fill="x")

        def restart_as_admin():
            win.destroy()
            if runner.relaunch_as_admin():
                self.destroy()
            else:
                self._show_elevation_failed_dialog()

        ctk.CTkButton(btn_row, text="Restart as Administrator", fg_color=ACCENT,
                      command=restart_as_admin).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="Continue Anyway", fg_color="#374151",
                      command=win.destroy).pack(side="left")

    def _build_content_area(self):
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color=CONTENT_BG)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _register_pages(self):
        from pages.home import HomePage
        from pages.debloat import DebloatPage
        from pages.backup_page import BackupPage
        from pages.fixes import FixesPage
        from pages.system_info import SystemInfoPage
        from pages.settings import SettingsPage
        from pages.gaming import GamingPage
        from pages.tweak_category_page import TweakCategoryPage
        from pages.install_apps import InstallAppsPage
        from pages.history_page import HistoryPage
        from pages.changelog_page import ChangelogPage

        static_pages = [
            ("Home", HomePage), ("Debloat", DebloatPage), ("Install Apps", InstallAppsPage),
            ("History", HistoryPage), ("Backup", BackupPage),
            ("Fixes", FixesPage), ("System Info", SystemInfoPage),
            ("Settings", SettingsPage), ("Gaming", GamingPage), ("Changelog", ChangelogPage),
        ]
        for Name, PageClass in static_pages:
            page = PageClass(self.content, self)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[Name] = page

        category_subtitles = {
            "Core": "The essentials most people apply first.",
            "Privacy": "Control what Windows tracks and shares.",
            "Power": "Squeeze more performance out of your power plan.",
            "Network": "Lower latency, tune DNS, and reduce overhead.",
            "Explorer & UI": "Small quality-of-life tweaks to how Windows looks and behaves.",
            "Storage": "Keep your drives fast and free of clutter.",
            "Advanced": "Bigger tradeoffs — read every warning first.",
        }
        for category in TWEAK_NAV_CATEGORIES:
            page = TweakCategoryPage(
                self.content, self, category, category_subtitles.get(category, ""),
                sections=[(None, TWEAKS[category])],
            )
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[category] = page

        services_page = TweakCategoryPage(
            self.content, self, "Services",
            "Background Windows services you can safely turn off - or advanced ones with real tradeoffs.",
            sections=[("Safe", SERVICES["Safe"]), ("Advanced", SERVICES["Advanced"])],
        )
        services_page.grid(row=0, column=0, sticky="nsew")
        self.pages["Services"] = services_page

    def show_page(self, name):
        from pages.widgets import close_all_tooltips
        close_all_tooltips()

        self.current_page_name = name
        for n, btn in self.nav_buttons.items():
            btn.configure(fg_color=ACCENT if n == name else "transparent")
        self.pages[name].tkraise()
        if hasattr(self.pages[name], "on_show"):
            self.pages[name].on_show()

    def apply_theme_live(self):
        """Rebuilds the entire UI with the newly selected theme - no app restart needed.
        We reload every page module so their module-level ACCENT/CARD_BG/etc constants
        (which are bound once at import time) pick up the freshly saved theme colors."""
        global ACCENT, ACCENT2, SIDEBAR_BG, CONTENT_BG, CARD_BG

        modules_to_reload = [
            "pages.widgets", "pages.home", "pages.gaming", "pages.settings",
            "pages.tweak_category_page", "pages.debloat", "pages.fixes",
            "pages.backup_page", "pages.system_info", "pages.install_apps", "pages.history_page",
            "pages.changelog_page",
        ]
        for modname in modules_to_reload:
            mod = sys.modules.get(modname)
            if mod:
                importlib.reload(mod)

        ACCENT, ACCENT2 = theme.get_accent_colors()
        SIDEBAR_BG, CONTENT_BG, CARD_BG = theme.get_bg_colors()
        self.configure(fg_color=CONTENT_BG)

        remembered_page = self.current_page_name
        self.sidebar_scroll.destroy()
        self.content.destroy()

        self._build_sidebar()
        self._build_content_area()
        self.pages = {}
        self._register_pages()
        self.show_page(remembered_page if remembered_page in self.pages else "Home")

    # ---------- close / restart prompt ----------

    def _on_close_request(self):
        restart_prompt_enabled = state.load_state().get("restart_prompt_enabled", True)

        if not restart_prompt_enabled:
            self.destroy()
            return

        if self.changes_made_this_session:
            self._show_restart_dialog()
        else:
            self._show_no_changes_dialog()

    def _show_no_changes_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Nothing to do")
        win.geometry("360x160")
        win.grab_set()

        ctk.CTkLabel(win, text="No changes were made", font=("Segoe UI", 16, "bold")).pack(
            padx=24, pady=(24, 6), anchor="w"
        )
        ctk.CTkLabel(
            win, text="Nothing was applied this session — you're safe to close.",
            font=("Segoe UI", 12), text_color="#9CA3AF", wraplength=310, justify="left",
        ).pack(padx=24, anchor="w")

        ctk.CTkButton(win, text="Close BungusTweaks", fg_color=ACCENT, command=self.destroy).pack(
            padx=24, pady=24, fill="x"
        )

    def _show_restart_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Restart recommended")
        win.geometry("440x420")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", lambda: None)  # force a real choice

        ctk.CTkLabel(
            win, text="Some tweaks were changed", font=("Segoe UI", 16, "bold"),
        ).pack(padx=24, pady=(24, 6), anchor="w")
        ctk.CTkLabel(
            win,
            text="Restart your PC so every change takes full effect. "
                 "You can also restart later — nothing will be lost.",
            font=("Segoe UI", 12), text_color="#9CA3AF", wraplength=390, justify="left",
        ).pack(padx=24, anchor="w")

        ctk.CTkLabel(
            win, text=f"WHAT CHANGED THIS SESSION ({len(self.session_change_log)})",
            font=("Segoe UI", 10, "bold"), text_color="#6B7280",
        ).pack(padx=24, pady=(16, 4), anchor="w")

        list_frame = ctk.CTkScrollableFrame(win, fg_color="#0E0E10", height=140)
        list_frame.pack(padx=24, fill="both", expand=True)
        if self.session_change_log:
            for change in self.session_change_log:
                ctk.CTkLabel(
                    list_frame, text=f"•  {change}", font=("Segoe UI", 11),
                    text_color="#D1D5DB", anchor="w", justify="left",
                ).pack(fill="x", padx=8, pady=2, anchor="w")
        else:
            ctk.CTkLabel(list_frame, text="No details recorded.", text_color="#6B7280").pack(
                padx=8, pady=8
            )

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(padx=24, pady=16, fill="x")

        def restart_now():
            win.destroy()
            self.destroy()
            try:
                import subprocess
                subprocess.run("shutdown /r /t 5", shell=True)
            except Exception:
                pass

        def restart_later():
            win.destroy()
            self.destroy()

        ctk.CTkButton(btn_row, text="Restart Now", fg_color=ACCENT, command=restart_now).pack(
            side="left", padx=(0, 10)
        )
        ctk.CTkButton(btn_row, text="Restart Later", fg_color="#374151", command=restart_later).pack(
            side="left"
        )
        ctk.CTkButton(btn_row, text="Cancel", fg_color="transparent", hover_color="#26262b",
                      command=win.destroy).pack(side="right")


if __name__ == "__main__":
    if os.name != "nt":
        print("This tool is designed for Windows. Some tweaks will not run on this OS.")
    try:
        app = App()
        app.mainloop()
    except Exception:
        import traceback
        print("=" * 60)
        print("BungusTweaks crashed. Full error below:")
        print("=" * 60)
        traceback.print_exc()
        input("\nPress Enter to close...")
        sys.exit(1)
