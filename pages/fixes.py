import customtkinter as ctk
from pages.widgets import SectionHeader, ActionRow, LogConsole, confirm_dialog
from core import runner
from data.fixes_data import FIXES


class FixesPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=30, pady=24)

        SectionHeader(
            outer, "Fixes",
            "Automatically detect and repair common Windows issues.",
        ).pack(anchor="w", fill="x", pady=(0, 12))

        scroll = ctk.CTkScrollableFrame(outer, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self.rows = {}
        for fix in FIXES:
            row = ActionRow(
                scroll, fix["name"], fix["description"], "Fix now",
                on_click=lambda f=fix: self._confirm_run(f),
            )
            row.pack(fill="x", pady=6)
            self.rows[fix["key"]] = row

        self.console = LogConsole(outer, height=140)
        self.console.pack(fill="x", pady=(12, 0))

    def _confirm_run(self, fix):
        msg = fix["description"]
        if fix["needs_restart"]:
            msg += "\n\nYou'll need to restart your PC afterwards for this to fully take effect."
        confirm_dialog(self, fix["name"], msg, on_yes=lambda: self._run(fix))

    def _run(self, fix):
        row = self.rows[fix["key"]]
        row.set_button("Running…", enabled=False)
        self.console.log(f"— Running: {fix['name']} —")

        if not runner.is_admin():
            self.console.log("⚠ Not running as Administrator — this fix may not fully apply.")

        def on_done(success, errors):
            row.set_button("Fix now", enabled=True)
            if success:
                self.app.mark_changed(f"{fix['name']} — Ran")
                self.console.log(f"✔ {fix['name']} completed.\n")
            else:
                self.console.log(f"✘ Completed with some errors — see log above.\n")

        runner.run_commands(fix["commands"], on_line=self.console.log, on_done=on_done)
