import customtkinter as ctk
from pages.widgets import Card, SectionHeader, TweakRow, LogConsole, ACCENT
from core import system_info, launchers, nvidia_inspector, runner, state, history, value_extract
from data.tweaks_data import TWEAKS
from data.vendor_tweaks import NVIDIA_TWEAKS, AMD_TWEAKS, CPU_TWEAKS


def _find_tweak(category, key):
    return next(t for t in TWEAKS[category] if t["key"] == key)


class GamingPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._built = False

    def on_show(self):
        if not self._built:
            self._build()
            self._built = True

    def _build(self):
        outer = ctk.CTkScrollableFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=30, pady=24)

        SectionHeader(
            outer, "Gaming", "GPU/CPU tools, driver profiles, and tweaks tuned for gaming."
        ).pack(anchor="w", fill="x", pady=(0, 16))

        gpu_vendor = system_info.get_gpu_vendor()
        gpu_name = system_info.get_gpu_name()
        cpu_vendor = system_info.get_cpu_vendor()

        # ---------- detected hardware + vendor tools ----------
        detect_row = ctk.CTkFrame(outer, fg_color="transparent")
        detect_row.pack(fill="x", pady=(0, 16))
        detect_row.grid_columnconfigure((0, 1), weight=1)

        gpu_card = Card(detect_row)
        gpu_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(gpu_card, text="◈ Your GPU", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", padx=18, pady=(16, 4)
        )
        ctk.CTkLabel(gpu_card, text=gpu_name, font=("Segoe UI", 12), text_color="#D1D5DB").pack(
            anchor="w", padx=18, pady=(0, 12)
        )
        gpu_btn_row = ctk.CTkFrame(gpu_card, fg_color="transparent")
        gpu_btn_row.pack(fill="x", padx=18, pady=(0, 16))
        if gpu_vendor == "nvidia":
            ctk.CTkButton(gpu_btn_row, text="Open NVIDIA App", fg_color=ACCENT,
                          command=lambda: self._launch("nvidia_app")).pack(side="left", padx=(0, 8))
            ctk.CTkButton(gpu_btn_row, text="Control Panel", fg_color="#374151",
                          command=lambda: self._launch("nvidia_control_panel")).pack(side="left")
        elif gpu_vendor == "amd":
            ctk.CTkButton(gpu_btn_row, text="Open AMD Adrenalin", fg_color=ACCENT,
                          command=lambda: self._launch("amd_adrenalin")).pack(side="left")
        elif gpu_vendor == "intel":
            ctk.CTkButton(gpu_btn_row, text="Open Intel Graphics Center", fg_color=ACCENT,
                          command=lambda: self._launch("intel_graphics")).pack(side="left")
        else:
            ctk.CTkLabel(gpu_btn_row, text="No supported GPU vendor tool detected.",
                        font=("Segoe UI", 11), text_color="#9CA3AF").pack(anchor="w")

        cpu_card = Card(detect_row)
        cpu_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(cpu_card, text="◆ Your CPU", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", padx=18, pady=(16, 4)
        )
        cpu_label = {"amd": "AMD processor detected", "intel": "Intel processor detected"}.get(
            cpu_vendor, "Processor vendor not detected"
        )
        ctk.CTkLabel(cpu_card, text=cpu_label, font=("Segoe UI", 12), text_color="#D1D5DB").pack(
            anchor="w", padx=18, pady=(0, 12)
        )
        ctk.CTkLabel(
            cpu_card,
            text="CPU overclocking/undervolting needs your motherboard's BIOS or vendor tools "
                 "(AMD Ryzen Master / Intel XTU) - not something this app touches directly.",
            font=("Segoe UI", 11), text_color="#9CA3AF", wraplength=280, justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 16))

        # ---------- overclocking note + safe launcher ----------
        oc_card = Card(outer)
        oc_card.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(oc_card, text="▲ GPU Auto-Tuning", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", padx=18, pady=(16, 4)
        )
        ctk.CTkLabel(
            oc_card,
            text="We don't build our own overclock scanner — pushing voltage/clocks safely needs deep "
                 "vendor driver access (NVAPI/ADL) that a hobby tool shouldn't be reinventing. Instead, "
                 "here's a one-click launch into tools that already do this properly:",
            font=("Segoe UI", 12), text_color="#9CA3AF", wraplength=900, justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 10))
        oc_btn_row = ctk.CTkFrame(oc_card, fg_color="transparent")
        oc_btn_row.pack(fill="x", padx=18, pady=(0, 16))
        ctk.CTkButton(oc_btn_row, text="Launch MSI Afterburner", fg_color="#374151",
                      command=lambda: self._launch("msi_afterburner")).pack(side="left", padx=(0, 8))
        if gpu_vendor == "nvidia":
            ctk.CTkButton(oc_btn_row, text="NVIDIA App Auto-Tune", fg_color="#374151",
                          command=lambda: self._launch("nvidia_app")).pack(side="left", padx=(0, 8))
        elif gpu_vendor == "amd":
            ctk.CTkButton(oc_btn_row, text="AMD Adrenalin Auto-Tune", fg_color="#374151",
                          command=lambda: self._launch("amd_adrenalin")).pack(side="left")

        # ---------- NVIDIA Inspector profiles ----------
        if gpu_vendor == "nvidia":
            nvp_card = Card(outer)
            nvp_card.pack(fill="x", pady=(0, 16))
            ctk.CTkLabel(nvp_card, text="▤ NVIDIA Driver Profiles", font=("Segoe UI", 14, "bold")).pack(
                anchor="w", padx=18, pady=(16, 4)
            )
            ctk.CTkLabel(
                nvp_card,
                text="Imports a pre-built NVIDIA Profile Inspector profile (driver-level game settings "
                     "like texture filtering, shader cache, and sharpening). Auto-detected if you drop "
                     "nvidiaProfileInspector.exe into tools/nvidiaProfileInspector/ - or set a custom path in Settings.",
                font=("Segoe UI", 12), text_color="#9CA3AF", wraplength=900, justify="left",
            ).pack(anchor="w", padx=18, pady=(0, 10))

            nvp_btn_row = ctk.CTkFrame(nvp_card, fg_color="transparent")
            nvp_btn_row.pack(fill="x", padx=18, pady=(0, 8))
            ctk.CTkButton(nvp_btn_row, text="Apply Desktop Profile", fg_color=ACCENT,
                          command=lambda: self._apply_nvidia_profile("Desktop")).pack(side="left", padx=(0, 8))
            ctk.CTkButton(nvp_btn_row, text="Apply Laptop Profile", fg_color=ACCENT,
                          command=lambda: self._apply_nvidia_profile("Laptop")).pack(side="left")

            self.nvp_console = LogConsole(nvp_card, height=70)
            self.nvp_console.pack(fill="x", padx=18, pady=(4, 16))
            if not nvidia_inspector.is_configured():
                self.nvp_console.log(
                    "⚠ Drop nvidiaProfileInspector.exe into tools/nvidiaProfileInspector/, "
                    "or set a custom path in Settings."
                )

        self.console = LogConsole(outer, height=120)

        # ---------- GPU tweaks ----------
        ctk.CTkLabel(outer, text="GPU TWEAKS", font=("Segoe UI", 12, "bold"),
                     text_color="#9CA3AF").pack(anchor="w", pady=(4, 8))
        gpu_tweaks = [_find_tweak("Power", "enable_gpu_scheduling")]
        if gpu_vendor == "nvidia":
            gpu_tweaks += NVIDIA_TWEAKS
        elif gpu_vendor == "amd":
            gpu_tweaks += AMD_TWEAKS
        self._render_tweak_rows(outer, gpu_tweaks)

        # ---------- CPU tweaks ----------
        ctk.CTkLabel(outer, text="CPU TWEAKS", font=("Segoe UI", 12, "bold"),
                     text_color="#9CA3AF").pack(anchor="w", pady=(16, 8))
        cpu_tweaks = [_find_tweak("Power", "min_processor_state_100")] + CPU_TWEAKS
        self._render_tweak_rows(outer, cpu_tweaks)

        # ---------- general gaming + input tweaks ----------
        ctk.CTkLabel(outer, text="GENERAL GAMING & INPUT TWEAKS", font=("Segoe UI", 12, "bold"),
                     text_color="#9CA3AF").pack(anchor="w", pady=(16, 8))
        self._render_tweak_rows(outer, TWEAKS["Gaming"])

        self.console.pack(fill="x", pady=(12, 0))

    def _render_tweak_rows(self, parent, tweaks):
        for tweak in tweaks:
            is_on = state.is_tweak_applied(tweak["key"])
            row = TweakRow(
                parent, tweak["name"], tweak["description"], tweak["warning"],
                is_on, on_toggle=lambda on, r, t=tweak: self._on_toggle(on, r, t),
                risk=tweak.get("risk", "safe"), tweak=tweak,
            )
            row.pack(fill="x", pady=6)

    def _launch(self, tool_key):
        success, message = launchers.launch_tool(tool_key)
        self.console.log(("✔ " if success else "→ ") + message)

    def _apply_nvidia_profile(self, name):
        success, message = nvidia_inspector.apply_profile(name)
        self.nvp_console.log(("✔ " if success else "✘ ") + message)
        if success:
            self.app.mark_changed(f"NVIDIA {name} Profile — Applied")

    def _on_toggle(self, turning_on, row, tweak):
        row.set_enabled(False)
        self.console.log(f"— {'Applying' if turning_on else 'Reverting'}: {tweak['name']} —")
        commands = tweak["apply"] if turning_on else tweak["revert"]

        def on_done(success, errors):
            row.set_enabled(True)
            if success:
                state.set_tweak_applied(tweak["key"], turning_on)
                default_val, recommended_val = value_extract.get_default_and_recommended(tweak)
                new_val = recommended_val if turning_on else default_val
                history.log_change(
                    tweak["key"], tweak["name"], "applied" if turning_on else "reverted",
                    "Gaming", default_val, new_val,
                )
                self.app.mark_changed(f"{tweak['name']} — {'Applied' if turning_on else 'Reverted'}")
                self.console.log(f"✔ {tweak['name']} {'applied' if turning_on else 'reverted'}.\n")
            else:
                row.set_state(not turning_on)
                self.console.log("✘ Failed — is the app running as Administrator?\n")

        if not runner.is_admin():
            self.console.log("⚠ Not running as Administrator — this tweak may not apply.\n")

        runner.run_commands(commands, on_line=self.console.log, on_done=on_done)
