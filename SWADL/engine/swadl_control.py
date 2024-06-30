"""
File: SWADLcontrol.py
Purpose: the control proxy object
"""
import logging
import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from SWADL.engine.swadl_base import SWADLBase
from SWADL.engine.swadl_constants import CACHE
from SWADL.engine.swadl_constants import CLICK
from SWADL.engine.swadl_cfg import cfgdict
from SWADL.engine.swadl_constants import ENABLED
from SWADL.engine.swadl_constants import EXIST
from SWADL.engine.swadl_constants import FAILURE_LOG
from SWADL.engine.swadl_constants import RESULT_LOG
from SWADL.engine.swadl_constants import SELENIUM_CONTROL_DEFAULT_TIMEOUT
from SWADL.engine.swadl_constants import SELENIUM_PAGE_DEFAULT_TIMEOUT
from SWADL.engine.swadl_constants import UNIQUE
from SWADL.engine.swadl_constants import VALIDATE_CLICK
from SWADL.engine.swadl_constants import VALIDATE_ENABLED
from SWADL.engine.swadl_constants import VALIDATE_EXIST
from SWADL.engine.swadl_constants import VALIDATE_INPUT
from SWADL.engine.swadl_constants import VALIDATE_TEXT
from SWADL.engine.swadl_constants import VALIDATE_UNIQUE
from SWADL.engine.swadl_constants import VALIDATE_VISIBLE
from SWADL.engine.swadl_constants import VALUE
from SWADL.engine.swadl_constants import VISIBLE
from SWADL.engine.swadl_dict import SWADLDict
from SWADL.engine.swadl_utils import get_timestamp, bannerize
from SWADL.engine.swadl_output import Output

logger = logging.getLogger(__name__)

# Datum: accumulated_failures
# Purpose: All failed control validations
accumulated_failures = []


class SWADLControl(SWADLBase):
    """
    Class: SWADLControl
    Purpose: Interfaces to controls
    Notes:
        Through most of these calls
        - The keyword `timeout` means keep retrying until that amount of seconds has passed.
        - keyword `end_time` means keep trying until this time is reached.
        timeout is used to create end_time. A series of operations can pass along the timeout
        value, or more easily, if end_time isn't passed, use timeout to produce a new end_time.
        Then pass the end_time from function to function. Each function should attempt it's
        operation, and then if it fails and the time isn't met yet, then retry. This assures
        each call is performed at least once.
    """

    """
    Datum: has_text
    Purpose: if the element "has this text" (in it)
    Notes: is_text wins over has_text
    """
    has_text = None

    """
    Datum: index
    Purpose: if specified means the nth item to match
    Notes: index is appied AFTER is_text or has_text
    """
    index = None

    """
    Datum: is_text
    Purpose: if the element text matches this text exactly
    Notes: is_text wins over has_text
    """
    is_text = None

    """
    Datum: key
    Purpose: if calling validate_input or similr, this means get the data from
             cfgdict[SUBSTITUTION_SOURCES]
    Notes: String or real
    """
    key = None

    def __init__(self, **kwargs):
        """
        Method: __init__
        Purpose: Initialize instance
        Args:
            - selector (string/required) the CSS selector to use for the control
            - name (string/required) the name of the control to use in reporting
            - **kwargs - All other arguments are applied to the object as object properties.
        Valid Object Properties Which Affect Behavior
            - has_text (string/None) if this text is present in an element found with the
              provided selector
            - is_text (string/None) if this text is an exact match for the text found in an
              element found with the provided selector (is_text overrides has_text)
            - index (int/None) A value on this property means this is the nth match. Index matches
              are done after is_text/has_text
            - VALIDATE_CLICK (bool/None) if True, calling validate() will cause the control to be
              cliked on.
            - VALIDATE_ENABLED (bool/None) if a value is specified, the validate() call will attempt
              to validate that the control's state matches the boolean value
            - VALIDATE_EXIST (bool/None) if a value is specified, the validate() call will attempt
              to validate that the control's state matches the boolean value
            - VALIDATE_INPUT (bool/None) if set, use the control's
            - VALIDATE_TEXT (string/None) if a value is specified, the validate() call will attempt
              to validate that the control's state matches the boolean value.
            - VALIDATE_UNIQUE (bool/None) if a value is specified, the validate() call will attempt
              to validate that the control's state matches the boolean value
            - VALIDATE_VISIBLE (bool/None) if a value is specified, the validate() call will attempt
              to validate that the control's state matches the boolean value
        """
        assert 'selector' in kwargs, "Controls must have a selector property at instantiation"
        self.validation = None
        super().__init__(**kwargs)
        self.clear_cached_status()
        self.mater_validation_table = {
            VALIDATE_ENABLED: self.validate_enabled,
            VALIDATE_EXIST: self.validate_exist,
            VALIDATE_TEXT: self.validate_text,
            VALIDATE_UNIQUE: self.validate_unique,
            VALIDATE_VISIBLE: self.validate_visible,
            # these last two are out of order on purpose, we want to verify the others first,
            # and in particular button has to be last, as sometimes clicking a button causes the
            # shift to a new page.
            VALIDATE_INPUT: self.validate_input,
            VALIDATE_CLICK: self.validate_click,
        }

    def _check_actionable(self, end_time=None, force=False, kwargs=None,
                          timeout=cfgdict[SELENIUM_PAGE_DEFAULT_TIMEOUT]):
        """
        Method: _check_clickable
        Purpose: Applies kwargs, calculates end_time, and runs all the checks to see that a control
                 is actionable.
        Args:
            - end_time (time float/None): time when to give up on getting the element
            - force (bool/None): force reload of cache
            - kwargs (dict/None): passed arguments to apply to object properties
            - timeout (float/20): time to wait to get elements before failing
        Returns:
            tuple of (end_time, element_list)
        Notes:
            I created this so I wouldn't have to keep doing this same block on every method.
        """
        if kwargs:
            self.apply_kwargs(kwargs)
        end_time = end_time if end_time else time.time() + timeout
        if force:
            self.clear_cached_status()
        element_list = self.get_elements(end_time=end_time)

        assert len(element_list) > 0, (
            f"Can't find an element that matches {self.selector}"
        )
        assert len(element_list) == 1, (
            f"{self.get_name()} Can't operate on multiple elements, found {len(element_list)} "
            f"matches for {self.selector}"
        )
        assert element_list[0].is_enabled(), (
            f"Can't find an enabled element that matches {self.selector}"
        )
        assert element_list[0].is_displayed(), (
            f"Can't find a visible element that matches {self.selector}"
        )
        return (end_time, element_list)

    def click(self, end_time=None, force=False,
              timeout=cfgdict[SELENIUM_PAGE_DEFAULT_TIMEOUT], **kwargs):
        """
        Method: click
        Purpose: Click on the control
        Args:
            - end_time (time float/0) time at which user called timeout expires
            - force (bool/False) Forces a reload of the cache
            - timeout (float/20) How long to wait for the control to become ready
            - kwargs are applied as object properties before actions are taken
        Notes:
            1: Should this be called do_click?
            2: This should be a template for similar calls, such as `submit`
        TODO: Add keyword "fallback" that, in the event of failure, retries the click at the x, y
              basically clicking on the location, because something else is higher in the z-order
        """
        end_time, element_list = self._check_actionable(
            end_time=end_time,
            force=force,
            kwargs=kwargs,
            timeout=timeout
        )
        return self._perform_webdriver_call(
            call=self._do_click, expected=True, end_time=end_time, force=force,
        )

    def _do_click(self):
        """
        Method: _do_click
        Purpose: Performs the actual click
        Returns: bool of whether successful
        Notes: Click will fail and this return False if the thing is obscured!
               (See click() for more information)
        """
        try:
            self._elements[0].click()
            self._results[CLICK] = True
        except (TypeError, IndexError):
            self._results[CLICK] = False
        return self._results[CLICK]

    def get_elements(self, end_time=None, timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT],
                     **kwargs):
        """
        Method: get_elements
        Purpose: Fetches elements based on self.selector, self.index, self.is_text and
                 self.has_text (is_text will win if both are present)
        Args:
            - end_time (float time.time()+timeout) - Passed from other methods also doing
                       timeout operations. So we don't have to be constantly recalculating the
                       end time.
            - timeout (float, default=20) - How long until we give up looking for a match
            _ **kwargs - Are applied to the object as object properties before acting.
        """
        self.apply_kwargs(kwargs)
        end_time = end_time if end_time else time.time() + timeout
        processed_selector = self.resolve_substitutions(self.selector)
        processed_list = []
        while True:
            try:
                # The explicit reference here forces everything to be a CSS based selector.
                # TODO: Use prefixes instead, such as css= or xpath=. Add that logic here.
                raw_element_list = self.driver.find_elements(By.CSS_SELECTOR, processed_selector)
                processed_list = []

                if self.is_text:
                    for element in raw_element_list:
                        if self.is_text == element.text:
                            processed_list.append(element)
                elif self.has_text:
                    for element in raw_element_list:
                        if self.has_text in element.text:
                            processed_list.append(element)
                else:
                    processed_list = raw_element_list
                if self.index is not None:
                    assert len(processed_list) > self.index, (
                        f"Index of {self.index} into the list of matching controls is "
                        f"invalid, the number of elements was {len(processed_list)}."
                    )
                    processed_list = [processed_list[self.index]]
                if processed_list:
                    break
            except Exception:
                # we do not care what errors occur, just keep going and retry
                pass
            if time.time() > end_time:
                # we do care wheter we've gone past our end time. But performinng this test
                # here, rather than at the top, means we go thru the loop at least once.
                break
        return processed_list

    def clear_cached_status(self):
        # Method: clear_cached_status
        # Purpose: Reset the cache data to blank. Will cause next option to refetch
        self._elements = []
        self._results = {}

    def get_exist(self, end_time=None, expected=True, force=True,
                  timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Method: get_exist
        # Purpose: Returns true if control exists
        end_time, element_list = self._check_actionable(
            end_time=end_time,
            force=force,
            kwargs=kwargs,
            timeout=timeout
        )
        return self._get_exist(end_time=end_time, expected=expected, timeout=timeout, **kwargs)[0]

    def get_enabled(self, end_time=None, expected=True,
                    timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Method: get_enabled
        # Purpose: Returns true if control enabled
        end_time, element_list = self._check_actionable(
            end_time=end_time,
            kwargs=kwargs,
            timeout=timeout
        )
        return self._get_enabled(end_time=end_time, expected=expected, timeout=timeout, **kwargs)[0]

    def get_value(self, end_time=None, expected=True,
                    timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Method: get_value
        # Purpose: Returns value (text) of the control
        end_time, element_list = self._check_actionable(
            end_time=end_time,
            kwargs=kwargs,
            timeout=timeout
        )
        return self._get_value(end_time=end_time, expected=expected, timeout=timeout, **kwargs)[0]

    def get_visible(self, end_time=None, expected=True,
                    timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Method: get_visible
        # Purpose: Returns true if control visible
        end_time, element_list = self._check_actionable(
            end_time=end_time,
            kwargs=kwargs,
            timeout=timeout
        )
        return self._get_visible(end_time=end_time, expected=expected, timeout=timeout, **kwargs)[0]

    def get_unique(self, end_time=None, expected=True,
                   timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Method: get_unique
        # Purpose: Returns true if control is unique
        end_time, element_list = self._check_actionable(
            end_time=end_time,
            kwargs=kwargs,
            timeout=timeout
        )
        return self._get_unique(end_time=end_time, expected=expected, timeout=timeout, **kwargs)[0]

    def send_keys(self, end_time=None, fatal=False, force=False, value=None,
                  timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        """
        Method: send_keys
        Purpose: Send text input to a control
        Args:
            - fatal (bool/default=False) - Should a failure be fatal
            - force (bool/default=False) - Force cache reload?
            - timeout(float/default=20) - How long to wait for the control to exist
            - value (string/default=None) - Value to type into field
        Returns:
            - True if successful
        """
        end_time, element_list = self._check_actionable(
            end_time=end_time,
            kwargs=kwargs,
            timeout=timeout
        )
        element_list[0].send_keys(value, **self._remove_keys_webdriver_doesnt_like(kwargs))
        return True  # because we were successful if we didn't throw an error

    def submit(self, end_time=None, fatal=False, force=False, value=None,
               timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Method: submit
        # Purpose: Sends submit to the control
        end_time, element_list = self._check_actionable(
            end_time=end_time,
            kwargs=kwargs,
            timeout=timeout
        )
        element_list[0].submit(**self._remove_keys_webdriver_doesnt_like(kwargs))

    def validate_click(self, end_time=None, expected=True, fatal=False, force=True,
                       timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        """
        Method: validate_click
        Purpose: Perform the click as part of the engine based processing of controls
        """
        result, elapsed_time = self.click(force=force, end_time=end_time, timeout=timeout)
        return self._validate(
            elapsed_time=elapsed_time,
            expected=expected,
            fatal=fatal,
            result=result,
            validation_name="Click",
            **kwargs,
        )

    def validate_exist(self, end_time=None, expected=True, fatal=False, force=True,
                       timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Method: validate_exist
        # Purpose: verify whether a control exists
        result, elapsed_time = self._get_exist(end_time=end_time, expected=expected, force=force,
                                               timeout=timeout)
        return self._validate(
            elapsed_time=elapsed_time,
            expected=expected,
            fatal=fatal,
            result=result,
            validation_name=EXIST,
            **kwargs,
        )

    def validate_enabled(self, end_time=None, expected=True, fatal=False, force=False,
                         timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Method: validate_enabled
        # Purpose: verify whether a control is enabled
        result, elapsed_time = self._get_enabled(end_time=end_time, expected=expected, force=force,
                                                 timeout=timeout)
        return self._validate(
            elapsed_time=elapsed_time,
            expected=expected,
            fatal=fatal,
            result=result,
            validation_name=ENABLED,
            **kwargs,
        )

    def validate_input(self=None, end_time=None, expected=True, fatal=False, force=False,
                       timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        """
        Method: validate_input
        Purpose: Perform the input as part of the engine based processing of controls
        """
        start_time = time.time()
        result = self.input(end_time=end_time, timeout=timeout)
        elapsed_time = time.time() - start_time
        return self._validate(
            elapsed_time=elapsed_time,
            expected=expected,
            fatal=fatal,
            result=result,
            validation_name="Input",
            **kwargs,
        )

    def validate_text(self=None, end_time=None, expected=None, fatal=False, force=False,
                      timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Method: validate_text
        # Purpose: verify whether a control's value matches it's VALIDATE_TEXT value
        expected_to_test = expected if expected else self.VALIDATE_TEXT
        result, elapsed_time = self._get_value(
            end_time=end_time, expected=expected_to_test, force=force, timeout=timeout
        )
        comments = f'expected: "{expected_to_test}", actual: "{self._results[VALUE]}"'
        return self._validate(
            comments=comments,
            elapsed_time=elapsed_time,
            expected=expected,
            fatal=fatal,
            result=result,
            validation_name=VALIDATE_TEXT,
            **kwargs,
        )

    def validate_visible(self, end_time=None, expected=True, fatal=False, force=False,
                         timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Method: validate_visible
        # Purpose: verify whether a control is visible
        result, elapsed_time = self._get_visible(end_time=end_time, expected=expected, force=force,
                                                 timeout=timeout)
        return self._validate(
            elapsed_time=elapsed_time,
            expected=expected,
            fatal=fatal,
            result=result,
            validation_name=VISIBLE,
            **kwargs,
        )

    def validate_unique(self, end_time=None, expected=True, fatal=False, force=False,
                        timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Method: validate_unique
        # Purpose: verify whether a control is unique
        result, elapsed_time = self._get_unique(end_time=end_time, expected=expected, force=force,
                                                timeout=timeout)
        return self._validate(
            elapsed_time=elapsed_time,
            expected=expected,
            fatal=fatal,
            result=result,
            validation_name=UNIQUE,
            **kwargs,
        )

    def validate(self, end_time=None, fatal=False, timeout=cfgdict[SELENIUM_PAGE_DEFAULT_TIMEOUT],
                 validation=None, **kwargs):
        # Method: validate
        # Purpose: Given a validation dict, or a self.validation dict (if none is passed)
        #          Then validate that each thing is of the correct value
        # Returns: (bool) was the validation successful
        vaildation = validation or self.validation
        assert vaildation, "SWADLControl.validate() was called with no validations specified."
        end_time = end_time if end_time else time.time() + timeout
        result = True
        for item in vaildation:
            time_remaining = end_time - time.time()
            time_remaining = time_remaining if time_remaining > 0 else 1
            validation_call = self.mater_validation_table[item]
            result = validation_call(fatal=fatal, timeout=time_remaining, **kwargs) and result
        return result

    def _get_exist(self, end_time=None, expected=None, force=True,
                   timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Method: get_exist
        # Purpose: Returns the result of testing the existence of the control
        return self._perform_webdriver_call(
            call=self._query_exist, end_time=end_time, expected=expected, force=force,
            timeout=timeout,
        )

    def _get_enabled(self, end_time=None, expected=None, force=False,
                     timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Method: get_enabled
        # Purpose: Returns the result of testing the enabled status of the control
        return self._perform_webdriver_call(
            call=self._query_enabled, end_time=end_time, expected=expected, force=force,
            timeout=timeout
        )

    def _get_value(self, end_time=None, expected=None, force=False,
                   timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Method: get_value
        # Purpose: Returns the result of testing the VALIDATE_TEXT of the control

        result, elapsed = self._perform_webdriver_call(
            call=self._query_value, end_time=end_time, expected=expected, force=force,
            timeout=timeout,
        )
        import pdb ; pdb.set_trace()
        if expected is None and result:
            result = self._results[VALUE]
        return result, elapsed

    def _get_visible(self, end_time=None, expected=None, force=False,
                     timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Method: get_visible
        # Purpose: Returns the result of testing the visibility of the control
        return self._perform_webdriver_call(
            call=self._query_visible, end_time=end_time, expected=expected, force=force,
            timeout=timeout
        )

    def _get_unique(self, end_time=None, expected=None, force=False,
                    timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Method: get_unique
        # Purpose: Returns the result of testing the unique status of the control
        return self._perform_webdriver_call(
            call=self._query_unique, end_time=end_time, expected=expected, force=force,
            timeout=timeout
        )

    def _query_enabled(self):
        # Method: _get_enabled
        # Purpose: Helper that performs the actual comparison to get the enabled state.
        #          Intended to be a helper method, for internal use
        try:
            self._results[ENABLED] = self._elements[0].is_enabled()
        except TypeError:
            self._results[ENABLED] = False
        return self._results[ENABLED]

    def _query_exist(self):
        # Method: _get_exist
        # Purpose: Helper that performs the actual comparison to get the exist state.
        #          Intended to be a helper method, for internal use
        self._results[EXIST] = bool(self._elements)
        return self._results[EXIST]

    def _query_unique(self):
        #  Method: _get_unique
        # Purpose: Helper that performs the actual comparison to get the unique state.
        #          Intended to be a helper method, for internal use
        self._results[UNIQUE] = len(self._elements) == 1
        return self._results[UNIQUE]

    def _query_value(self):
        # Method: _get_value
        # Purpose: Helper that performs the actual comparison to get the value.
        #          Intended to be a helper method, for internal use
        try:
            import pdb ; pdb.set_trace()
            self._results[VALUE] = self._elements[0].text
        except (TypeError, IndexError):
            self._results[VALUE] = False
        return self._results[VALUE]

    def _query_visible(self):
        # Method: _get_visible
        # Purpose: Helper that performs the actual comparison to get the visible state.
        #          Intended to be a helper method, for internal use
        try:
            self._results[VISIBLE] = self._elements[0].is_displayed()
        except (TypeError, IndexError):
            self._results[VISIBLE] = False
        return self._results[VISIBLE]

    def _refresh(self, end_time=None, expected=None, force=False, timeout=0):
        # Method: _refresh
        # Purpose: Reloads the element list. Intended to be a helper method, for internal use
        if force or not self.__dict__.get(CACHE):
            self.clear_cached_status()
            if expected is False:
                timeout = 0
            self._elements = self.get_elements(end_time=end_time, timeout=timeout)

    def _validate(self, comments='', elapsed_time='', expected=None, fatal=False, report=True,
                  result=None, validation_name=None):
        # Method: _validate
        # Purpose: reports on the pass/fail status of a validation call

        if report:
            if FAILURE_LOG not in cfgdict:
                cfgdict[FAILURE_LOG] = Output('test_failures.log')
                cfgdict[RESULT_LOG] = Output('test_results.log')
            if isinstance(elapsed_time, str):
                elapsed_time = 'not specified'
            else:
                elapsed_time = (
                    '< 0.0001 seconds' if elapsed_time < 0.0001 else
                    f'{round(elapsed_time, 4)} seconds'
                )
            if not result:
                file_name = f'FAILURE_{get_timestamp()}.png'
                self.driver.save_screenshot(file_name)
                report_me = f'    saved image: {file_name},\n'
            else:
                report_me = ''
            message_dict = SWADLDict()
            message_dict = SWADLDict()
            message_dict['result'] = "PASSED" if result else "FAILED"
            message_dict['for control'] = self.get_name()
            message_dict['with selector'] = self.selector
            message_dict['is_text'] = self.is_text
            message_dict['has_text'] = self.has_text
            message_dict['index'] = self.index
            message_dict['validation_name'] = validation_name
            message_dict['expected'] = expected
            message_dict['elapsed_time'] = elapsed_time
            message_dict['fatal'] = fatal
            message_dict['report_me'] = report_me
            message_dict['comments'] = comments
            message = bannerize(data=message_dict, title="SWADL Validation Result")
            # (
            #     f'SWADL_TESTRESULT:\n'
            #     f'    result: {"PASSED" if result else "FAILED"},\n'
            #     f'    for control: {self.get_name()},\n'
            #     f'    with selector: {self.selector},\n'
            #     f'    with is_text: {self.is_text},\n'
            #     f'    with has_text: {self.has_text},\n'
            #     f'    with index: {self.index},\n'
            #     f'    validating: {validation_name},\n'
            #     f'    expected: {expected},\n'
            #     f'    elapsed: {elapsed_time},\n'
            #     f'    fatal: {fatal},\n'
            #     f'{report_me}'
            #     f'    comments: {comments}'
            # )
            cfgdict[RESULT_LOG].add(message)
            if result:
                logger.info(message)
            else:
                logger.critical(message)
                cfgdict[FAILURE_LOG].add(message)
                accumulated_failures.append(message)
            print(message)
            was_not_fatal = not (result is False and fatal is True)
            assert was_not_fatal, f"A fatal error occurred. {message}"

        return result

    def _perform_webdriver_call(self, call, end_time=None, expected=None, force=False,
                                timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Method: _perform_webdriver_call
        # Purpose: Wraps the webdriver call in a time-based retry mechanism (retry until match or
        #          the timeout expires). Intended to be a helper method, for internal use
        end_time = end_time if end_time else time.time() + timeout
        self._refresh(end_time=end_time, expected=expected, force=force, timeout=timeout)
        result = False
        start_time = time.time()
        while True:
            try:
                result = call()
            except StaleElementReferenceException:
                print("STALE ELEMENT EXCEPTION===========================================================")
                if time.time() > end_time:
                    break
                self._refresh(force=True)
                result = False
                continue
            # if expected is None, we're not awaiting a specific response
            if expected is None:
                break
            else:
                if result == expected:
                    break
            if time.time() > end_time:
                break
        if expected is not None:
            result = result == expected
        return result, time.time() - start_time
