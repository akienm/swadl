
# File: google_unit_tests
# Purpose: Akien's first unit tests for SWADL

from learning.flows.hdhs_flows import HDHSFlows
from SWADL.engine.swadl_base_test import SWADLTest


class HDHSSmokeTests(SWADLTest):
    # Purpose: Unit tests for SWADL

    def setUp(self):
        # Purpose: Initialize class, which in this case also means instantiate the flow
        super().setUp()
        self.hdhs_flows = HDHSFlows()

    def test_open_page(self):
        # Purpose: Implements the following SWADL unit tests:
        #          - Webdriver is connected
        #          - page.open() works
        #          - page.validate_loaded() works
        # Test does a search and looks for a given result title

        self.hdhs_flows.hdhs_header_validate_controls(self.test_data)

        pass

