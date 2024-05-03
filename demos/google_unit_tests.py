
# File: google_unit_tests
# Purpose: Akien's first unit tests for SWADL
import logging

from demos.google_search_flow import GoogleFlows
from engine.swadl_test import SWADLTest


logger = logging.getLogger(__name__)


class TestGoogleSearchSWADLUnitTests(SWADLTest):
    # Class: TestGoogleSearchSWADLUnitTests
    # Purpose: Unit tests for SWADL

    def setUp(self):
        # Method: __init__
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
        self.google_flows.search("Chromedriver")
        self.google_flows.validate_in_results("ChromeDriver - WebDriver for Chrome")
