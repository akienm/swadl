# Purpose: search flows for google unit test and demo

from SWADL.engine.swadl_base_flow import SWADLBaseFlow
from learning.page_sections.hdhs_header import HDHSHeader

class HDHSFlows(SWADLBaseFlow):
    # Purpose: Encapsulates flows for Google used in unit tests

    def __init__(self, name='GoogleFlows', **kwargs):
        # Purpose: Initialize the instance. In this case, that includes instantiating the page_sections
        super().__init__(name=name, **kwargs)
        self.hdhs_header_page = HDHSHeader()

    def hdhs_header_validate_controls(self, test_data):
        # Purpose: Perform google search
        # Keys: "GoogleSearchSection loaded ok": True
        # Keys: Project.flows.google_search_constants.SEARCH_KEY
        self.hdhs_header_page.hdhs_header_validate_controls(test_data)

