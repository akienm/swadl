
from SWADL.engine.swadl_base_test import SWADLTest
from learning.flows.admin_flows import AdminFlows


class Learning_Silentestudio_Tests(SWADLTest):
    # Purpose: Unit tests for SWADL

    def setUp(self):
        # Purpose: Initialize class, which in this case also means instantiate the flow
        super().setUp()
        self.admin_flows = AdminFlows()

    def test_open_page(self):
        # Purpose: Implements the following SWADL unit tests:
        #          - Webdriver is connected
        #          - page.open() works
        #          - page.validate_loaded() works
        # Test does a search and looks for a given result title

        self.admin_flows.validate_UI()

        # self.assert_in(
        #     member=self.test_data[SEARCH_RESULT_STRING],
        #     container=self.test_data[SEARCH_RESULT_TITLES_LIST],
        # )

    # def test_background_gui(self):
    #     # Purpose: Validate all links :
    #
    #     self.learning_silentestudio_flows.validate_background_gui()