# File: google_search_section.py
# Purpose: To validate the SWADL (Test Automation Framework)

import logging

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

        self.about_link = SWADLControl(
            name="about_link",
            parent=self,
            selector='.MV3Tnb',
            index= 0,
            validation={VALIDATE_VISIBLE: True},
        )
        self.store_link = SWADLControl(
            name="store_link",
            parent=self,
            selector='.MV3Tnb',
            index= 1,
            validation={VALIDATE_VISIBLE: True},
        )
        self.gmail_link = SWADLControl(
            name="gmail_link",
            parent=self,
            selector='.gN089b',
            index=0,
            validation={VALIDATE_VISIBLE: True},
        )
        self.img_link = SWADLControl(
            name="img_link",
            parent=self,
            selector='.gb_y:nth-child (1)',
            validation={VALIDATE_VISIBLE: True},
        )
        self.search_button = SWADLControl(
            name="search_button",
            parent=self,
            selector='.gN089b',
            index=1,
            validation={VALIDATE_VISIBLE: True},
        )
        self.lucky_button = SWADLControl(
            name="lucky_button",
            parent=self,
            selector='.gN089b ',
            index=2,
            validation={VALIDATE_VISIBLE: True},
        )
        # used by self.validate_loaded()
        self.validate_loaded_queue = [self.search_box]
        self.validate_all = [
            self.search_box,
            self.about_link,
            self.store_link,
            self.about_link,
            self.gmail_link,
            self.search_button,
            self.img_link,
            self.lucky_button,
        ]

    def do_search(self):
        # Purpose: loads page if it's not loaded
        # Keys: SEARCH_KEY
        # Emits: "GoogleSearchSection loaded ok": True" = page load validated

        self.load_page()
        self.search_box.send_keys(value=self.test_data[SEARCH_KEY])
        self.search_box.submit()

    def validate_background_gui(self):
        # purpose: confirms visibility of controls
        # Keys: VALIDATE_VISIBLE
        # Output:
        self.load_page()
        self.validate_controls(controls=self.validate_all, validation=VALIDATE_VISIBLE)