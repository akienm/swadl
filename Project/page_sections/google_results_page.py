# File: google_results_page.py
# Purpose: To validate the SWADL (Test Automation Framework)

import logging

from SWADL.engine.swadl_constants import VALIDATE_VISIBLE
from SWADL.engine.swadl_control import SWADLControl
from SWADL.engine.swadl_base_section import SWADLPageSection
from Project.flows.google_search_constants import SEARCH_RESULT_TITLES

logger = logging.getLogger(__name__)


class GoogleResultSection(SWADLPageSection):
    # Purpose: Google search page, for framework unit tests

    def __init__(self, **kwargs):
        # Purpose: Unit test fixture.
        super().__init__(**kwargs)
        self.url = "https://www.google.com"

        # for page load testing
        self.google_icon = SWADLControl(
            name="google_icon",
            parent=self,
            selector='img[alt="Google"]',
            validation=VALIDATE_VISIBLE,
        )
        self.terms_link = SWADLControl(
            name="terms_link",
            parent=self,
            selector='[href*="policies"][href*="terms"]',
            validation=VALIDATE_VISIBLE,
        )
        self.validate_loaded_queue = (self.google_icon, self.terms_link)

        # other controls
        self.search_box = SWADLControl(
            name="search_box",
            parent=self,
            selector='[title="Search"]',
            validation=VALIDATE_VISIBLE,
        )
        self.any_result_header = SWADLControl(
            name="any_result",
            parent=self,
            selector='h3[class="LC20lb DKV0Md"]',
            validation=VALIDATE_VISIBLE,
        )

    def get_matching_results(self, test_data=None):
        # Purpose: Returns matching test results if any
        # Inputs: - (str)string_to_test - item to search for
        # Notes: Google specific!
        # WARNING: DESTROYS CONTENTS OF self.index!!!

        raw_results = self.any_result_header.get_elements()
        raw_count = len(raw_results)
        result_list = []

        for index in range(0, raw_count):
            self.any_result_header.index = index
            result_list.append(self.any_result_header.get_value())
        test_data[SEARCH_RESULT_TITLES] = result_list
