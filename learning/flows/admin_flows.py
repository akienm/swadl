
from SWADL.engine.swadl_base_flow import SWADLBaseFlow
from Project.page_sections.google_results_section import GoogleResultSection
from Project.page_sections.google_search_section import GoogleSearchSection
from learning.sections.silentestudios_header import SilentestudiosHeader


class AdminFlows(SWADLBaseFlow):
    # Purpose: Encapsulates flows for Google used in unit tests

    def __init__(self, name='AdminFlows', **kwargs):
        # Purpose: Initialize the instance. In this case, that includes instantiating the page_sections
        super().__init__(name=name, **kwargs)
        self.silentestudio_header_page = SilentestudiosHeader()

    def validate_UI(self):
        # Purpose: Perform google search
        # Keys: "GoogleSearchSection loaded ok": True
        # Keys: Project.flows.google_search_constants.SEARCH_KEY
        self.silentestudio_header_page.load_page()
        self.silentestudio_header_page.validate_UI()
