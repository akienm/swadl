# File: SWADLconstants.py
# Purpose: Constants

# standard libraries
import os
import sys

# selenium imports
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium import webdriver


# SWADL libs
from engine.swadl_config_dict import ConfigDict

# Section: Don't clutter up the workspace. Adding this here makes PYTHONDONTWRITEBYTECODE
# less important.
sys.dont_write_bytecode = True

# Section: Uncategorized importable string constants
# Purospe: Everything else not covered in the sections below
ANY = "Any"
CACHE = "cache"
CLICK = "click"
DRIVER = "driver"
ENABLED = "enabled"
EXIST = "exist"
EXPECTED = "expected"
FAILURE_LOG = "failure_log"
NAME = "name"
RESULT_LOG = "result_log"
SELECTED_CAPS = "SELECTED_CAPS"
SUBSTITUTION_SOURCES = "substitution_sources"
TEST_NAME = 'test_name'
TEST_SET_FILE = "test_set_file"
TIMEOUT = "timeout"
UNIQUE = "unique"
VALIDATE_CLICKABLE = "validate_clickable"
VALIDATE_CLICK = "validate_click"
VALIDATE_ENABLED = "validate_enabled"
VALIDATE_EXIST = "validate_exist"
VALIDATE_INPUT = "validate_input"
VALIDATE_TEXT = "validate_text"
VALIDATE_VISIBLE = "validate_visible"
VALIDATE_UNIQUE = "validate_unique"
VALIDATION_NOT_EXIST = {VALIDATE_EXIST: False}
VALIDATION_VISIBLE = {VALIDATE_VISIBLE: True}
VALUE = "value"
VISIBLE = "visible"

# Section: Environment Variables
# Purpose: These are all importable names which coud have values passed in from the environment
#          and which are present in the importable cgfdict (explained below)
SELENIUM_BROWSER = "SELENIUM_BROWSER"
SELENIUM_BROWSER_OPTIONS = "SELENIUM_BROWSER_OPTIONS"
SELENIUM_BROWSER_PLATFORM = "SELENIUM_BROWSER_PLATFORM"
SELENIUM_BROWSER_VERSION = "SELENIUM_BROWSER_VERSION"
SELENIUM_CONTROL_DEFAULT_TIMEOUT = "SELENIUM_CONTROL_DEFAULT_TIMEOUT"
SELENIUM_PAGE_DEFAULT_TIMEOUT = "SELENIUM_PAGE_DEFAULT_TIMEOUT"
SELENIUM_PORT = "SELENIUM_PORT"
SELENIUM_SERVER = "SELENIUM_SERVER"
SELENIUM_TEST_SET_FILE = "SELENIUM_TEST_SET_FILE"
SWADLTEST_URL = "SELENIUM_URL"
SWADLTEST_VERBOSE = "SWADLTEST_VERBOSE"

