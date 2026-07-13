import customtkinter as ctk
from pages.widgets import SectionHeader, TweakRow, LogConsole
from core import runner, state, history, value_extract


class TweakCategoryPage(ctk.CTkFrame):
    """A page showing one or more sections of toggleable tweaks.

    sections: list of (section_title_or_None, tweaks_list) tuples.
    Pass a single (None, tweaks_list) for a plain category page, or multiple
    titled sections (e.g. "Safe" / "Advanced") for something like Services.
    """

    def __init__(self, master, app, title, subtitle, sections):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.title_text = title
        self.subtitle_text = subtitle
        self.sections = sections
        self._built = False

    def on_show(self):
        if not self._built:
            self._build()
            self._built = True

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=30, pady=24)

        SectionHeader(outer, self.title_text, self.subtitle_text).pack(
            anchor="w", fill="x", pady=(0, 8)
        )

        legend = ctk.CTkFrame(outer, fg_color="transparent")
        legend.pack(anchor="w", pady=(0, 12))
        for color, text in [("#22C55E", "Safe"), ("#F59E0B", "Slightly risky"), ("#EF4444", "Risky")]:
            item = ctk.CTkFrame(legend, fg_color="transparent")
            item.pack(side="left", padx=(0, 16))
            ctk.CTkLabel(item, text="●", text_color=color, font=("Segoe UI", 12)).pack(side="left")
            ctk.CTkLabel(item, text=f" {text}", font=("Segoe UI", 12), text_color="#9CA3AF").pack(
                side="left"
            )

        scroll = ctk.CTkScrollableFrame(outer, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for section_title, tweaks in self.sections:
            if section_title:
                ctk.CTkLabel(
                    scroll, text=section_title.upper(), font=("Segoe UI", 12, "bold"),
                    text_color="#9CA3AF",
                ).pack(anchor="w", pady=(10, 4))
            for tweak in tweaks:
                is_on = state.is_tweak_applied(tweak["key"])
                row = TweakRow(
                    scroll, tweak["name"], tweak["description"], tweak["warning"],
                    is_on, on_toggle=lambda on, r, t=tweak: self._on_toggle(on, r, t),
                    risk=tweak.get("risk", "safe"), tweak=tweak,
                )
                row.pack(fill="x", pady=6)

        self.console = LogConsole(outer, height=130)
        self.console.pack(fill="x", pady=(12, 0))

    def _on_toggle(self, turning_on, row, tweak):
        row.set_enabled(False)
        action_word = "Applying" if turning_on else "Reverting"
        self.console.log(f"— {action_word}: {tweak['name']} —")

        commands = tweak["apply"] if turning_on else tweak["revert"]

        def on_done(success, errors):
            row.set_enabled(True)
            if success:
                state.set_tweak_applied(tweak["key"], turning_on)
                default_val, recommended_val = value_extract.get_default_and_recommended(tweak)
                new_val = recommended_val if turning_on else default_val
                history.log_change(
                    tweak["key"], tweak["name"], "applied" if turning_on else "reverted",
                    self.title_text, default_val, new_val,
                )
                self.app.mark_changed(f"{tweak['name']} — {'Applied' if turning_on else 'Reverted'}")
                self.console.log(f"✔ {tweak['name']} {'applied' if turning_on else 'reverted'}.\n")
            else:
                row.set_state(not turning_on)
                self.console.log("✘ Failed — is the app running as Administrator?\n")

        if not runner.is_admin():
            self.console.log("⚠ Not running as Administrator — this tweak may not apply. "
                              "Click the admin button in the sidebar to elevate.\n")

        runner.run_commands(commands, on_line=self.console.log, on_done=on_done)
