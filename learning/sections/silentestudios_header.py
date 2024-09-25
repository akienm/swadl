# File: google_search_section.py
# Purpose: To validate the SWADL (Test Automation Framework)

import logging

from SWADL.engine.swadl_constants import VALIDATE_VISIBLE
from SWADL.engine.swadl_control import SWADLControl
from SWADL.engine.swadl_base_section import SWADLPageSection
from Project.flows.google_search_constants import SEARCH_KEY


class SilentestudiosHeader(SWADLPageSection):
    # Purpose: Google search page, for framework unit tests

    def __init__(self, name="SilentestudiosHeader", **kwargs):
        # Purpose: describe the page
        super().__init__(name=name, **kwargs)
        self.url = "https://silentestudios.com"

        self.design_link = SWADLControl(
            name="design_link",
            parent=self,
            selector='.wp-block-navigation-item__content',
            is_text="Design",
            validation={VALIDATE_VISIBLE: True},

        )

        self.interactive_link = SWADLControl(
            name="interactive_link",
            parent=self,
            selector='.wp-block-navigation-item__content',
            is_text="Interactive",
            validation={VALIDATE_VISIBLE: True},
        )

        self.about_link = SWADLControl(
            name="about_link",
            parent=self,
            selector='.wp-block-navigation-item__content',
            is_text="About",
            validation={VALIDATE_VISIBLE: True},
        )

        self.contact_link = SWADLControl(
            name="Contact_link",
            selector='.wp-block-navigation-item__content',
            is_text="Contact",
            validation={VALIDATE_VISIBLE: True},
        )

        # used by self.validate_loaded()
        self.validate_loaded_queue = [self.contact_link]
        self.validate_all = [
            self.design_link,
            self.interactive_link,
            self.about_link,
            self.contact_link,
        ]

    def validate_UI(self):

        self.load_page()
        self.validate_controls(controls=self.validate_all, validation=VALIDATE_VISIBLE)
