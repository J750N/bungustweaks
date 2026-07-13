# Bundled Tools Folder

BungusTweaks can launch vendor tools with **zero settings needed** if you
drop the real files into the matching subfolder below. This is entirely
optional — without them, BungusTweaks falls back to checking your normal
Windows install, and if that's not found either, it opens the official
download page instead.

We don't ship these ourselves: we have no way to fetch and embed someone
else's compiled binaries as part of building this project, and quietly
redistributing NVIDIA's/AMD's/MSI's own software isn't a decision we get to
make for you. Grabbing the official copy yourself takes a minute and keeps
you on a version you know is legitimate and up to date.

## Where each one goes

| Folder | What to put in it | Get it from |
|---|---|---|
| `tools/nvidiaProfileInspector/` | `nvidiaProfileInspector.exe` (+ its DLLs) | https://github.com/Orbmu2k/nvidiaProfileInspector/releases |
| `tools/MSIAfterburner/` | The full MSI Afterburner install folder (`MSIAfterburner.exe` + its files) | https://www.msi.com/Landing/afterburner |
| `tools/NVIDIAApp/` | `NVIDIA app.exe` (from a normal NVIDIA App install, copy the folder) | https://www.nvidia.com/en-us/software/nvidia-app/ |
| `tools/AMDAdrenalin/` | `RadeonSoftware.exe` (from a normal AMD Adrenalin install) | https://www.amd.com/en/support |
| `tools/IntelGraphics/` | `IGCC.exe` (from a normal Intel Graphics Command Center install) | https://www.intel.com/content/www/us/en/support/detect.html |

**nvidiaProfileInspector is the easiest one** — it's a small, portable,
open-source tool (no installer, just an exe + a couple DLLs), so dropping it
into its folder takes 10 seconds and immediately unlocks the "Apply Desktop
Profile" / "Apply Laptop Profile" buttons on the Gaming page with no Settings
step at all.

The bigger ones (NVIDIA App, AMD Adrenalin, MSI Afterburner) are full
installed applications — realistically, most people already have these
installed from setting up their PC, so BungusTweaks will usually find them
automatically without you needing to touch this folder at all. Bundling them
here is only useful if you want a fully self-contained BungusTweaks folder
that works on a brand new PC with nothing else installed.

## Note for packaging into an installer

If you bundle real files here, `build_exe.bat` needs to include this folder
too — see the `--add-data` note in that script.
