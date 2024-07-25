
# File: google_unit_tests
# Purpose: Akien's first unit tests for SWADL

from Project.flows.google_search_constants import SEARCH_KEY
from Project.flows.google_search_constants import SEARCH_RESULT_TITLES_LIST
from Project.flows.google_search_constants import SEARCH_RESULT_STRING
from Project.flows.google_search_flow import GoogleFlows
import SWADL.engine.swadl_base_test
from SWADL.engine.swadl_constants import FINAL_RESULT_MESSAGE, FAILED, PASSED



class TestGoogleSearchSWADLUnitTests(SWADL.engine.swadl_base_test.SWADLTest):
    # Purpose: Unit tests for SWADL

    def setUp(self):
        # Purpose: Initialize class, which in this case also means instantiate the flow
        super().setUp()
        self.google_flows = GoogleFlows()

    def test_background_gui(self):
        # Purpose: Validate all links :

        self.google_flows.validate_background_gui()


