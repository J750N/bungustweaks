import customtkinter as ctk
from pages.widgets import SectionHeader, ActionRow, LogConsole, ACCENT
from core import runner, state
from data.install_apps_data import INSTALL_APPS


class InstallAppsPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._built = False

    def on_show(self):
        if not self._built:
            self._build()
            self._built = True

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=30, pady=24)

        SectionHeader(
            outer, "Install Apps",
            "One-click installs via winget (Windows' official package manager) - no bundled installers, "
            "straight from the source. Installed something by accident? Click it again to uninstall.",
        ).pack(anchor="w", fill="x", pady=(0, 12))

        scroll = ctk.CTkScrollableFrame(outer, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self.rows = {}
        for app_info in INSTALL_APPS:
            already_installed = state.load_state().get(f"installed_app_{app_info['key']}", False)
            row = ActionRow(
                scroll, app_info["name"], app_info["description"],
                "Uninstall" if already_installed else "Install",
                on_click=lambda a=app_info: self._toggle(a),
                button_color="#374151" if already_installed else ACCENT,
            )
            row.pack(fill="x", pady=6)
            self.rows[app_info["key"]] = row

        self.console = LogConsole(outer, height=140)
        self.console.pack(fill="x", pady=(12, 0))

    def _toggle(self, app_info):
        is_installed = state.load_state().get(f"installed_app_{app_info['key']}", False)
        if is_installed:
            self._uninstall(app_info)
        else:
            self._install(app_info)

    def _install(self, app_info):
        row = self.rows[app_info["key"]]
        row.set_button("Installing…", enabled=False)
        self.console.log(f"— Installing {app_info['name']} via winget —")

        command = (
            f'winget install --id {app_info["winget_id"]} -e --silent '
            f'--accept-package-agreements --accept-source-agreements'
        )

        def on_done(success, errors):
            if success:
                row.set_button("Uninstall", color="#374151", enabled=True)
                self.console.log(f"✔ {app_info['name']} installed.\n")
                s = state.load_state()
                s[f"installed_app_{app_info['key']}"] = True
                state.save_state(s)
                self.app.mark_changed(f"{app_info['name']} — Installed")
            else:
                row.set_button("Install", enabled=True)
                self.console.log(
                    f"✘ Couldn't install {app_info['name']} — is winget installed and up to date?\n"
                )

        runner.run_commands([command], on_line=self.console.log, on_done=on_done)

    def _uninstall(self, app_info):
        row = self.rows[app_info["key"]]
        row.set_button("Uninstalling…", enabled=False)
        self.console.log(f"— Uninstalling {app_info['name']} —")

        command = f'winget uninstall --id {app_info["winget_id"]} -e --silent'

        def on_done(success, errors):
            if success:
                row.set_button("Install", color=ACCENT, enabled=True)
                self.console.log(f"✔ {app_info['name']} uninstalled.\n")
                s = state.load_state()
                s[f"installed_app_{app_info['key']}"] = False
                state.save_state(s)
                self.app.mark_changed(f"{app_info['name']} — Uninstalled")
            else:
                row.set_button("Uninstall", color="#374151", enabled=True)
                self.console.log(f"✘ Couldn't uninstall {app_info['name']}.\n")

        runner.run_commands([command], on_line=self.console.log, on_done=on_done)
