"""Regression test for SELENIUM_USER_DATA_DIR (custom browser profile).

Required by TheIgors gmail flows: Igor must drive Gmail in Akien's browser
profile (cookies, session, saved login already present), not the default
empty profile. Without this, every Gmail flow run would need to log in
again, including 2FA — unworkable for routine automation.

Tests cover the option-construction logic without launching Chrome (which
would require a display + chromedriver matching binary). Build the
ChromeOptions and assert the user-data-dir argument is present.
"""

from __future__ import annotations

import unittest

from SWADL.engine.swadl_constants import SELENIUM_USER_DATA_DIR


class TestChromeUserDataDirOption(unittest.TestCase):
    def test_no_user_data_dir_returns_none(self):
        """When SELENIUM_USER_DATA_DIR is unset/None, _build_chrome_options
        returns None so the caller passes nothing to webdriver.Chrome."""
        from SWADL.engine import swadl_cfg

        # Snapshot + clear
        saved = swadl_cfg.cfgdict.get(SELENIUM_USER_DATA_DIR)
        try:
            swadl_cfg.cfgdict[SELENIUM_USER_DATA_DIR] = None
            self.assertIsNone(swadl_cfg._build_chrome_options())
        finally:
            swadl_cfg.cfgdict[SELENIUM_USER_DATA_DIR] = saved

    def test_user_data_dir_set_returns_options_with_argument(self):
        """When set, _build_chrome_options returns a ChromeOptions instance
        carrying --user-data-dir=<path>."""
        from SWADL.engine import swadl_cfg

        saved = swadl_cfg.cfgdict.get(SELENIUM_USER_DATA_DIR)
        try:
            swadl_cfg.cfgdict[SELENIUM_USER_DATA_DIR] = "/tmp/test-profile"
            options = swadl_cfg._build_chrome_options()
            self.assertIsNotNone(options)
            args = options.arguments
            assert any(
                "--user-data-dir=/tmp/test-profile" in a for a in args
            ), f"got args={args}"
        finally:
            swadl_cfg.cfgdict[SELENIUM_USER_DATA_DIR] = saved


if __name__ == "__main__":
    unittest.main()
