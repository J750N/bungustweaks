import customtkinter as ctk
from pages.widgets import Card, SectionHeader, LogConsole, confirm_dialog, ACCENT, RISK_COLORS
from core import history, tweak_registry, runner, state


class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._built = False

    def on_show(self):
        if not self._built:
            self._build()
            self._built = True
        else:
            self._refresh_list()

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=30, pady=24)

        header_row = ctk.CTkFrame(outer, fg_color="transparent")
        header_row.pack(fill="x")
        SectionHeader(
            header_row, "History", "Every tweak/service change you've made, with one-click revert.",
        ).pack(side="left", anchor="w")
        ctk.CTkButton(
            header_row, text="Clear History", fg_color="#374151", width=110,
            command=self._confirm_clear,
        ).pack(side="right", pady=(8, 0))

        self.list_frame = ctk.CTkScrollableFrame(outer, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, pady=(16, 0))

        self.console = LogConsole(outer, height=100)
        self.console.pack(fill="x", pady=(12, 0))

        self._refresh_list()

    def _refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        entries = history.load_history()
        if not entries:
            ctk.CTkLabel(
                self.list_frame, text="No changes yet — anything you apply, revert, or fix will show up here.",
                text_color="#6B7280",
            ).pack(anchor="w", pady=20)
            return

        for entry in entries:
            self._build_entry_row(entry)

    def _build_entry_row(self, entry):
        row = Card(self.list_frame)
        row.pack(fill="x", pady=5)

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)
        inner.grid_columnconfigure(0, weight=1)

        title_row = ctk.CTkFrame(inner, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="w")
        action_color = "#22C55E" if entry["action"] == "applied" else "#9CA3AF"
        ctk.CTkLabel(title_row, text="●", text_color=action_color, font=("Segoe UI", 12)).pack(
            side="left", padx=(0, 6)
        )
        ctk.CTkLabel(title_row, text=entry["name"], font=("Segoe UI", 13, "bold")).pack(side="left")

        subtitle = (
            f"{entry['action'].capitalize()} in {entry['category']}  ·  "
            f"{history.format_timestamp(entry['timestamp'])}  ·  set to {entry['new_value']}"
        )
        ctk.CTkLabel(inner, text=subtitle, font=("Segoe UI", 11), text_color="#9CA3AF").grid(
            row=1, column=0, sticky="w", pady=(2, 0)
        )

        tweak = tweak_registry.get(entry["key"])
        btn_text = "Revert to Default" if entry["action"] == "applied" else "Re-Apply"
        btn = ctk.CTkButton(
            inner, text=btn_text, width=130, fg_color=ACCENT,
            command=lambda: self._confirm_undo(entry, tweak, btn),
        )
        btn.grid(row=0, column=1, rowspan=2, sticky="e", padx=(12, 0))
        if not tweak:
            btn.configure(state="disabled", text="Unavailable")

    def _confirm_undo(self, entry, tweak, btn):
        going_to = "revert" if entry["action"] == "applied" else "apply"
        confirm_dialog(
            self, "Confirm change",
            f"{'Revert' if going_to == 'revert' else 'Re-apply'} '{entry['name']}'?",
            on_yes=lambda: self._run_undo(entry, tweak, going_to, btn),
        )

    def _run_undo(self, entry, tweak, going_to, btn):
        btn.configure(state="disabled", text="Working…")
        commands = tweak["revert"] if going_to == "revert" else tweak["apply"]
        turning_on = going_to == "apply"

        def on_done(success, errors):
            if success:
                state.set_tweak_applied(tweak["key"], turning_on)
                from core import value_extract
                default_val, recommended_val = value_extract.get_default_and_recommended(tweak)
                new_val = recommended_val if turning_on else default_val
                history.log_change(
                    tweak["key"], tweak["name"], "applied" if turning_on else "reverted",
                    "History", default_val, new_val,
                )
                self.app.mark_changed(f"{tweak['name']} — {'Applied' if turning_on else 'Reverted'} (from History)")
                self.console.log(f"✔ {tweak['name']} {'applied' if turning_on else 'reverted'}.")
            else:
                self.console.log(f"✘ Failed to change {tweak['name']} — is the app running as Administrator?")
            self._refresh_list()

        if not runner.is_admin():
            self.console.log("⚠ Not running as Administrator — this may not apply.")

        runner.run_commands(commands, on_line=self.console.log, on_done=on_done)

    def _confirm_clear(self):
        confirm_dialog(
            self, "Clear history?",
            "This only clears the history log — it does not revert any tweaks.",
            on_yes=self._do_clear,
        )

    def _do_clear(self):
        history.clear_history()
        self._refresh_list()
