# File: google_results_section.py
# Purpose: To validate the SWADL (Test Automation Framework)

import logging

from SWADL.engine.swadl_constants import VALIDATE_VISIBLE
from Project.flows.google_search_constants import SEARCH_RESULT_STRING, SEARCH_RESULT_TITLES_LIST
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

        self.google_icon = SWADLControl(
            name="google_icon",
            parent=self,
            selector='img[alt="Google"]',
            validation=VALIDATE_VISIBLE,
        )
        self.search_box = SWADLControl(
            name="search_box",
            parent=self,
            selector='#APjFqb',
            validation=VALIDATE_VISIBLE,
        )
        self.any_result_header = SWADLControl(
            name="any_result",
            parent=self,
            selector='h3[class="LC20lb MBeuO DKV0Md"]',  #.DKV0Md
            validation=VALIDATE_VISIBLE,
        )
        self.validate_loaded_queue = (self.google_icon, self.search_box)

    def get_matching_results(self):
        # Purpose: Returns matching test results if any
        # Inputs: SEARCH_RESULT_STRING - item to search for
        # Returns: SEARCH_RESULT_TITLES_LIST
        #          '{self.name} raw matching elements'
        # Notes: DESTROYS CONTENTS OF self.index!!!
        #        Uses has_text rather than is_text
        self.validate_loaded()  # this line logs entry to this page in the test_data

        raw_elements = f'{self.name} raw matching elements'
        self.any_result_header.has_text = self.test_data[SEARCH_RESULT_STRING]
        self.test_data[raw_elements] = self.any_result_header.get_elements()
        raw_count = len(self.test_data[raw_elements])
        self.test_data[SEARCH_RESULT_TITLES_LIST] = []

        for index in range(0, raw_count):
            self.any_result_header.index = index
            found_value = self.any_result_header.get_value()
            self.test_data[SEARCH_RESULT_TITLES_LIST].append(found_value)
