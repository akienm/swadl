
# File: google_unit_tests
# Purpose: Akien's first unit tests for SWADL

from Project.flows.google_search_constants import SEARCH_KEY
from Project.flows.google_search_constants import SEARCH_RESULT_TITLES_LIST
from Project.flows.google_search_constants import SEARCH_RESULT_STRING
from Project.flows.google_search_flow import GoogleFlows
from SWADL.engine.swadl_base_test import SWADLTest


class TestGoogleSearchSWADLUnitTests(SWADLTest):
    # Purpose: Unit tests for SWADL

    def setUp(self):
        # Purpose: Initialize class, which in this case also means instantiate the flow
        super().setUp()
        self.google_flows = GoogleFlows()

    def test_open_page(self):
        # Purpose: Implements the following SWADL unit tests:
        #          - Webdriver is connected
        #          - page.open() works
        #          - page.validate_loaded() works
        # Test does a search and looks for a given result title

        self.test_data[SEARCH_KEY] = "Chromedriver"
        self.test_data[SEARCH_RESULT_STRING] = "ChromeDriver overview - Chrome for Developers"

        self.google_flows.search()
        self.google_flows.get_matching_results()

        self.assert_in(
            member=self.test_data[SEARCH_RESULT_STRING],
            container=self.test_data[SEARCH_RESULT_TITLES_LIST],
        )

    def test_background_gui(self):
        # Purpose: Validate all links :

        self.google_flows.validate_background_gui()