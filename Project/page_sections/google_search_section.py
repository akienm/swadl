# File: google_search_section.py
# Purpose: To validate the SWADL (Test Automation Framework)

from SWADL.engine.swadl_constants import VALIDATE_VISIBLE
from SWADL.engine.swadl_control import SWADLControl
from SWADL.engine.swadl_base_section import SWADLPageSection
from Project.flows.google_search_constants import SEARCH_KEY


class GoogleSearchSection(SWADLPageSection):
    # Purpose: Google search page, for framework unit tests

    def __init__(self, name="GoogleSearchSection", **kwargs):
        # Purpose: describe the page
        super().__init__(name=name, **kwargs)
        self.url = "https://www.google.com"

        self.search_box = SWADLControl(
            name="search_box",
            parent=self,
            selector='#APjFqb',
            validation={VALIDATE_VISIBLE: True},
        )

        # used by self.validate_loaded()
        self.validate_loaded_queue = [self.search_box]

    def do_search(self):
        # Purpose: loads page if it's not loaded
        # Keys: SEARCH_KEY
        # Emits: "GoogleSearchSection loaded ok": True" = page load validated

        self.load_page()
        self.search_box.set_value(value=self.test_data[SEARCH_KEY])
        self.search_box.submit()
