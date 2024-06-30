
# File: google_unit_tests
# Purpose: Akien's first unit tests for SWADL
import logging

from Project.flows.google_search_constants import SEARCH_KEY, SEARCH_RESULT_TITLES_LIST
from Project.flows.google_search_constants import SEARCH_RESULT_STRING
from Project.flows.google_search_constants import SEARCH_RESULT_TITLES
from Project.flows.google_search_flow import GoogleFlows
import SWADL.engine.swadl_base_test
from SWADL.engine.swadl_constants import FINAL_RESULT_MESSAGE, FAILED, PASSED

logger = logging.getLogger(__name__)


class TestGoogleSearchSWADLUnitTests(SWADL.engine.swadl_base_test.SWADLTest):
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
        #          - control.validate() works

        self.test_data[SEARCH_KEY] = "Chromedriver"
        self.test_data[SEARCH_RESULT_STRING] = "ChromeDriver XXoverview - Chrome for Developers"

        self.google_flows.search()
        self.google_flows.get_matching_results()

        #TODO: Put all this into the assertions on the base class (since this is an "in" comparison)
        # Produce result message
        if self.test_data[SEARCH_RESULT_STRING] in self.test_data[SEARCH_RESULT_TITLES_LIST]:
            result = PASSED
            found = "found"
        else:
            result = FAILED
            found = "NOT FOUND"
        self.test_data[FINAL_RESULT_MESSAGE] = (
            f"{self.name} reports {result}, "
            f"The expected search result was {found}. "
            "Expected to find "
            f"'{self.test_data[SEARCH_RESULT_STRING]}' in {self.test_data[SEARCH_RESULT_TITLES_LIST]}"
        )

        # fail the test if necessary, else print the passing message
        if result == FAILED:
            raise AssertionError(self.test_data[FINAL_RESULT_MESSAGE])
        print(self.test_data[FINAL_RESULT_MESSAGE])
