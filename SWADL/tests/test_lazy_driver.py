"""
File: test_lazy_driver.py
Purpose: Regression test for lazy driver instantiation.

Importing SWADL must NOT spawn a browser. The browser leak this prevents
cost a session (Akien noticed 6 orphan Chrome processes after a single
test that should have skipped). The driver only spins up when something
actually accesses self.driver, then must be quit explicitly via
SWADLBaseAutomation.quit() / SWADLTest.tearDown.

Detection: count chrome/chromedriver processes in the test process tree
(not system-wide — Akien's daily Chrome is open and would false-positive
a `pgrep chrome` check).
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest


def _count_browser_children() -> int:
    """Count chrome/chromedriver processes spawned by this test process."""
    try:
        out = subprocess.check_output(
            ["pgrep", "-P", str(os.getpid()), "-f", "chrome|chromedriver"],
            stderr=subprocess.DEVNULL,
        )
        return len([line for line in out.decode().splitlines() if line.strip()])
    except subprocess.CalledProcessError:
        return 0


class TestLazyDriver(unittest.TestCase):
    def test_importing_swadltest_does_not_spawn_browser(self):
        """Subprocess: fresh interpreter, import only — no browser allowed."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from SWADL.engine.swadl_base_test import SWADLTest; "
                "import os, subprocess; "
                "out = subprocess.run(['pgrep', '-P', str(os.getpid()), '-f', 'chrome|chromedriver'], "
                "  capture_output=True, text=True); "
                "n = len([l for l in out.stdout.splitlines() if l.strip()]); "
                "print(n)",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        spawned = int(result.stdout.strip())
        self.assertEqual(
            spawned,
            0,
            f"Importing SWADLTest spawned {spawned} chrome process(es) — "
            f"driver creation must be lazy",
        )

    def test_importing_swadl_cfg_does_not_spawn_browser(self):
        """Subprocess: importing the cfg module alone must not spawn."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from SWADL.engine import swadl_cfg; "
                "import os, subprocess; "
                "out = subprocess.run(['pgrep', '-P', str(os.getpid()), '-f', 'chrome|chromedriver'], "
                "  capture_output=True, text=True); "
                "n = len([l for l in out.stdout.splitlines() if l.strip()]); "
                "print(n)",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
        spawned = int(result.stdout.strip())
        self.assertEqual(
            spawned,
            0,
            f"Importing swadl_cfg spawned {spawned} chrome process(es)",
        )

    def test_get_driver_creates_on_first_call_and_quit_clears(self):
        """get_driver() spawns; _quit_driver_if_running() cleans up."""
        from SWADL.engine.swadl_cfg import (
            cfgdict,
            get_driver,
            _quit_driver_if_running,
        )
        from SWADL.engine.swadl_constants import DRIVER

        # Pre-state: nothing spawned by import alone
        self.assertIsNone(cfgdict.get(DRIVER))

        try:
            driver = get_driver()
            self.assertIsNotNone(driver)
            self.assertIsNotNone(cfgdict.get(DRIVER))
        finally:
            _quit_driver_if_running()

        self.assertIsNone(cfgdict.get(DRIVER))


if __name__ == "__main__":
    unittest.main()
