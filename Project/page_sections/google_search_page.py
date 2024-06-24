# File: google_search_page.py
# Purpose: To validate the SWADL (Test Automation Framework)

import logging

from SWADL.engine.swadl_constants import VALIDATE_VISIBLE
from SWADL.engine.swadl_control import SWADLControl
from SWADL.engine.swadl_base_section import SWADLPageSection
from Project.flows.google_search_constants import SEARCH_KEY

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

    def do_search(self):
        # Purpose: loads page if it's not loaded
        # Inputs: SEARCH_KEY
        self.load_page()
        # This
        self.search_box.send_keys(value=self.test_data[SEARCH_KEY])
        self.search_box.submit()
