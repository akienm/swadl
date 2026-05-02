# standard libraries
import os
from selenium import webdriver

# SWADL libs
from SWADL.engine.swadl_config_dict import ConfigDict
from SWADL.engine.swadl_driver import SeleniumDriver
from SWADL.engine.swadl_constants import SELENIUM_BROWSER_OPTIONS
from SWADL.engine.swadl_constants import SELENIUM_BROWSER_PLATFORM
from SWADL.engine.swadl_constants import SELENIUM_BROWSER_VERSION
from SWADL.engine.swadl_constants import SELENIUM_BROWSER
from SWADL.engine.swadl_constants import SELENIUM_CONTROL_DEFAULT_TIMEOUT
from SWADL.engine.swadl_constants import SELENIUM_PAGE_DEFAULT_TIMEOUT
from SWADL.engine.swadl_constants import SELENIUM_TEST_SET_FILE
from SWADL.engine.swadl_constants import SWADLTEST_URL
from SWADL.engine.swadl_constants import SWADLTEST_VERBOSE
from SWADL.engine.swadl_constants import DRIVER
from SWADL.engine.swadl_constants import ID
from SWADL.engine.swadl_constants import CONFIG_DICT
from SWADL.engine.swadl_constants import TEST_DATA
from SWADL.engine.swadl_dict import SWADLDict

# Section: cfgdict
# Purpose: Global configuration storge importable instance. All test values to be read from the
#          environment will be in here (eg, SELENIUM_BROWSER)
cfgdict = ConfigDict()
cfgdict[ID] = CONFIG_DICT


# Section: SWADL Defaults
# Purpose: Specify the base-most defaults, but allow environment variables to override
# Notes: The use of the environment means we just need to set env vars to pass in what
#        we want to do. Makes everything very repeatable.
TEST_PARAMETERS = {
    SELENIUM_BROWSER_OPTIONS: None,
    SELENIUM_BROWSER_PLATFORM: "WINDOWS",
    SELENIUM_BROWSER_VERSION: "",
    SELENIUM_BROWSER: "chrome",
    SELENIUM_CONTROL_DEFAULT_TIMEOUT: 20,
    SELENIUM_PAGE_DEFAULT_TIMEOUT: 40,
    SELENIUM_TEST_SET_FILE: None,
    SWADLTEST_URL: None,
    SWADLTEST_VERBOSE: False,
}

# Now this reads them in, or their defaults if they're unspecified
for key in TEST_PARAMETERS:
    cfgdict[key] = os.environ.get(key, TEST_PARAMETERS[key])

# Section: test_data
# Purpose: creates the vehicle by which all other parts communicate
cfgdict[TEST_DATA] = SWADLDict()
cfgdict[TEST_DATA][ID] = TEST_DATA

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


# Section: webdriver creation
# Purpose: Sorts out the invocation parameters by browser
def _create_chrome_webdriver():
    cfgdict[DRIVER] = SeleniumDriver(webdriver.Chrome())
    return cfgdict[DRIVER]


def _create_edge_webdriver():
    cfgdict[DRIVER] = SeleniumDriver(webdriver.Edge())
    return cfgdict[DRIVER]


driver_creators = {
    "chrome": _create_chrome_webdriver,
    "edge": _create_edge_webdriver,
}


def get_driver():
    # Purpose: Return the active driver, creating it on first call.
    # Why lazy: importing swadl_cfg used to spawn a browser at module load,
    # which leaked Chrome processes from any consumer that imported SWADL
    # but never intended to drive a browser (e.g., a test that should skip,
    # or pywinauto-only automation). Driver now spins up on first access.
    if cfgdict.get(DRIVER) is None:
        method_key = cfgdict[SELENIUM_BROWSER]
        creator = driver_creators.get(method_key)
        if creator is None:
            raise Exception(
                f"Browser '{method_key}' is not yet supported by the framework"
            )
        creator()
    return cfgdict[DRIVER]


def _quit_driver_if_running():
    # Purpose: Quit and clear the active driver if one was created.
    # Called from SWADLBaseAutomation.quit() and SWADLTest.tearDown.
    driver = cfgdict.get(DRIVER)
    if driver is not None:
        try:
            driver.quit()
        except Exception:
            pass
        cfgdict[DRIVER] = None
