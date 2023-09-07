# File: google_results_page.py
# Purpose: To validate the SWADL (Test Automation Framework)

import logging

from swadl.engine.swadl_constants import VALIDATE_VISIBLE
from seleniumpoc.SWADL.SWADLcontrol import SWADLControl
from seleniumpoc.SWADL.SWADLpagesection import SWADLPageSection

logger = logging.getLogger(__name__)


class GoogleResultSection(SWADLPageSection):
    # Class: GoogleResultSection
    # Purpose: Google search page, for framework unit tests
    def __init__(self, **kwargs):
        # Method: __init__
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

    def validate_google_search_result(self, string_to_test=None):
        # Method: validate_google_search_result
        # Purpose: Validates whether or not a header which contains the specified string exists
        # Inputs: - (str)string_to_test - item to search for
        # Returns: - True if found
        # Notes: Google specific!
        self.any_result_header.has_text = string_to_test
        return self.any_result_header.validate_exist()
