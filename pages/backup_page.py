import customtkinter as ctk
import os
from pages.widgets import SectionHeader, Card, LogConsole, confirm_dialog
from core import backup, runner


class BackupPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=30, pady=24)

        SectionHeader(
            outer, "Backup & Restore",
            "Always back up before applying tweaks. You can undo anything from here.",
        ).pack(anchor="w", fill="x", pady=(0, 16))

        row = ctk.CTkFrame(outer, fg_color="transparent")
        row.pack(fill="x", pady=(0, 16))
        row.grid_columnconfigure((0, 1), weight=1)

        restore_card = Card(row)
        restore_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(restore_card, text="System Restore Point", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", padx=18, pady=(16, 4)
        )
        ctk.CTkLabel(
            restore_card, text="A full snapshot Windows can roll back to if anything goes wrong.",
            font=("Segoe UI", 12), text_color="#9CA3AF", wraplength=280, justify="left",
        ).pack(anchor="w", padx=18)
        self.restore_btn = ctk.CTkButton(
            restore_card, text="Create Restore Point", fg_color="#8B5CF6",
            command=self._create_restore_point,
        )
        self.restore_btn.pack(anchor="w", padx=18, pady=16)

        reg_card = Card(row)
        reg_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(reg_card, text="Registry Backup", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", padx=18, pady=(16, 4)
        )
        ctk.CTkLabel(
            reg_card, text="Exports the registry keys tweaks modify, so you can re-import them anytime.",
            font=("Segoe UI", 12), text_color="#9CA3AF", wraplength=280, justify="left",
        ).pack(anchor="w", padx=18)
        ctk.CTkButton(
            reg_card, text="Export Registry Keys", fg_color="#8B5CF6",
            command=self._export_registry,
        ).pack(anchor="w", padx=18, pady=16)

        list_card = Card(outer)
        list_card.pack(fill="both", expand=True)
        ctk.CTkLabel(list_card, text="SAVED BACKUPS", font=("Segoe UI", 11), text_color="#9CA3AF").pack(
            anchor="w", padx=18, pady=(16, 8)
        )
        self.backup_list_frame = ctk.CTkScrollableFrame(list_card, fg_color="transparent")
        self.backup_list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.console = LogConsole(outer, height=100)
        self.console.pack(fill="x", pady=(12, 0))

        self._refresh_backup_list()

    def on_show(self):
        self._refresh_backup_list()

    def _refresh_backup_list(self):
        for w in self.backup_list_frame.winfo_children():
            w.destroy()
        backups = backup.list_backups()
        if not backups:
            ctk.CTkLabel(self.backup_list_frame, text="No backups yet.", text_color="#6B7280").pack(
                anchor="w", padx=10, pady=6
            )
            return
        for path in backups:
            row = ctk.CTkFrame(self.backup_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(row, text=os.path.basename(path), anchor="w").grid(row=0, column=0, sticky="w")
            ctk.CTkButton(
                row, text="Restore", width=90, fg_color="#374151",
                command=lambda p=path: self._confirm_restore(p),
            ).grid(row=0, column=1, padx=6)

    def _create_restore_point(self):
        if not runner.is_admin():
            self.console.log("⚠ Requires Administrator — click the admin button in the sidebar first.")
            return
        self.restore_btn.configure(text="Creating…", state="disabled")
        self.console.log("Creating system restore point (this can take a minute)…")

        def worker():
            result = backup.create_restore_point()
            self.after(0, lambda: self._restore_point_done(result.returncode == 0))

        import threading
        threading.Thread(target=worker, daemon=True).start()

    def _restore_point_done(self, success):
        self.restore_btn.configure(text="Create Restore Point", state="normal")
        self.console.log("✔ Restore point created." if success else
                          "✘ Failed to create restore point (System Restore may be disabled).")

    def _export_registry(self):
        self.console.log("Exporting registry keys…")

        def worker():
            files = backup.export_registry()
            self.after(0, lambda: self._export_done(files))

        import threading
        threading.Thread(target=worker, daemon=True).start()

    def _export_done(self, files):
        if files:
            self.console.log(f"✔ Exported {len(files)} registry file(s) to %LOCALAPPDATA%\\PCTweaker\\backups")
        else:
            self.console.log("✘ Export failed — try running as Administrator.")
        self._refresh_backup_list()

    def _confirm_restore(self, path):
        confirm_dialog(
            self, "Restore backup?",
            f"Import {os.path.basename(path)} back into the registry? A sign-out or restart may be needed.",
            on_yes=lambda: self._do_restore(path),
        )

    def _do_restore(self, path):
        self.console.log(f"Restoring {os.path.basename(path)}…")
        result = backup.restore_from_file(path)
        self.console.log("✔ Restore complete." if result.returncode == 0 else "✘ Restore failed.")
