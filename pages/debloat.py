import customtkinter as ctk
import urllib.parse
from pages.widgets import SectionHeader, DualActionRow, LogConsole, confirm_dialog, ACCENT
from core import runner
from data.debloat_data import BLOAT_APPS


class DebloatPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=30, pady=24)

        SectionHeader(
            outer, "Debloat",
            "Remove pre-installed Windows apps you don't use. This only removes the app — no personal files. "
            "Removed something by accident? Hit Reinstall to get it back.",
        ).pack(anchor="w", fill="x", pady=(0, 12))

        scroll = ctk.CTkScrollableFrame(outer, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self.rows = {}
        for app_info in BLOAT_APPS:
            row = DualActionRow(
                scroll, app_info["name"], app_info["description"],
                primary_text="Remove", on_primary=lambda a=app_info: self._confirm_remove(a),
                secondary_text="Reinstall", on_secondary=lambda a=app_info: self._reinstall(a),
            )
            row.pack(fill="x", pady=6)
            self.rows[app_info["key"]] = row

        self.console = LogConsole(outer, height=140)
        self.console.pack(fill="x", pady=(12, 0))

    def _confirm_remove(self, app_info):
        confirm_dialog(
            self, "Remove app?",
            f"Remove {app_info['name']}? You can hit Reinstall any time to get it back from the Microsoft Store.",
            on_yes=lambda: self._remove(app_info),
        )

    def _remove(self, app_info):
        row = self.rows[app_info["key"]]
        row.set_primary("Removing…", enabled=False)
        self.console.log(f"— Removing {app_info['name']} —")

        pkg = app_info["package"]
        commands = [
            f'powershell -Command "Get-AppxPackage *{pkg}* | Remove-AppxPackage -ErrorAction SilentlyContinue"',
            f'powershell -Command "Get-AppxProvisionedPackage -Online | Where-Object DisplayName -like \'*{pkg}*\' '
            f'| Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue"',
        ]

        def on_done(success, errors):
            if success:
                row.set_primary("Removed", color="#374151", enabled=False)
                self.app.mark_changed(f"{app_info['name']} — Removed")
                self.console.log(f"✔ {app_info['name']} removed.\n")
            else:
                row.set_primary("Remove", color=ACCENT, enabled=True)
                self.console.log(f"✘ Could not fully remove {app_info['name']} (it may already be gone).\n")

        runner.run_commands(commands, on_line=self.console.log, on_done=on_done)

    def _reinstall(self, app_info):
        """Opens the Microsoft Store search for this app. We deliberately don't guess exact
        Store product IDs (getting one wrong could silently point at the wrong app) - a search
        deep-link always works and puts the real Install button one click away."""
        row = self.rows[app_info["key"]]
        query = urllib.parse.quote(app_info["name"])
        command = f'start "" "ms-windows-store://search/?query={query}"'
        self.console.log(f"→ Opening Microsoft Store search for {app_info['name']}…")

        def on_done(success, errors):
            if success:
                row.set_primary("Remove", color=ACCENT, enabled=True)
                self.console.log(f"✔ Store opened — click Install there to bring {app_info['name']} back.\n")
            else:
                self.console.log(f"✘ Couldn't open the Microsoft Store.\n")

        runner.run_commands([command], on_line=self.console.log, on_done=on_done)
