# File: SWADLconstants.py
# Purpose: Constants

# standard libraries
import sys

# Section: Don't clutter up the workspace. Adding this here makes PYTHONDONTWRITEBYTECODE
# less important.
sys.dont_write_bytecode = True

# Section: Uncategorized importable string constants
# Purospe: Everything else not covered in the sections below
ANY = 'Any'
ARGS = 'ARGS'
ARGSCOUNT = 'ARGSCOUNT'
ARGSCOUNT_OK = 'ARGSCOUNT_OK'
ARGSFIELDS = 'ARGSFIELDS'
ASSERT = 'ASSERT'
CACHE = 'cache'
CLICK = 'click'
CONFIG_DICT = 'CONFIG_DICT'
DRIVER = 'driver'
ENABLED = 'enabled'
ERROR = 'ERROR'
EXIST = 'exist'
EXPECTED = 'expected'
FAILED = '🔎 FAILED'
FAILURE_LOG = 'failure_log'
FATAL = 'FATAL'
FINAL_RESULT_MESSAGE = 'FINAL_RESULT_MESSAGE'
HELPER = 'HELPER'
ID = 'ID'
KWARGS = 'KWARGS'
LOGICAL_RESULT = 'LOGICAL_RESULT'
MESSAGE = 'MESSAGE'
NAME = 'name'
PASSED = '😇 Passed'
REPORTING_DICT = 'REPORTING_DICT'
RESULT = 'RESULT'
RESULT_LOG = 'result_log'
SELECTED_CAPS = 'SELECTED_CAPS'
SELF__DICT__ = 'self.__dict__'
STACKTRACE = 'STACKTRACE'
SUBSTITUTION_SOURCES = 'substitution_sources'
TEST_DATA = 'TEST_DATA'
TEST_NAME = 'test_name'
TEST_SET_FILE = 'test_set_file'
TEST_OBJECT = 'TEST_OBJECT'
TIME_FINISHED = 'TIME_FINISHED'
TIME_STARTED = 'TIME_STARTED'
TITLE = 'TITLE'
TIMEOUT = 'timeout'
UNIQUE = 'unique'
VALIDATE_CLICKABLE = 'validate_clickable'
VALIDATE_CLICK = 'validate_click'
VALIDATE_ENABLED = 'validate_enabled'
VALIDATE_EXIST = 'validate_exist'
VALIDATE_INPUT = 'validate_input'
VALIDATE_TEXT = 'validate_text'
VALIDATE_VISIBLE = 'validate_visible'
VALIDATE_UNIQUE = 'validate_unique'
VALIDATION_NOT_EXIST = {VALIDATE_EXIST: False}
VALIDATION_VISIBLE = {VALIDATE_VISIBLE: True}
VALUE = 'value'
VISIBLE = 'visible'
WARN = 'WARN'

# Section: Environment Variables
# Purpose: These are all importable names which coud have values passed in from the environment
#          and which are present in the importable cgfdict (explained below)
SELENIUM_BROWSER = 'SELENIUM_BROWSER'
SELENIUM_BROWSER_OPTIONS = 'SELENIUM_BROWSER_OPTIONS'
SELENIUM_BROWSER_PLATFORM = 'SELENIUM_BROWSER_PLATFORM'
SELENIUM_BROWSER_VERSION = 'SELENIUM_BROWSER_VERSION'
SELENIUM_CONTROL_DEFAULT_TIMEOUT = 'SELENIUM_CONTROL_DEFAULT_TIMEOUT'
SELENIUM_PAGE_DEFAULT_TIMEOUT = 'SELENIUM_PAGE_DEFAULT_TIMEOUT'
SELENIUM_PORT = 'SELENIUM_PORT'
SELENIUM_SERVER = 'SELENIUM_SERVER'
SELENIUM_TEST_SET_FILE = 'SELENIUM_TEST_SET_FILE'
SWADLTEST_URL = 'SELENIUM_URL'
SWADLTEST_VERBOSE = 'SWADLTEST_VERBOSE'

