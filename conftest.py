"""conftest.py — make system-installed Python packages (gi, at-spi2) visible in venv."""

import sys

_SYSTEM_PACKAGES = "/usr/lib/python3/dist-packages"
if _SYSTEM_PACKAGES not in sys.path:
    sys.path.insert(0, _SYSTEM_PACKAGES)
