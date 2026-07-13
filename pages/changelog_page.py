import customtkinter as ctk
from pages.widgets import Card, SectionHeader, ACCENT, bind_responsive_wrap
from core import updates
from pages.settings import APP_VERSION


class ChangelogPage(ctk.CTkFrame):
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

        header_row = ctk.CTkFrame(outer, fg_color="transparent")
        header_row.pack(fill="x")
        SectionHeader(
            header_row, "Changelog", f"Every release, straight from GitHub. You're on v{APP_VERSION}.",
        ).pack(side="left", anchor="w")
        self.refresh_button = ctk.CTkButton(
            header_row, text="Refresh", fg_color="#374151", width=90,
            command=self._fetch,
        )
        self.refresh_button.pack(side="right", pady=(8, 0))

        self.body = ctk.CTkFrame(outer, fg_color="transparent")
        self.body.pack(fill="both", expand=True, pady=(16, 0))
        ctk.CTkLabel(
            self.body, text="Loading release history…", font=("Segoe UI", 12), text_color="#6B7280",
        ).pack(anchor="w", pady=20)

        self._fetch()

    def _fetch(self):
        self.refresh_button.configure(text="Loading…", state="disabled")
        for w in self.body.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.body, text="Loading release history…", font=("Segoe UI", 12), text_color="#6B7280",
        ).pack(anchor="w", pady=20)

        def worker():
            releases = updates.get_all_releases()
            self.after(0, lambda: self._render(releases))

        import threading
        threading.Thread(target=worker, daemon=True).start()

    def _render(self, releases):
        self.refresh_button.configure(text="Refresh", state="normal")
        for w in self.body.winfo_children():
            w.destroy()

        if releases is None:
            ctk.CTkLabel(
                self.body, text="Couldn't reach GitHub — no internet, or it's temporarily unreachable.",
                font=("Segoe UI", 12), text_color="#6B7280",
            ).pack(anchor="w", pady=20)
            return

        if not releases:
            ctk.CTkLabel(
                self.body, text="No releases published yet.",
                font=("Segoe UI", 12), text_color="#6B7280",
            ).pack(anchor="w", pady=20)
            return

        for release in releases:
            self._build_release_card(release)

    def _build_release_card(self, release):
        card = Card(self.body)
        card.pack(fill="x", pady=6)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=16)

        header = ctk.CTkFrame(inner, fg_color="transparent")
        header.pack(fill="x", pady=(0, 4))
        is_current = release["version"].lstrip("vV") == APP_VERSION.lstrip("vV")
        title_text = release["name"] or release["version"]
        ctk.CTkLabel(header, text=title_text, font=("Segoe UI", 15, "bold")).pack(side="left")
        if is_current:
            ctk.CTkLabel(
                header, text="  YOU ARE HERE", font=("Segoe UI", 10, "bold"), text_color="#22C55E",
            ).pack(side="left")
        if release.get("prerelease"):
            ctk.CTkLabel(
                header, text="  PRE-RELEASE", font=("Segoe UI", 10, "bold"), text_color="#F59E0B",
            ).pack(side="left")
        ctk.CTkLabel(
            header, text=updates.format_release_date(release["published_at"]),
            font=("Segoe UI", 11), text_color="#6B7280",
        ).pack(side="right")

        notes_frame = ctk.CTkFrame(inner, fg_color="transparent")
        notes_frame.pack(fill="x", pady=(6, 8))
        lines = updates.parse_release_notes(release["notes"])
        if not lines:
            ctk.CTkLabel(
                notes_frame, text="No notes written for this release.",
                font=("Segoe UI", 12), text_color="#6B7280",
            ).pack(anchor="w")
        else:
            for line in lines:
                self._render_note_line(notes_frame, line)

        ctk.CTkButton(
            inner, text="View on GitHub →", fg_color="transparent", hover_color="#26262b",
            text_color=ACCENT, font=("Segoe UI", 11), height=22,
            command=lambda: __import__("webbrowser").open(release["url"]),
        ).pack(anchor="w")

    def _render_note_line(self, parent, line):
        t = line["type"]
        if t == "h2":
            ctk.CTkLabel(
                parent, text=line["text"], font=("Segoe UI", 13, "bold"), text_color="white",
            ).pack(anchor="w", pady=(6, 2))
        elif t == "h3":
            ctk.CTkLabel(
                parent, text=line["text"], font=("Segoe UI", 12, "bold"), text_color="#D1D5DB",
            ).pack(anchor="w", pady=(4, 2))
        elif t == "bullet":
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text="•", font=("Segoe UI", 12), text_color=ACCENT, width=16).pack(
                side="left", anchor="n"
            )
            label = ctk.CTkLabel(
                row, text=line["text"], font=("Segoe UI", 12), text_color="#D1D5DB", justify="left",
            )
            label.pack(side="left", anchor="w")
            bind_responsive_wrap(label, container=row, padding=40)
        elif t == "quote":
            label = ctk.CTkLabel(
                parent, text=line["text"], font=("Segoe UI", 11, "italic"), text_color="#9CA3AF",
                justify="left",
            )
            label.pack(anchor="w", pady=1)
            bind_responsive_wrap(label, container=parent)
        else:
            label = ctk.CTkLabel(
                parent, text=line["text"], font=("Segoe UI", 12), text_color="#D1D5DB", justify="left",
            )
            label.pack(anchor="w", pady=1)
            bind_responsive_wrap(label, container=parent)
