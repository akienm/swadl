# File: google_search_page.py
# Purpose: To validate the SWADL (Test Automation Framework)

import logging

from swadl.engine.swadl_constants import VALIDATE_VISIBLE
from seleniumpoc.SWADL.SWADLcontrol import SWADLControl
from seleniumpoc.SWADL.SWADLpagesection import SWADLPageSection

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

    def do_search(self, search_key):
        # Method: do_search
        # Purpose: loads page if it's not loaded
        self.load_page()
        self.search_box.send_keys(value=search_key)
        self.search_box.submit()
