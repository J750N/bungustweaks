import customtkinter as ctk
import threading
from pages.widgets import Card, SectionHeader, HistoryGraph, ACCENT, ACCENT2
from core import system_info, state, history, updates
from data.tweaks_data import TWEAKS
from data.services_data import SERVICES
from pages.settings import APP_VERSION


class HomePage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()
        self._loop_running = False

    def _build(self):
        pad = ctk.CTkFrame(self, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=30, pady=24)

        SectionHeader(pad, "Home", "Live temps, usage, and quick actions").pack(
            anchor="w", fill="x", pady=(0, 16)
        )

        top = ctk.CTkFrame(pad, fg_color="transparent")
        top.pack(fill="x", pady=(0, 16))
        top.grid_columnconfigure((0, 1), weight=1)

        score_card = Card(top)
        score_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        applied = sum(
            1 for cat in TWEAKS.values() for t in cat if state.is_tweak_applied(t["key"])
        ) + sum(
            1 for cat in SERVICES.values() for t in cat if state.is_tweak_applied(t["key"])
        )
        total = sum(len(cat) for cat in TWEAKS.values()) + sum(len(cat) for cat in SERVICES.values())
        ctk.CTkLabel(score_card, text="TWEAKS APPLIED", font=("Segoe UI", 11), text_color="#9CA3AF").pack(
            anchor="w", padx=18, pady=(16, 0)
        )
        self.score_label = ctk.CTkLabel(
            score_card, text=f"{applied} / {total}", font=("Segoe UI", 32, "bold")
        )
        self.score_label.pack(anchor="w", padx=18, pady=(0, 16))

        specs_card = Card(top)
        specs_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        specs = system_info.get_static_specs()
        specs_header = ctk.CTkFrame(specs_card, fg_color="transparent")
        specs_header.pack(fill="x", padx=18, pady=(16, 4))
        ctk.CTkLabel(specs_header, text="THIS PC", font=("Segoe UI", 11), text_color="#9CA3AF").pack(
            side="left"
        )
        ctk.CTkButton(
            specs_header, text="Full System Info →", fg_color="transparent", hover_color="#26262b",
            text_color=ACCENT, font=("Segoe UI", 11), height=20, width=120,
            command=lambda: self.app.show_page("System Info"),
        ).pack(side="right")
        ctk.CTkLabel(
            specs_card,
            text=f"{specs['cpu']}\n{specs['cores']}C / {specs['threads']}T  ·  {specs['ram_gb']} GB RAM\n{specs['os']}",
            font=("Segoe UI", 13), justify="left", text_color="#D1D5DB",
        ).pack(anchor="w", padx=18, pady=(0, 16))

        # live rolling graphs (CPU / Memory / Disk), like the reference app's temp graphs
        graphs_row = ctk.CTkFrame(pad, fg_color="transparent")
        graphs_row.pack(fill="x", pady=(0, 16))
        graphs_row.grid_columnconfigure((0, 1, 2), weight=1, uniform="graphs")

        self.cpu_graph = HistoryGraph(graphs_row, "CPU Usage", unit="%", color=ACCENT)
        self.cpu_graph.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.mem_graph = HistoryGraph(graphs_row, "Memory Usage", unit="%", color=ACCENT2)
        self.mem_graph.grid(row=0, column=1, sticky="nsew", padx=8)

        self.disk_graph = HistoryGraph(graphs_row, "Disk Usage", unit="%", color="#F472B6")
        self.disk_graph.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        nav_card = Card(pad)
        nav_card.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(nav_card, text="QUICK ACTIONS", font=("Segoe UI", 11), text_color="#9CA3AF").pack(
            anchor="w", padx=18, pady=(16, 8)
        )
        btn_row = ctk.CTkFrame(nav_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(0, 16))
        for label, page in [("Apply Tweaks", "Core"), ("Debloat Apps", "Debloat"),
                             ("Create Backup", "Backup"), ("Run a Fix", "Fixes")]:
            ctk.CTkButton(
                btn_row, text=label, fg_color="#26262b", hover_color="#33333a",
                command=lambda p=page: self.app.show_page(p),
            ).pack(side="left", padx=(0, 10))

        whats_new_card = Card(pad)
        whats_new_card.pack(fill="x", pady=(0, 16))
        wn_header = ctk.CTkFrame(whats_new_card, fg_color="transparent")
        wn_header.pack(fill="x", padx=18, pady=(16, 8))
        ctk.CTkLabel(wn_header, text="WHAT'S NEW", font=("Segoe UI", 11), text_color="#9CA3AF").pack(
            side="left"
        )
        self.wn_version_label = ctk.CTkLabel(
            wn_header, text="", font=("Segoe UI", 11, "bold"), text_color=ACCENT,
        )
        self.wn_version_label.pack(side="right")

        self.wn_body = ctk.CTkFrame(whats_new_card, fg_color="transparent")
        self.wn_body.pack(fill="x", padx=18, pady=(0, 16))
        ctk.CTkLabel(
            self.wn_body, text="Checking for the latest release notes…",
            font=("Segoe UI", 12), text_color="#6B7280",
        ).pack(anchor="w")
        self._fetch_whats_new()

        support_card = Card(pad)
        support_card.pack(fill="x", pady=(0, 16))
        support_row = ctk.CTkFrame(support_card, fg_color="transparent")
        support_row.pack(fill="x", padx=18, pady=16)
        support_row.grid_columnconfigure(0, weight=1)
        text_col = ctk.CTkFrame(support_row, fg_color="transparent")
        text_col.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(text_col, text="NEED SUPPORT?", font=("Segoe UI", 11), text_color="#9CA3AF").pack(
            anchor="w"
        )
        ctk.CTkLabel(
            text_col, text="Questions, bugs, or feedback — find me here.",
            font=("Segoe UI", 12), text_color="#D1D5DB",
        ).pack(anchor="w", pady=(2, 0))
        ctk.CTkButton(
            support_row, text="guns.lol/stinkybungus", fg_color=ACCENT,
            command=lambda: __import__("webbrowser").open("https://guns.lol/stinkybungus"),
        ).grid(row=0, column=1, sticky="e")

        recent_card = Card(pad)
        recent_card.pack(fill="x")
        recent_header = ctk.CTkFrame(recent_card, fg_color="transparent")
        recent_header.pack(fill="x", padx=18, pady=(16, 8))
        ctk.CTkLabel(recent_header, text="RECENT CHANGES", font=("Segoe UI", 11), text_color="#9CA3AF").pack(
            side="left"
        )
        ctk.CTkButton(
            recent_header, text="View Full History →", fg_color="transparent", hover_color="#26262b",
            text_color=ACCENT, font=("Segoe UI", 11), height=20, width=140,
            command=lambda: self.app.show_page("History"),
        ).pack(side="right")

        entries = history.load_history()[:5]
        recent_body = ctk.CTkFrame(recent_card, fg_color="transparent")
        recent_body.pack(fill="x", padx=18, pady=(0, 16))
        if not entries:
            ctk.CTkLabel(
                recent_body, text="Nothing changed yet — apply a tweak and it'll show up here.",
                font=("Segoe UI", 12), text_color="#6B7280",
            ).pack(anchor="w")
        else:
            for entry in entries:
                row = ctk.CTkFrame(recent_body, fg_color="transparent")
                row.pack(fill="x", pady=3)
                row.grid_columnconfigure(0, weight=1)
                dot_color = "#22C55E" if entry["action"] == "applied" else "#9CA3AF"
                line = ctk.CTkFrame(row, fg_color="transparent")
                line.grid(row=0, column=0, sticky="w")
                ctk.CTkLabel(line, text="●", text_color=dot_color, font=("Segoe UI", 10)).pack(
                    side="left", padx=(0, 6)
                )
                ctk.CTkLabel(
                    line, text=f"{entry['name']} — {entry['action'].capitalize()}",
                    font=("Segoe UI", 12), text_color="#D1D5DB",
                ).pack(side="left")
                ctk.CTkLabel(
                    row, text=history.format_timestamp(entry["timestamp"]),
                    font=("Segoe UI", 11), text_color="#6B7280",
                ).grid(row=0, column=1, sticky="e")

    def on_show(self):
        if not self._loop_running:
            self._loop_running = True
            self._update_stats()

    def _fetch_whats_new(self):
        def worker():
            result = updates.check_for_update(APP_VERSION)
            self.after(0, lambda: self._render_whats_new(result))

        threading.Thread(target=worker, daemon=True).start()

    def _render_whats_new(self, result):
        for w in self.wn_body.winfo_children():
            w.destroy()

        if result is None:
            self.wn_version_label.configure(text="")
            ctk.CTkLabel(
                self.wn_body, text="Couldn't reach GitHub to check for release notes "
                                    "(no internet, or it's temporarily unreachable).",
                font=("Segoe UI", 12), text_color="#6B7280", wraplength=900, justify="left",
            ).pack(anchor="w")
            return

        self.wn_version_label.configure(text=result["latest_version"])
        lines = updates.parse_release_notes(result["notes"])

        if not lines:
            ctk.CTkLabel(
                self.wn_body, text="No release notes were written for this version.",
                font=("Segoe UI", 12), text_color="#6B7280",
            ).pack(anchor="w")
        else:
            max_lines = 10
            shown, remaining = lines[:max_lines], lines[max_lines:]
            for line in shown:
                self._render_note_line(line)
            if remaining:
                ctk.CTkLabel(
                    self.wn_body, text=f"…and {len(remaining)} more line(s) — see the full notes below.",
                    font=("Segoe UI", 11), text_color="#6B7280",
                ).pack(anchor="w", pady=(4, 0))

        if result["available"]:
            ctk.CTkLabel(
                self.wn_body, text=f"🔔 v{result['latest_version']} is newer than your v{APP_VERSION}",
                font=("Segoe UI", 12, "bold"), text_color=ACCENT,
            ).pack(anchor="w", pady=(8, 4))

        ctk.CTkButton(
            self.wn_body, text="View Full Release Notes →", fg_color="transparent",
            hover_color="#26262b", text_color=ACCENT, font=("Segoe UI", 11), height=22,
            command=lambda: __import__("webbrowser").open(result["url"]),
        ).pack(anchor="w", pady=(6, 0))
        ctk.CTkButton(
            self.wn_body, text="View Full Changelog →", fg_color="transparent",
            hover_color="#26262b", text_color=ACCENT, font=("Segoe UI", 11), height=22,
            command=lambda: self.app.show_page("Changelog"),
        ).pack(anchor="w", pady=(2, 0))

    def _render_note_line(self, line):
        t = line["type"]
        if t == "h2":
            ctk.CTkLabel(
                self.wn_body, text=line["text"], font=("Segoe UI", 14, "bold"), text_color="white",
            ).pack(anchor="w", pady=(6, 2))
        elif t == "h3":
            ctk.CTkLabel(
                self.wn_body, text=line["text"], font=("Segoe UI", 12, "bold"), text_color="#D1D5DB",
            ).pack(anchor="w", pady=(4, 2))
        elif t == "bullet":
            row = ctk.CTkFrame(self.wn_body, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text="•", font=("Segoe UI", 12), text_color=ACCENT, width=16).pack(
                side="left", anchor="n"
            )
            ctk.CTkLabel(
                row, text=line["text"], font=("Segoe UI", 12), text_color="#D1D5DB",
                wraplength=850, justify="left",
            ).pack(side="left", anchor="w")
        elif t == "quote":
            ctk.CTkLabel(
                self.wn_body, text=line["text"], font=("Segoe UI", 11, "italic"), text_color="#9CA3AF",
                wraplength=850, justify="left",
            ).pack(anchor="w", pady=1)
        else:
            ctk.CTkLabel(
                self.wn_body, text=line["text"], font=("Segoe UI", 12), text_color="#D1D5DB",
                wraplength=850, justify="left",
            ).pack(anchor="w", pady=1)

    def _update_stats(self):
        try:
            live = system_info.get_live_stats()
            self.cpu_graph.push(live["cpu_percent"])
            self.mem_graph.push(live["ram_percent"])
            self.disk_graph.push(live["disk_percent"])
        except Exception:
            pass
        self.after(1500, self._update_stats)
