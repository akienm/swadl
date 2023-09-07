# File: SWADLconstants.py
# Purpose: Constants

# standard libraries
import os
import sys

# selenium imports
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver

# SWADL libs
from seleniumpoc.SWADL.SWADLconfig_dict import ConfigDict

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

# Section: cfgdict
# Purpose: Global configuration storge importable instance. All test values to be read from the
#          environment will be in here (eg, SELENIUM_BROWSER)
cfgdict = ConfigDict()

# Section: SWADL Defaults
# Purpose: Specify the basemost defaults, but allow environment variables to override
# Notes: The use of the environment means we just need to set env vars to pass in what
#        we want to do. Makes everything very repeatable.
TEST_PARAMETERS = {
    SELENIUM_BROWSER_OPTIONS: None,
    SELENIUM_BROWSER_PLATFORM: "WINDOWS",
    SELENIUM_BROWSER_VERSION: "",
    SELENIUM_BROWSER: "edge",
    SELENIUM_CONTROL_DEFAULT_TIMEOUT: 10,
    SELENIUM_PAGE_DEFAULT_TIMEOUT: 40,
    SELENIUM_PORT: 0,
    SELENIUM_SERVER: "127.0.0.1",
    SELENIUM_TEST_SET_FILE: None,
    SWADLTEST_URL: None,
    SWADLTEST_VERBOSE: False,
}

for key in TEST_PARAMETERS:
    cfgdict[key] = os.environ.get(key, TEST_PARAMETERS[key])

# Section: test_set
# Purpose: Read from a .test_set file if one is specified. Overrides values in cfgdict
# TODO: If a SELENIUM_TEST_SET_FILE is specified, overwrite the values above with it's
#       contents.
if cfgdict[SELENIUM_TEST_SET_FILE]:
    raise Exception(".test_set files are not yet implemented")


# Section: Driver
# Purpose: To create the importable instance "driver" of Webdriver Remote, that will be available
#          everywhere
# Inputs: (dict)cfgdict: All configuration environment values read from various sources
# Output: importable instance of "driver"


def build_class_with_cleanup(driver_class):
    # Method: build_class_with_cleanup
    # Purpose: Builds a webdriver that cleans itself up for whatever class of remote
    #          we've been passed.

    class RemoteWithCleanup(driver_class):
        # Class: RemoteWithCleanup
        # Purpose: Adds a "clean close on exit"
        # Notes: This

        # Datum: clean_close_on_exit
        # Purpose: Flag that allows clean close on exit. Set to False and the behavior is inhibited.
        clean_close_on_exit = True

        def __del__(self):
            # Method: __del__()
            # Purpose: Adds a "clean close on exit"
            if self.clean_close_on_exit:
                try:
                    self.quit()
                except Exception:
                    # this handles:
                    # File ...site-packages\selenium\webdriver\common\service.py",
                    # line 122, in send_remote_shutdown_command
                    # ImportError: sys.meta_path is None, Python is likely shutting down
                    pass
    return RemoteWithCleanup

# TODO: Use this to put together really generic capabilities
# Requires more reseach on Chromium Edge and being able to launch as if on grid.
# For some reason, this doesn't work with EDGE and I still haven't sorted why
# cfgdict[SELECTED_CAPS] = {
#     'browserName': cfgdict[SELENIUM_BROWSER],
#     'version': cfgdict[SELENIUM_BROWSER_VERSION],
#     'platform': cfgdict[SELENIUM_BROWSER_PLATFORM],
# }
# command_exec = f"http://{cfgdict[SELENIUM_SERVER]}:{cfgdict[SELENIUM_PORT]}/wd/hub"
# driver = RemoteWithCleanup(
#     command_executor=command_exec,
#     desired_capabilities=cfgdict[SELECTED_CAPS],
#     options=cfgdict[SELENIUM_BROWSER_OPTIONS],
#     platform=cfgdict[SELENIUM_BROWSER_PLATFORM]
# )


# Section: webdriver creation
# Purpose: Sorts out the invocation parameters by browser
def create_chrome_webdriver():
    # driver_class = webdriver.Chrome
    # driver_args = ['chromedriver.exe']
    # driver_options = ChromeOptions
    # driver_capabilities = DesiredCapabilities.CHROME.copy()
    raise Exception("Not implemented for chromedriver yet")


def create_edge_webdriver():
    # Method:
    # Purpose: To create the edge specific webdriver.

    # options: Note that this seems to fail on edge! TODO: Investigate
    options = EdgeOptions()
    options.use_chromium = True
    # Add any other options here

    # Datum: capabilities
    # Purpose: Template for capabilities that will be passed on
    # {'browserName': 'MicrosoftEdge', 'version': '', 'platform': 'WINDOWS'}
    capabilities = DesiredCapabilities.EDGE.copy()
    # Add anything else we wind up needing to add to Edge here

    # This call returns a class, bascically the driver class we want, but with an auto-close
    # magic method added.
    edge_driver_class = build_class_with_cleanup(EdgeDriver)

    # And now we make our driver
    driver = edge_driver_class(
        executable_path='msedgedriver.exe',
        port=cfgdict[SELENIUM_PORT],
        # options=options,  # TODO: This failed but shouldn't have, research it!
        capabilities=capabilities,
    )

    return driver


driver_creators = {
    "chrome": create_chrome_webdriver,
    "edge": create_edge_webdriver,
}
try:
    method_key = cfgdict[SELENIUM_BROWSER]
    method_to_call = driver_creators[method_key]
    driver = method_to_call()
except Exception as e:
    raise Exception(
        f"{e}\nPerhaps {cfgdict[SELENIUM_BROWSER]} is not yet supported by the framework?"
    )

cfgdict[DRIVER] = driver
