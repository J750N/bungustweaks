"""
Flattens every tweak definition (tweak categories, services, vendor-specific
GPU/CPU tweaks) into one key -> tweak dict, so History can look up and
revert ANY past change regardless of which page it lives on.
"""

from data.tweaks_data import TWEAKS
from data.services_data import SERVICES
from data.vendor_tweaks import NVIDIA_TWEAKS, AMD_TWEAKS, CPU_TWEAKS

_ALL = {}

for _category in TWEAKS.values():
    for _t in _category:
        _ALL[_t["key"]] = _t

for _category in SERVICES.values():
    for _t in _category:
        _ALL[_t["key"]] = _t

for _t in NVIDIA_TWEAKS + AMD_TWEAKS + CPU_TWEAKS:
    _ALL[_t["key"]] = _t


def get(key: str):
    return _ALL.get(key)
