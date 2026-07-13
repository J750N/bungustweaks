import customtkinter as ctk
from tkinter import filedialog
from pages.widgets import Card, SectionHeader, LogConsole, ACCENT
from core import theme, startup, state, runner, nvidia_inspector, updates

APP_VERSION = "1.0.2"


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        outer = ctk.CTkScrollableFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=30, pady=24)

        SectionHeader(outer, "Settings", "Personalize how BungusTweaks looks and behaves.").pack(
            anchor="w", fill="x", pady=(0, 16)
        )

        # ---------- Appearance ----------
        appearance = Card(outer)
        appearance.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(appearance, text="Appearance", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", padx=18, pady=(16, 4)
        )
        ctk.CTkLabel(
            appearance, text="Pick an accent + dark palette theme. Applies instantly.",
            font=("Segoe UI", 12), text_color="#9CA3AF",
        ).pack(anchor="w", padx=18, pady=(0, 10))

        swatch_wrap = ctk.CTkFrame(appearance, fg_color="transparent")
        swatch_wrap.pack(fill="x", padx=18, pady=(0, 16))
        current = theme.get_theme_name()
        row = None
        for i, (name, preset) in enumerate(theme.PRESETS.items()):
            if i % 5 == 0:
                row = ctk.CTkFrame(swatch_wrap, fg_color="transparent")
                row.pack(fill="x", pady=(0, 10))
            self._build_swatch(row, name, preset["accent"], preset["accent2"], selected=(name == current))

        # ---------- Behavior ----------
        behavior = Card(outer)
        behavior.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(behavior, text="Behavior", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", padx=18, pady=(16, 8)
        )

        startup_row = ctk.CTkFrame(behavior, fg_color="transparent")
        startup_row.pack(fill="x", padx=18, pady=6)
        startup_row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(startup_row, text="Launch BungusTweaks with Windows", font=("Segoe UI", 13)).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(
            startup_row, text="Opens automatically when you sign in.",
            font=("Segoe UI", 11), text_color="#9CA3AF",
        ).grid(row=1, column=0, sticky="w")
        self.startup_var = ctk.BooleanVar(value=startup.is_startup_enabled())
        ctk.CTkSwitch(
            startup_row, text="", variable=self.startup_var, progress_color=ACCENT,
            command=self._toggle_startup,
        ).grid(row=0, column=1, rowspan=2, sticky="e")

        restart_row = ctk.CTkFrame(behavior, fg_color="transparent")
        restart_row.pack(fill="x", padx=18, pady=(6, 16))
        restart_row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(restart_row, text="Prompt to restart after applying tweaks", font=("Segoe UI", 13)).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(
            restart_row, text="Recommended — some tweaks only fully apply after a restart.",
            font=("Segoe UI", 11), text_color="#9CA3AF",
        ).grid(row=1, column=0, sticky="w")
        self.restart_prompt_var = ctk.BooleanVar(value=state.load_state().get("restart_prompt_enabled", True))
        ctk.CTkSwitch(
            restart_row, text="", variable=self.restart_prompt_var, progress_color=ACCENT,
            command=self._toggle_restart_prompt,
        ).grid(row=0, column=1, rowspan=2, sticky="e")

        # ---------- System Tools ----------
        tools = Card(outer)
        tools.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(tools, text="System Tools", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", padx=18, pady=(16, 8)
        )
        dism_row = ctk.CTkFrame(tools, fg_color="transparent")
        dism_row.pack(fill="x", padx=18, pady=(0, 12))
        dism_row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(dism_row, text="Run DISM & SFC Health Scan", font=("Segoe UI", 13)).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(
            dism_row, text="Finds and repairs corrupted Windows system files. Takes 10-20 minutes.",
            font=("Segoe UI", 11), text_color="#9CA3AF",
        ).grid(row=1, column=0, sticky="w")
        self.dism_button = ctk.CTkButton(
            dism_row, text="Run Scan", fg_color=ACCENT, width=110, command=self._run_dism_scan,
        )
        self.dism_button.grid(row=0, column=1, rowspan=2, sticky="e")

        self.console = LogConsole(tools, height=100)
        self.console.pack(fill="x", padx=18, pady=(0, 12))

        nvp_row = ctk.CTkFrame(tools, fg_color="transparent")
        nvp_row.pack(fill="x", padx=18, pady=(0, 16))
        nvp_row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(nvp_row, text="NVIDIA Profile Inspector path", font=("Segoe UI", 13)).grid(
            row=0, column=0, sticky="w"
        )
        if nvidia_inspector.is_bundled():
            path_text = f"✔ Auto-detected: {nvidia_inspector.get_inspector_path()}"
        else:
            path_text = (nvidia_inspector.get_inspector_path()
                         or "Not set — drop it in tools/nvidiaProfileInspector/ or browse below")
        self.nvp_path_label = ctk.CTkLabel(
            nvp_row, text=path_text, font=("Segoe UI", 11), text_color="#9CA3AF",
            wraplength=520, justify="left",
        )
        self.nvp_path_label.grid(row=1, column=0, sticky="w")
        ctk.CTkButton(nvp_row, text="Browse…", width=90, fg_color="#374151",
                      command=self._browse_inspector_path).grid(row=0, column=1, rowspan=2, sticky="e")

        # ---------- Community & Support ----------
        community = Card(outer)
        community.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(community, text="Community & Support", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", padx=18, pady=(16, 4)
        )
        ctk.CTkLabel(
            community, text="Need help, found a bug, or just want to say hi? Check out my profile.",
            font=("Segoe UI", 12), text_color="#9CA3AF",
        ).pack(anchor="w", padx=18, pady=(0, 10))
        ctk.CTkButton(
            community, text="guns.lol/stinkybungus", fg_color=ACCENT,
            command=lambda: __import__("webbrowser").open("https://guns.lol/stinkybungus"),
        ).pack(anchor="w", padx=18, pady=(0, 16))

        # ---------- About ----------
        about = Card(outer)
        about.pack(fill="x")
        about_header = ctk.CTkFrame(about, fg_color="transparent")
        about_header.pack(fill="x", padx=18, pady=(16, 4))
        ctk.CTkLabel(about_header, text="About", font=("Segoe UI", 14, "bold")).pack(side="left")
        self.update_button = ctk.CTkButton(
            about_header, text="Check for Updates", fg_color="#374151", width=140,
            command=self._check_for_updates,
        )
        self.update_button.pack(side="right")
        ctk.CTkLabel(
            about, text=f"BungusTweaks v{APP_VERSION}\nFree & open source Windows tuning tool.",
            font=("Segoe UI", 12), text_color="#9CA3AF", justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 8))

        self.update_result_frame = ctk.CTkFrame(about, fg_color="transparent")
        self.update_result_frame.pack(fill="x", padx=18, pady=(0, 16))

    def _check_for_updates(self):
        self.update_button.configure(text="Checking…", state="disabled")
        for w in self.update_result_frame.winfo_children():
            w.destroy()

        def worker():
            result = updates.check_for_update(APP_VERSION)
            self.after(0, lambda: self._show_update_result(result))

        import threading
        threading.Thread(target=worker, daemon=True).start()

    def _show_update_result(self, result):
        self.update_button.configure(text="Check for Updates", state="normal")

        if result is None:
            ctk.CTkLabel(
                self.update_result_frame,
                text="Couldn't check for updates — no internet connection, or GitHub is unreachable.",
                font=("Segoe UI", 12), text_color="#9CA3AF", wraplength=500, justify="left",
            ).pack(anchor="w")
            return

        if not result["available"]:
            ctk.CTkLabel(
                self.update_result_frame, text=f"✔ You're up to date (v{APP_VERSION}).",
                font=("Segoe UI", 12), text_color="#22C55E",
            ).pack(anchor="w")
            return

        ctk.CTkLabel(
            self.update_result_frame,
            text=f"🔔 {result['latest_version']} is available (you have v{APP_VERSION})",
            font=("Segoe UI", 13, "bold"), text_color=ACCENT,
        ).pack(anchor="w", pady=(0, 6))

        if result["notes"]:
            preview = result["notes"][:280] + ("…" if len(result["notes"]) > 280 else "")
            ctk.CTkLabel(
                self.update_result_frame, text=preview, font=("Segoe UI", 11),
                text_color="#9CA3AF", wraplength=500, justify="left",
            ).pack(anchor="w", pady=(0, 8))

        ctk.CTkButton(
            self.update_result_frame, text="View & Download", fg_color=ACCENT,
            command=lambda: __import__("webbrowser").open(result["url"]),
        ).pack(anchor="w")

    def _build_swatch(self, master, name, c1, c2, selected):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.pack(side="left", padx=(0, 14))

        canvas = ctk.CTkCanvas(frame, width=48, height=48, highlightthickness=2,
                                highlightbackground=ACCENT if selected else "#26262b", bd=0)
        canvas.pack()
        steps = 24
        for i in range(steps):
            t = i / (steps - 1)
            r = int(int(c1[1:3], 16) * (1 - t) + int(c2[1:3], 16) * t)
            g = int(int(c1[3:5], 16) * (1 - t) + int(c2[3:5], 16) * t)
            b = int(int(c1[5:7], 16) * (1 - t) + int(c2[5:7], 16) * t)
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_rectangle(i * (48 / steps), 0, (i + 1) * (48 / steps) + 1, 48,
                                     fill=color, outline=color)
        canvas.bind("<Button-1>", lambda e, n=name: self._select_theme(n))

        ctk.CTkLabel(frame, text=name, font=("Segoe UI", 10), text_color="#9CA3AF").pack(pady=(4, 0))

    def _select_theme(self, name):
        theme.set_theme(name)
        self.app.apply_theme_live()

    def _toggle_startup(self):
        if self.startup_var.get():
            ok = startup.enable_startup()
            self.console.log("✔ Will launch with Windows." if ok else "✘ Failed to set startup entry.")
        else:
            ok = startup.disable_startup()
            self.console.log("✔ Removed from Windows startup." if ok else "✘ Failed to remove startup entry.")

    def _toggle_restart_prompt(self):
        s = state.load_state()
        s["restart_prompt_enabled"] = self.restart_prompt_var.get()
        state.save_state(s)

    def _browse_inspector_path(self):
        path = filedialog.askopenfilename(
            title="Locate nvidiaProfileInspector.exe",
            filetypes=[("Executable", "*.exe")],
        )
        if path:
            nvidia_inspector.set_inspector_path(path)
            self.nvp_path_label.configure(text=path)

    def _run_dism_scan(self):
        self.dism_button.configure(text="Running…", state="disabled")
        self.console.log("— Running DISM & SFC health scan (this can take a while) —")

        def on_done(success, errors):
            self.dism_button.configure(text="Run Scan", state="normal")
            self.console.log("✔ Scan complete." if success else "✘ Scan completed with some errors — see above.")

        runner.run_commands(
            ["DISM /Online /Cleanup-Image /RestoreHealth", "sfc /scannow"],
            on_line=self.console.log, on_done=on_done,
        )
