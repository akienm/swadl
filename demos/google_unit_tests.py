
# File: google_unit_tests
# Purpose: Akien's first unit tests for SWADL
import logging

from flows.google_search_constants import SEARCH_KEY, SEARCH_RESULT
from flows.google_search_flow import GoogleFlows
import engine.swadl_test


logger = logging.getLogger(__name__)


class TestGoogleSearchSWADLUnitTests(engine.swadl_test.SWADLTest):
    # Class: TestGoogleSearchSWADLUnitTests
    # Purpose: Unit tests for SWADL

    def setUp(self):
        # Method: setUp
        # Purpose: Initialize class, which in this case also means instantiate the flow
        super().setUp()
        self.google_flows = GoogleFlows()

    def test_open_page(self):
        # Method: test_open_page
        # Purpose: Implements the following SWADL unit tests:
        #          - Webdriver is connected
        #          - page.open() works
        #          - page.validate_loaded() works
        #          - control.validate() works
        self.test_data[SEARCH_KEY] = "Chromedriver"
        self.test_data[SEARCH_RESULT] = "ChromeDriver - WebDriver for Chrome"
        self.google_flows.search(self.test_data)
        self.google_flows.validate_in_results(self.test_data)
