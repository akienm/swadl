# Purpose: search flows for google unit test and demo

from SWADL.engine.swadl_base_flow import SWADLBaseFlow
from Project.page_sections.google_results_section import GoogleResultSection
from Project.page_sections.google_search_section import GoogleSearchSection


class GoogleFlows(SWADLBaseFlow):
    # Purpose: Encapsulates flows for Google used in unit tests

    def __init__(self, name='GoogleFlows', **kwargs):
        # Purpose: Initialize the instance. In this case, that includes instantiating the page_sections
        super().__init__(name=name, **kwargs)
        self.google_search_page = GoogleSearchSection()
        self.google_results_page = GoogleResultSection()

    def search(self):
        # Purpose: Perform google search
        # Keys: "GoogleSearchSection loaded ok": True
        # Keys: Project.flows.google_search_constants.SEARCH_KEY
        self.google_search_page.do_search()

    def get_matching_results(self):
        # Purpose: Validate that the search_key provided is in the result headers somewhere
        # Keys: SEARCH_RESULT_STRING - string to look for
        # Returns: Project.flows.google_search_constants.SEARCH_RESULT_TITLES_LIST
        self.google_results_page.get_matching_results()
