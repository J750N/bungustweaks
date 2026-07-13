import customtkinter as ctk
from pages.widgets import Card, SectionHeader
from core import system_info


class InfoRow(ctk.CTkFrame):
    """A simple label/value row - easy to scan at a glance."""

    def __init__(self, master, label, value):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self, text=label, font=("Segoe UI", 12), text_color="#9CA3AF", width=140,
                     anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self, text=str(value), font=("Segoe UI", 13, "bold"), anchor="w",
                     wraplength=320, justify="left").grid(row=0, column=1, sticky="w")


class InfoCard(Card):
    def __init__(self, master, icon, title):
        super().__init__(master)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(16, 8))
        ctk.CTkLabel(header, text=f"{icon}  {title}", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="x", padx=18, pady=(0, 16))

    def add_row(self, label, value):
        row = InfoRow(self.body, label, value)
        row.pack(fill="x", pady=3)


class SystemInfoPage(ctk.CTkFrame):
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

        SectionHeader(outer, "System Info", "Everything about this PC, at a glance.").pack(
            anchor="w", fill="x", pady=(0, 16)
        )

        specs = system_info.get_static_specs()
        gpu = system_info.get_gpu_info()
        board = system_info.get_motherboard_info()
        disks = system_info.get_disk_partitions()
        adapters = system_info.get_network_adapter_names()

        grid = ctk.CTkFrame(outer, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure((0, 1), weight=1)

        cpu_card = InfoCard(grid, "◆", "Processor")
        cpu_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=8)
        cpu_card.add_row("Name", specs["cpu"])
        cpu_card.add_row("Physical Cores", specs["cores"])
        cpu_card.add_row("Logical Threads", specs["threads"])
        cpu_card.add_row("Architecture", specs["machine"])

        gpu_card = InfoCard(grid, "◈", "Graphics")
        gpu_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=8)
        if gpu:
            gpu_card.add_row("Name", gpu["name"])
            gpu_card.add_row("Driver Version", gpu.get("driver_version", "Unknown"))
            gpu_card.add_row("Temperature", f"{gpu['temp_c']}°C")
            gpu_card.add_row("Utilization", f"{gpu['util_percent']}%")
            gpu_card.add_row("VRAM Used", f"{gpu['mem_used_mb']} / {gpu['mem_total_mb']} MB")
        else:
            gpu_card.add_row("Status", "No NVIDIA GPU detected")
            gpu_card.add_row("Note", "AMD/Intel GPU details need a vendor-specific tool.")

        mem_card = InfoCard(grid, "▥", "Memory")
        mem_card.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=8)
        mem_card.add_row("Total RAM", f"{specs['ram_gb']} GB")
        ram_summary = system_info.get_ram_summary()
        if ram_summary:
            mem_card.add_row("Modules", ram_summary)

        board_card = InfoCard(grid, "⚙", "Motherboard & BIOS")
        board_card.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=8)
        board_card.add_row("Manufacturer", board["manufacturer"])
        board_card.add_row("Model", board["product"])
        board_card.add_row("BIOS Version", board["bios_version"])

        os_card = InfoCard(grid, "▤", "Operating System")
        os_card.grid(row=2, column=0, sticky="nsew", padx=(0, 8), pady=8)
        os_card.add_row("OS", specs["os"])

        net_card = InfoCard(grid, "◎", "Network")
        net_card.grid(row=2, column=1, sticky="nsew", padx=(8, 0), pady=8)
        if adapters:
            for name in adapters[:4]:
                net_card.add_row("Adapter", name)
        else:
            net_card.add_row("Adapters", "None detected")

        storage_card = InfoCard(grid, "▦", "Storage Drives")
        storage_card.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=8)
        if disks:
            for d in disks:
                storage_card.add_row(
                    d["mountpoint"],
                    f"{d['used_gb']} GB used / {d['total_gb']} GB total ({d['percent']}%)  ·  {d['fstype']}",
                )
        else:
            storage_card.add_row("Drives", "None detected")
