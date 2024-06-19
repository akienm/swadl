# File: google_search_page.py
# Purpose: To validate the SWADL (Test Automation Framework)

import logging

from engine.swadl_constants import VALIDATE_VISIBLE
from engine.swadl_control import SWADLControl
from engine.swadl_page_section import SWADLPageSection
from flows.google_search_constants import SEARCH_KEY

logger = logging.getLogger(__name__)


class GoogleSearchPage(SWADLPageSection):
    # Class: GoogleSearchPage
    # Purpose: Google search page, for framework unit tests
    def __init__(self, **kwargs):
        # Method: __init__
        # Purpose: Unit test fixture.
        super().__init__(**kwargs)
        self.url = "https://www.google.com"

        self.search_box = SWADLControl(
            name="search_box",
            parent=self,
            selector='[name="q"]',
            validation={VALIDATE_VISIBLE: True},
        )

        self.validate_loaded_queue = [self.search_box]

    def do_search(self, test_data=None):
        # Method: do_search
        # Purpose: loads page if it's not loaded
        self.load_page(test_data)
        self.search_box.send_keys(value=test_data[SEARCH_KEY])
        self.search_box.submit()  # TODO: AMM Asks if we need to make this take test_data as well...
