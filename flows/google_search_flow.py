# File: google_search_flow
# Purpose: Unit test and demo

from page_sections.google_results_page import GoogleResultSection
from page_sections.google_search_page import GoogleSearchPage


class GoogleFlows():
    # Class: GoogleFlows
    # Purpose: Encapsulates flows for Google used in unit tests

    def __init__(self):
        # Method: __init__
        # Purpose: Initialize the instance. In this case, that includes instantiating the page_sections
        self.google_search_page = GoogleSearchPage()
        self.google_results_page = GoogleResultSection()

    def search(self, search_key):
        # Method: search
        # Purpose: Perform google search
        self.google_search_page.do_search(search_key)

    def validate_in_results(self, search_key):
        # Method: validate_in_results
        # Purpose: Validate that the search_key provided is in the result headers somewhere
        self.google_results_page.validate_google_search_result(search_key)
