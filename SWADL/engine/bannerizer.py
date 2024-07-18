# File: SWADLhelpers.py
# Purpose: "everything else"
from SWADL.engine.swadl_constants import ID

OBJECT_ALREADY_DISPLAYED = '*** OBJECT ALREADY DISPLAYED ABOVE ***'
indents = 4


class Bannerize:
    # Purpose: To format dictionaries, lists and other objects in a way
    # That can allow us to use the dictionary as a logging object
    # in particular, for the SWADL test_data object, config dict and
    # test objects. This produces output that looks like this:
    # {
    #     "test object": {
    #         "_testMethodName": "test_open_page"
    #         "_outcome": <unittest.case._Outcome object at 0x0000019ABA48E150>
    #         }
    #         "name": "(TestGoogleSearchSWADLUnitTests)test_open_page"
    #         "ID": "(TestGoogleSearchSWADLUnitTests)test_open_page"
    #         "parent": None
    #         "cfgdict": {
    #             "ID": "CONFIG_DICT"
    #             "SELENIUM_BROWSER_OPTIONS": None
    #             "SELENIUM_BROWSER_PLATFORM": "WINDOWS"
    #             "SELENIUM_BROWSER_VERSION": ""
    #             "SELENIUM_BROWSER": "chrome"
    #             "SELENIUM_CONTROL_DEFAULT_TIMEOUT": 20
    #             "SELENIUM_PAGE_DEFAULT_TIMEOUT": 40
    #             "SELENIUM_TEST_SET_FILE": None
    #             "SELENIUM_URL": None
    #             "SWADLTEST_VERBOSE": False
    #             "TEST_DATA": {
    #                 "ID": "TEST_DATA"
    #                 "TEST_OBJECT": test_open_page (google_unit_tests.TestGoogleSearchSWADLUnitTests.test_open_page)
    #                 "SEARCH_KEY": "Chromedriver"
    #                 "SEARCH_RESULT": "ChromeDriver overview - Chrome for Developers"
    #                 "GoogleSearchSection loaded ok": True
    #                 "GoogleResultSection loaded ok": True
    #                 "GoogleResultSection raw matching elements": [
    #                     <selenium.webdriver.remote.webelement.WebElement (session="6855ae5be30b43a86d8f92f9e6fb2993"
    #                 ]
    #                 "SEARCH_RESULT_TITLES_LIST": [
    #                     "ChromeDriver overview - Chrome for Developers"
    #                 ]
    #                 "FINAL_RESULT_MESSAGE": "(TestGoogleSearchSWADLUnitTests)test_open_page reports 😇 Passed, T
    #             }
    #             "driver": <selenium.webdriver.chrome.webdriver.WebDriver (session="6855ae5be30b43a86d8f92f9e6fb2
    #             "test_name": "google_unit_tests.TestGoogleSearchSWADLUnitTests.test_open_page"
    #             "failure_log": <SWADL.engine.swadl_output.Output object at 0x0000019AB9FAAC50>/google_unit_tests
    #             "result_log": <SWADL.engine.swadl_output.Output object at 0x0000019ABA575390>/google_unit_tests.
    #         }
    #         "driver": *** OBJECT ALREADY DISPLAYED ABOVE ***
    #         "test_data": *** OBJECT ALREADY DISPLAYED ABOVE ***
    #         "substitution_sources": [
    #             *** OBJECT ALREADY DISPLAYED ABOVE ***
    #         ]
    #         "google_flows": <Project.flows.google_search_flow.GoogleFlows object at 0x0000019ABA48EB90>/google_u
    #     }
    # }

    def __init__(self):
        # Set up instance data
        self.indent = 0
        self.final_result = ''
        self.indent_char = ' '
        self.list_of_completed_objects = []
        self.types_that_got_substituted = []
        self.types_to_treat_as_string = (bool, str, int, tuple, float)

    def ind(self, data):
        # Purpose: Return an indented version of data
        return (self.indent * self.indent_char) + data

    def check_for_dupes(self, item):
        # Purpose: Look to see if this item has already been displayed once in this run.
        # Keeps us out of infinite loops
        if item is not None:
            if not isinstance(item, self.types_to_treat_as_string):
                # here we're creating a key that has both the id and the item.__str__()
                # because otherwise an empty list will just look like any other
                # empty list we've already displayed.
                item_id_string = ""

                # Now we check to see if it's a dict with an ID field
                if isinstance(item, dict) and ID in item.keys():
                    item_id_string += item[ID]
                elif hasattr(item, "get_name"):
                    item_id_string += item.get_name()
                else:
                    item_id_string += f"{item}"
                    # TODO: Remove me if OK: item_id_string = item_id_string[:60]
                item_id_string += f" with OID of {id(item)}"
                # Is it in the list of things already done?
                if item_id_string in self.list_of_completed_objects:
                    self.types_that_got_substituted.append(item_id_string)
                    item = f'{OBJECT_ALREADY_DISPLAYED} as {item_id_string}'
                else:
                    # No? then add it
                    self.list_of_completed_objects.append(item_id_string)
        return item

    def bannerize(self, data=None, iteration=0):
        # Purpose: This is the meat of the matter. here we set up the
        # formatting for each item on a line by line basis. Dicts and lists
        # get set up for, then we recurse thru the items, and finally we
        # mop up for the item with closing brackets or braces.
        # If just a string is passed, it's just added to the output
        iteration += 1
        if isinstance(data, dict):
            if len(data.keys()) > 0:
                self.final_result += '{\n'
                self.indent += indents
                for key, item in data.items():
                    self.final_result += self.ind(f'"{key}": ')
                    item = self.check_for_dupes(item)
                    self.bannerize(data=item, iteration=iteration)
                self.indent -= indents
                self.final_result += self.ind('}\n')
            else:
                self.final_result += '{}}\n'
        elif isinstance(data, list):
            if len(data) > 0:
                self.final_result += '[\n'
                self.indent += indents
                for item in data:
                    item = self.check_for_dupes(item)
                    self.final_result += self.ind('')
                    self.bannerize(data=item, iteration=iteration)
                self.indent -= indents
                self.final_result += self.ind(']')
                self.final_result += '\n'
            else:
                self.final_result += '[]\n'
        else:
            if isinstance(data, str):
                if not data == OBJECT_ALREADY_DISPLAYED:
                    data = f'"{data}"'
            self.final_result += data.__str__()
            self.final_result += '\n'

        iteration -= 1
        if iteration > 20:
            raise Exception(f"infinite loop in bannerizer: {data}")


def bannerize(data, title=None):
    # Purpose: This is the front end for the bannerizer.
    # See the class definition above for the output sample
    # title is optional, but can be used to create a outer dict
    # with the title as the key
    if title:
        data = {title: data}
    bannerizer = Bannerize()
    bannerizer.bannerize(data)
    return bannerizer.final_result

