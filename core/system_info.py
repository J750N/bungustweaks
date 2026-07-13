"""
Live system stats for the Home page. Uses only psutil + platform so it
works without any extra drivers. GPU name/load is best-effort (via
`nvidia-smi` if present); it degrades gracefully if not.
"""

import platform
import subprocess
import psutil


def _wmic_get(alias, fields):
    """Runs `wmic <alias> get <fields> /format:list` and returns a dict of the first result."""
    if platform.system() != "Windows":
        return {}
    try:
        out = subprocess.run(
            ["wmic", alias, "get", ",".join(fields), "/format:list"],
            capture_output=True, text=True, timeout=5,
        )
        result = {}
        for line in out.stdout.splitlines():
            if "=" in line:
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if key and value and key not in result:
                    result[key] = value
        return result
    except Exception:
        return {}


def get_cpu_name() -> str:
    """Real CPU marketing name (e.g. 'AMD Ryzen 7 7800X3D 8-Core Processor'),
    falling back to the raw platform string if wmic isn't available."""
    info = _wmic_get("cpu", ["Name"])
    name = info.get("Name", "").strip()
    return name or platform.processor() or "Unknown CPU"


def get_os_details() -> str:
    """Full OS edition + build (e.g. 'Windows 11 Pro (Build 22631)'), falling back
    to the generic platform string if wmic isn't available."""
    info = _wmic_get("os", ["Caption", "BuildNumber"])
    caption = info.get("Caption", "").replace("Microsoft ", "").strip()
    build = info.get("BuildNumber", "").strip()
    if caption and build:
        return f"{caption} (Build {build})"
    if caption:
        return caption
    return f"{platform.system()} {platform.release()}"


def get_static_specs() -> dict:
    return {
        "cpu": get_cpu_name(),
        "cores": psutil.cpu_count(logical=False),
        "threads": psutil.cpu_count(logical=True),
        "ram_gb": round(psutil.virtual_memory().total / (1024 ** 3), 1),
        "os": get_os_details(),
        "machine": platform.machine(),
    }


def get_live_stats() -> dict:
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.3),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("C:\\" if platform.system() == "Windows" else "/").percent,
        "net": psutil.net_io_counters(),
    }


def get_gpu_info() -> dict:
    """Best-effort NVIDIA GPU stats via nvidia-smi. Returns None if unavailable."""
    try:
        out = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total,driver_version",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=3,
        )
        if out.returncode == 0 and out.stdout.strip():
            parts = [s.strip() for s in out.stdout.strip().split(",")]
            name, temp, util, mem_used, mem_total = parts[:5]
            driver = parts[5] if len(parts) > 5 else "Unknown"
            return {
                "name": name,
                "temp_c": int(float(temp)),
                "util_percent": int(float(util)),
                "mem_used_mb": int(float(mem_used)),
                "mem_total_mb": int(float(mem_total)),
                "driver_version": driver,
            }
    except Exception:
        pass
    return None


def get_disk_partitions() -> list:
    """Returns per-partition usage info: mount point, fs type, total/used/free GB."""
    partitions = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            partitions.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_gb": round(usage.total / (1024 ** 3), 1),
                "used_gb": round(usage.used / (1024 ** 3), 1),
                "free_gb": round(usage.free / (1024 ** 3), 1),
                "percent": usage.percent,
            })
        except (PermissionError, OSError):
            continue
    return partitions


def get_motherboard_info() -> dict:
    """Best-effort motherboard/BIOS info via wmic (Windows only)."""
    info = {"manufacturer": "Unknown", "product": "Unknown", "bios_version": "Unknown"}
    if platform.system() != "Windows":
        return info
    try:
        out = subprocess.run(
            ["wmic", "baseboard", "get", "Manufacturer,Product", "/format:list"],
            capture_output=True, text=True, timeout=5,
        )
        for line in out.stdout.splitlines():
            if line.startswith("Manufacturer="):
                info["manufacturer"] = line.split("=", 1)[1].strip() or "Unknown"
            elif line.startswith("Product="):
                info["product"] = line.split("=", 1)[1].strip() or "Unknown"
        out2 = subprocess.run(
            ["wmic", "bios", "get", "SMBIOSBIOSVersion", "/format:list"],
            capture_output=True, text=True, timeout=5,
        )
        for line in out2.stdout.splitlines():
            if line.startswith("SMBIOSBIOSVersion="):
                info["bios_version"] = line.split("=", 1)[1].strip() or "Unknown"
    except Exception:
        pass
    return info


def get_network_adapter_names() -> list:
    """Returns names of active (non-loopback) network interfaces."""
    names = []
    try:
        stats = psutil.net_if_stats()
        for name, s in stats.items():
            if s.isup and "loopback" not in name.lower():
                names.append(name)
    except Exception:
        pass
    return names


def get_gpu_vendor() -> str:
    """Returns 'nvidia', 'amd', 'intel', or 'unknown' based on the primary GPU name."""
    if platform.system() != "Windows":
        return "unknown"
    try:
        out = subprocess.run(
            ["wmic", "path", "win32_VideoController", "get", "Name", "/format:list"],
            capture_output=True, text=True, timeout=5,
        )
        text = out.stdout.lower()
        if "nvidia" in text:
            return "nvidia"
        if "amd" in text or "radeon" in text:
            return "amd"
        if "intel" in text:
            return "intel"
    except Exception:
        pass
    return "unknown"


def get_gpu_name() -> str:
    if platform.system() != "Windows":
        return "Unknown"
    try:
        out = subprocess.run(
            ["wmic", "path", "win32_VideoController", "get", "Name", "/format:list"],
            capture_output=True, text=True, timeout=5,
        )
        for line in out.stdout.splitlines():
            if line.startswith("Name=") and line.split("=", 1)[1].strip():
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return "Unknown"


def get_cpu_vendor() -> str:
    """Returns 'amd', 'intel', or 'unknown' parsed from platform.processor()."""
    proc = platform.processor().lower()
    if "amd" in proc:
        return "amd"
    if "intel" in proc or "genuineintel" in proc:
        return "intel"
    return "unknown"


def get_ram_sticks() -> list:
    """Returns per-stick RAM info: capacity (GB) and speed (MHz). Windows only."""
    if platform.system() != "Windows":
        return []
    try:
        out = subprocess.run(
            ["wmic", "memorychip", "get", "Capacity,Speed", "/format:list"],
            capture_output=True, text=True, timeout=5,
        )
        sticks = []
        current = {}
        for line in out.stdout.splitlines():
            line = line.strip()
            if not line:
                if current:
                    sticks.append(current)
                    current = {}
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                current[key.strip()] = value.strip()
        if current:
            sticks.append(current)

        result = []
        for s in sticks:
            try:
                capacity_gb = round(int(s.get("Capacity", 0)) / (1024 ** 3), 1)
                speed = int(s.get("Speed", 0))
                result.append({"capacity_gb": capacity_gb, "speed_mhz": speed})
            except (ValueError, TypeError):
                continue
        return result
    except Exception:
        return []


def get_ram_summary() -> str:
    """A short summary like '2x16GB @ 5200MHz', falling back to just total GB."""
    sticks = get_ram_sticks()
    if not sticks:
        return ""
    speeds = {s["speed_mhz"] for s in sticks if s["speed_mhz"]}
    capacities = {s["capacity_gb"] for s in sticks}
    if len(capacities) == 1 and len(speeds) <= 1:
        cap = capacities.pop()
        speed_str = f" @ {speeds.pop()}MHz" if speeds else ""
        return f"{len(sticks)}x{cap:g}GB{speed_str}"
    return f"{len(sticks)} modules installed"
