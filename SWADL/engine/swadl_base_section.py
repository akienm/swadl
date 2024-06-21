# File: SWADLpagesection.py
# Purpose: Defines a proxy for page objects

import logging

from SWADL.engine.swadl_cfg import cfgdict
from SWADL.engine.swadl_constants import NAME
from SWADL.engine.swadl_constants import SELENIUM_PAGE_DEFAULT_TIMEOUT
from SWADL.engine.swadl_constants import VALIDATE_VISIBLE
from SWADL.engine.swadl_base import SWADLBase

logger = logging.getLogger(__name__)


class SWADLPageSection(SWADLBase):
    # Purpose: Represents a portion of a page
    # Usage:
    #       class HomePageHeader(SWADLPageSection):
    #           # Class: HomePageHeader
    #           # Purpose: Header for the home page, includes login
    #           name = "HomePageHeader"
    #           user_name = SWADLControl(
    #               data_key=USER_NAME,
    #               name=f'{name}.user_name',
    #               selector='css=[name=="User"]',
    #               validation=validation_input_type,
    #           )
    #           password = SWADLControl(
    #               data_key=PASSWORD,
    #               name=f'{name}.password',
    #               selector='css=[name=="password"]',
    #               validation=validation_input_type,
    #           )
    #           login = SWADLControl(
    #               data_key=True,  # on pushbutton, this causes click during test
    #               name=f'{name}.login_button',
    #               selector='css=[name=="advance"]',
    #               validation=validation_login_button,
    #           )
    #           controls_prove_loaded = (password, login)
    #           default_self_test = (user_name, password, login)
    #       ....
    #       class LoginFlow(SWADLBase):
    #           # Class: LoginFlow
    #           # Purpose: Provides login flow to other flows or to tests.
    #           def do_login(**kwargs):
    #               # Method: do_login(**kwargs)
    #               # Purpose: Performs login
    #               home_page_header = HomePageHeader(name="(HomePageHeader)home_page_header")
    #               user_home_page = UserHomePage(name="(UserHomePage)user_home_page)
    #               home_page_header.do_login()
    #               user_home_page.validate_loaded()

    url = None
    # Purpose: In the instance, may contain the url for this page section.
    # Users: open()

    def __init__(self, *args, name=None, **kwargs):
        # Purpose: Set the name based on the class
        kwargs[NAME] = name if name else self.__class__.__name__
        super().__init__(*args, **kwargs)

    def open(self, url=None, timeout=cfgdict[SELENIUM_PAGE_DEFAULT_TIMEOUT]):
        # Purpose: Open a page
        # Inputs: - (str)url - url to open, if None, looks for self.url
        #         - (float)timeout - seconds to wait before throwing an error
        # Notes: IMPORTANT! Experience shows some Chrome behavior of stalling on page loads with
        #        `data;` in the address box. 20200930AMM: We may need a link based loader if this
        #        becomes an issue.
        url = url or self.url
        assert url, "Unable to Section.open() with the url of 'None'."
        self.driver.get(url)

    def load_page(self, test_data=None):
        # Purpose: Load the specified page and validate that it was loaded.
        if not self.validate_loaded(fatal=False, report=False, timeout=0.5):
            self.open()
        else:
            logger.debug(
                f"SWADL.{self.get_name()}.load_page() asked to load page already loaded for "
                f"{self.url}"
            )
        self.validate_loaded()


    def validate_controls(self, controls=None, validation=None, **kwargs):
        # Purpose: Validates a collection of controls.
        # Inputs: - controls - A collection of either:
        #             - SWADLControl objects
        #             - tuples of (SWADLControl, validation_dict)
        #         - validation - a validation_dict or None
        # Returns: - (bool) whether all the controls validated True.
        # Notes:
        #             In the case of a SWADLControl, it's expected to have a .validation dict on
        #             the control instance itself. The collection form uses an explicit dict. In
        #             either case the dict has VALIDATE_ keywords such as:
        #             - VALIDATE_VISIBLE which can be:
        #                   - None: Do not process this control
        #                   - True: Log an error if control is not visible
        #                   - False: Log an error if control is visible
        #             - VALIDATE_ENABLED (as with VALIDATE_VISIBLE)
        #             - VALIDATE_EXIST (as with VALIDATE_VISIBLE)
        #             - VALIDATE_UNIQUE (as with VALIDATE_VISIBLE)
        #             - VALIDATE_PROPERTY - None or collection of:
        #                   - 0=(str)name,
        #                   - 1=(bool)match,
        #                   - 2=(any)value
        # Notes
        #   20201001AMM: Big debate with myself about whether this should go here or in SWADLBase.
        #                There it's available to "controls", which could make use of it when it's
        #                a composite control made from many elements. As of this writing, I have
        #                the tiniest leaning toward moving it later if it's proven to be needed.
        assert controls is not None, (
            f"{self.get_name()} cannot .process_controls() on an empty set of controls"
        )
        assert hasattr(controls, '__getitem__'), (
            f"{self.get_name()} cannot passed 'controls' because it's not a list/tuple. "
            f"Instead got '{controls}'"
        )
        result = True
        for control in controls:
            try:
                # first we set the value of value to control.
                value = control
                # this will raise if it's just a control and not a tuple, which is fine
                control = value[0]
                # if we haven't been passed an override validation, and
                # if we have been passed a tuple, then
                # lets see if we were also passed a validation
                if not validation:
                    # this will fail if it's a set of one element, but that's OK too.
                    validation = value[1]
            except Exception:
                # because it doesn't matter if we got errors, that's a planned for case
                pass

            # now validate the control, using the validation variable, which might be None
            new_result = False  # This is here so I can examine the output
            new_result = control.validate(validation=validation, **kwargs)
            result = result and new_result
        return result

    validate_loaded_queue = None
    # Purpose: (list/tuple) Used to contain references to the list of controls that will prove the
    #          Section is loaded. None gets overridden in the instance with a list of controls for
    #          that Section.
    # Users: validate_loaded()

    def validate_loaded(self, controls=None, fatal=True, timeout=None, **kwargs):
        # Purpose: Vaildates that all the specified controls are visible
        # Inputs: (collection)controls - controls to verify. If not specified, tries to use
        #                                self.validate_loaded_queue
        if timeout is None:
            if hasattr(self, SELENIUM_PAGE_DEFAULT_TIMEOUT):
                timeout = self.SELENIUM_PAGE_DEFAULT_TIMEOUT
            else:
                timeout = cfgdict[SELENIUM_PAGE_DEFAULT_TIMEOUT]
        if not controls:
            controls = self.validate_loaded_queue
        result = self.validate_controls(
            controls=controls,
            fatal=fatal,
            timeout=timeout,
            validation={VALIDATE_VISIBLE: True},
            **kwargs,
        )
        return result
