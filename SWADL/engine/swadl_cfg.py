
# standard libraries
import os
from selenium import webdriver

# SWADL libs
from SWADL.engine.swadl_config_dict import ConfigDict
from SWADL.engine.swadl_constants import SELENIUM_BROWSER_OPTIONS, SELENIUM_BROWSER_PLATFORM, SELENIUM_BROWSER_VERSION, \
    SELENIUM_BROWSER, SELENIUM_CONTROL_DEFAULT_TIMEOUT, SELENIUM_PAGE_DEFAULT_TIMEOUT, SELENIUM_TEST_SET_FILE, \
    SWADLTEST_URL, SWADLTEST_VERBOSE, DRIVER
from SWADL.engine.swadl_constants import TEST_DATA
from SWADL.engine.swadl_dict import SWADLDict

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
    SELENIUM_BROWSER: "chrome",
    SELENIUM_CONTROL_DEFAULT_TIMEOUT: 20,
    SELENIUM_PAGE_DEFAULT_TIMEOUT: 40,
    SELENIUM_TEST_SET_FILE: None,
    SWADLTEST_URL: None,
    SWADLTEST_VERBOSE: False,
}

for key in TEST_PARAMETERS:
    cfgdict[key] = os.environ.get(key, TEST_PARAMETERS[key])

# Section: test_data
# Purpose: creates the vehicle by which all other parts communicate
cfgdict[TEST_DATA] = SWADLDict()


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
    # Method:
    # Purpose: To create the chrome specific webdriver.
    cfgdict[DRIVER] = webdriver.Chrome()
    return cfgdict[DRIVER]


def _create_edge_webdriver():
    # Method:
    # Purpose: To create the edge specific webdriver.
    cfgdict[DRIVER] = webdriver.Edge()
    return cfgdict[DRIVER]


driver_creators = {
    "chrome": _create_chrome_webdriver,
    "edge": _create_edge_webdriver,
}

try:
    method_key = cfgdict[SELENIUM_BROWSER]
    method_to_call = driver_creators[method_key]
    method_to_call()
except Exception as e:
    raise Exception(
        f"{e}\nPerhaps {cfgdict[SELENIUM_BROWSER]} is not yet supported by the framework?"
    )
