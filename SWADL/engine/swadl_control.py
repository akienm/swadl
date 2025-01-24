"""
File: swadl_control.py
Purpose: the control proxy object
"""
import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from SWADL.engine.swadl_base import SWADLBase
from SWADL.engine.swadl_cfg import cfgdict
from SWADL.engine.swadl_constants import CACHE
from SWADL.engine.swadl_constants import CLICK
from SWADL.engine.swadl_constants import ENABLED
from SWADL.engine.swadl_constants import EXIST
from SWADL.engine.swadl_constants import FAILURE_LOG
from SWADL.engine.swadl_constants import RESULT_LOG
from SWADL.engine.swadl_constants import SELECTOR
from SWADL.engine.swadl_constants import SELENIUM_CONTROL_DEFAULT_TIMEOUT
from SWADL.engine.swadl_constants import SELENIUM_PAGE_DEFAULT_TIMEOUT
from SWADL.engine.swadl_constants import TEST_OBJECT
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
from SWADL.engine.swadl_output import Output


class SWADLControl(SWADLBase):
    """
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
    Datum: key
    Purpose: if calling validate_input or similar, this means get the data from
             cfgdict[SUBSTITUTION_SOURCES]
    Notes: String or real
    """
    key = None

    """
    Datum: has_text
    Purpose: if the element "has this text" (in it)
    Notes: is_text wins over has_text
    """
    has_text = None

    """
    Datum: index
    Purpose: if specified means the nth item to match
    Notes: index is applied AFTER is_text or has_text
    """
    index = None

    """
    Datum: is_text
    Purpose: if the element text matches this text exactly
    Notes: is_text wins over has_text
    """
    is_text = None

    """
    Datum: name
    Purpose: this string is used to identify the control in reporting
    Notes: Provided at instantiation
    """
    name = None

    """
    Datum: selector
    Purpose: this is the string that will be used to identify the control
    Notes: Provided at instantiation
    """
    selector = None

    """
    Data: _cache
    Purpose: These are used by the result caching that happens as controls are
             analyzed and acted upon. See def clear_cached_status(self)
    """
    _cache = {}

    def __init__(self, **kwargs):
        """
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
              clicked on.
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
        super().__init__(**kwargs)
        self.require_in(member=SELECTOR, container=kwargs, fatal=True)
        self.validation = None
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
        return end_time, element_list

    def click(self, end_time=None, force=False,
              timeout=cfgdict[SELENIUM_PAGE_DEFAULT_TIMEOUT], **kwargs):
        """
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
        return self._retry_until_expected_met(
            call=self._do_click, expected=True, end_time=end_time, force=force,
        )

    def _do_click(self):
        """
        Purpose: Performs the actual click
        Returns: bool of whether successful
        Notes: Click will fail and this return False if the thing is obscured!
               (See click() for more information)
        """
        try:
            self._cache['filtered_elements'][0].click()
            self._cache['status'][CLICK] = True
        except (TypeError, IndexError):
            self._cache['status'][CLICK] = False
        return self._cache['status'][CLICK]

    # noinspection PyBroadException
    def get_elements(self,
                     end_time=None,
                     force=False,
                     timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT],
                     **kwargs
                     ):
        """
        Purpose: Fetches elements based on self.selector, self.index, self.is_text and
                 self.has_text (is_text will win if both are present)
        Args:
            - end_time (float time.time()+timeout) - Passed from other methods also doing
                       timeout operations. So we don't have to be constantly recalculating the
                       end time.
            - force (bool) - force update by clearing the cache
            - timeout (float, default=20) - How long until we give up looking for a match
            _ **kwargs - Are applied to the object as object properties before acting.
        """
        self.apply_kwargs(kwargs)
        end_time = end_time if end_time else time.time() + timeout
        processed_selector = self.resolve_substitutions(self.selector)

        while True:
            try:
                # The explicit reference here forces everything to be a CSS based selector.
                # TODO: Use prefixes instead, such as css= or xpath=. Add that logic here.

                # first we get the current list of matching raw elements
                new_raw_elements = self.driver.find_elements(By.CSS_SELECTOR, processed_selector)
                # now we check and see if anything has changed from last time
                refresh = (
                    (self._cache['raw_elements'] != new_raw_elements) or
                    (self._cache['is_text'] != self.is_text) or
                    (self._cache['has_text'] != self.has_text) or
                    (self._cache['index'] != self.index) or
                    (force == True)
                )
                if refresh:
                    self.clear_cached_status()
                    self._cache['selector'] = self.selector
                    self._cache['processed_selector'] = processed_selector
                    self._cache['is_text'] = self.is_text
                    self._cache['has_text'] = self.has_text
                    self._cache['index'] = self.index
                    self._cache['raw_elements'] = new_raw_elements
                    if self.is_text:
                        for element in self._cache['raw_elements']:
                            text = element.text
                            if text not in self._cache['unique_text_values']:
                                self._cache['unique_text_values'].append(text)
                            if self.is_text == text:
                                self._cache['filtered_elements'].append(element)
                                break
                    elif self.has_text:
                        for element in self._cache['raw_elements']:
                            text = element.text
                            if text not in self._cache['unique_text_values']:
                                self._cache['unique_text_values'].append(text)
                            if self.is_text in text:
                                self._cache['filtered_elements'].append(element)
                                break
                    else:
                        self._cache['filtered_elements'] = self._cache['raw_elements']

                    if self.index is not None:
                        assert self.index < 0 or len(self._cache['filtered_elements']) > self.index, (
                            f"Index of {self.index} into the list of matching controls is "
                            f"invalid, the number of elements was {self._cache['filtered_elements']}."
                        )
                        self._cache['filtered_elements'] = [self._cache['filtered_elements'][self.index]]

                if self._cache['filtered_elements']:
                    break
            except Exception:
                # we do not care what errors occur, just keep going and retry
                pass
            if time.time() > end_time:
                # we do care whether we've gone past our end time. But performing this test
                # here, rather than at the top, means we go thru the loop at least once.
                break
        return self._cache['filtered_elements']

    def clear_cached_status(self):
        # Purpose: Reset the cache data to blank. Will cause next option to re-fetch
        self._cache = {
            'status': {},
            'raw_elements': [],
            'filtered_elements': [],
            'unique_text_values': [],
            'selector': None,
            'processed_selector': None,
            'is_text': None,
            'has_text': None,
            'index':None,
        }

    def get_status(self, force=True, timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        self.get_elements(force=force, timeout=timeout, **kwargs)
        self._cache['status'][EXIST] = False
        self._cache['status'][UNIQUE] = False
        self._cache['status'][VISIBLE] = None
        self._cache['status'][ENABLED] = None
        self._cache['status'][VALUE] = None

        how_many = len(self._cache['filtered_elements'])
        self._cache['status'][EXIST] = how_many > 0

        if self._cache['status'][EXIST]:
            self._cache['status'][UNIQUE] = how_many == 1
        if self._cache['status'][UNIQUE]:
            element=self._cache['filtered_elements'][0]
            self._cache['status'][VISIBLE]=element.is_displayed()
            self._cache['status'][ENABLED]=element.is_enabled()
            self._cache['status'][VALUE]=element.text

    def submit(self, end_time=None, fatal=False, force=False,
               timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Purpose: Sends submit to the control
        end_time, element_list = self._check_actionable(
            end_time=end_time,
            force=force,
            kwargs=kwargs,
            timeout=timeout
        )
        if len(element_list) > 0:
            element_list[0].submit(**self._remove_keys_webdriver_doesnt_like(kwargs))
        else:
            self.require_true(
                exper=element_list,
                fatal=fatal,
                message="Failed be able to submit"
            )

    def get_exist(self, end_time=None, expected=True, force=True,
                  timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Purpose: Returns true if control exists
        end_time = end_time if end_time else time.time() + timeout
        self._refresh(force=force)
        self.apply_kwargs(kwargs)
        return self._get_exist(end_time=end_time, expected=expected, timeout=timeout, **kwargs)[0]

    def get_enabled(self, end_time=None, expected=True,
                    timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Purpose: Returns true if control enabled
        end_time, element_list = self._check_actionable(
            end_time=end_time,
            kwargs=kwargs,
            timeout=timeout
        )
        return self._get_enabled(end_time=end_time, expected=expected, timeout=timeout, **kwargs)[0]

    def get_value(self, end_time=None, expected=None,
                  timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Purpose: Returns value (text) of the control
        end_time, element_list = self._check_actionable(
            end_time=end_time,
            kwargs=kwargs,
            timeout=timeout
        )
        return self._get_value(end_time=end_time, expected=expected, timeout=timeout, **kwargs)[0]

    def get_visible(self, end_time=None, expected=True,
                    timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Purpose: Returns true if control visible
        end_time, element_list = self._check_actionable(
            end_time=end_time,
            kwargs=kwargs,
            timeout=timeout
        )
        return self._get_visible(end_time=end_time, expected=expected, timeout=timeout, **kwargs)[0]

    def get_unique(self, end_time=None, expected=True,
                   timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Purpose: Returns true if control is unique
        end_time, element_list = self._check_actionable(
            end_time=end_time,
            kwargs=kwargs,
            timeout=timeout
        )
        return self._get_unique(end_time=end_time, expected=expected, timeout=timeout, **kwargs)[0]

    def set_value(self, end_time=None, fatal=True, force=False, value=None,
                  timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        """
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
            force=force,
            kwargs=kwargs,
            timeout=timeout
        )
        found_elements = len(element_list) > 0
        if found_elements:
            element_list[0].send_keys(value, **self._remove_keys_webdriver_doesnt_like(kwargs))
        else:
            self.require_true(
                exper=element_list,
                fatal=fatal,
                message="Failed to set value"
            )
        return found_elements  # because we were successful if we didn't throw an error

    def _get_exist(self, end_time=None, expected=None, force=True,
                   timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Purpose: Returns the result of testing the existence of the control
        return self._retry_until_expected_met(
            call=self._query_exist, end_time=end_time, expected=expected, force=force,
            timeout=timeout,
        )

    def _get_enabled(self, end_time=None, expected=None, force=False,
                     timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Purpose: Returns the result of testing the enabled status of the control
        return self._retry_until_expected_met(
            call=self._query_enabled, end_time=end_time, expected=expected, force=force,
            timeout=timeout
        )

    def _get_value(self, end_time=None, expected=None, force=False,
                   timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Purpose: Returns the result of testing the VALIDATE_TEXT of the control
        result, elapsed = self._retry_until_expected_met(
            call=self._query_value, end_time=end_time, expected=expected, force=force,
            timeout=timeout,
        )
        if expected is None and result:
            result =  self._cache['status'][VALUE]
        return result, elapsed

    def _get_visible(self, end_time=None, expected=None, force=False,
                     timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Purpose: Returns the result of testing the visibility of the control
        return self._retry_until_expected_met(
            call=self._query_visible, end_time=end_time, expected=expected, force=force,
            timeout=timeout
        )

    def _get_unique(self, end_time=None, expected=None, force=False,
                    timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Purpose: Returns the result of testing the unique status of the control
        return self._retry_until_expected_met(
            call=self._query_unique, end_time=end_time, expected=expected, force=force,
            timeout=timeout
        )

    def _query_enabled(self):
        # Purpose: Helper that performs the actual comparison to get the enabled state.
        #          Intended to be a helper method, for internal use
        try:
            self._cache['status'][ENABLED] = self._cache['filtered_elements'][0].is_enabled()
        except TypeError:
            self._cache['status'][ENABLED] = False
        return  self._cache['status'][ENABLED]

    def _query_exist(self):
        # Purpose: Helper that performs the actual comparison to get the exist state.
        #          Intended to be a helper method, for internal use
        self._cache['status'][EXIST] = bool(self._cache['filtered_elements'])
        return  self._cache['status'][EXIST]

    def _query_unique(self):
        # Purpose: Helper that performs the actual comparison to get the unique state.
        #          Intended to be a helper method, for internal use
        self._cache['status'][UNIQUE] = len(self._cache['filtered_elements']) == 1
        return  self._cache['status'][UNIQUE]

    def _query_value(self):
        # Purpose: Helper that performs the actual comparison to get the value.
        #          Intended to be a helper method, for internal use
        try:
            self._cache['status'][VALUE] = self._cache['filtered_elements'][0].text
        except (TypeError, IndexError):
            self._cache['status'][VALUE] = None
        return  self._cache['status'][VALUE]

    def _query_visible(self):
        # Purpose: Helper that performs the actual comparison to get the visible state.
        #          Intended to be a helper method, for internal use
        try:
            self._cache['status'][VISIBLE] = self._cache['filtered_elements'][0].is_displayed()
        except (TypeError, IndexError):
            self._cache['status'][VISIBLE] = False
        return  self._cache['status'][VISIBLE]

    def _refresh(self, end_time=None, expected=None, force=False, timeout=0):
        # Purpose: Reloads the element list. Intended to be a helper method, for internal use
        if force or not self.__dict__.get(CACHE):
            self.clear_cached_status()
            if expected is False:
                timeout = 0
            self.get_elements(end_time=end_time, timeout=timeout)

    # if _retry gets an exception, we'll put it here. it can be checked after the last one
    _exception_from_refresh = None

    def _retry_until_expected_met(self, call, end_time=None, expected=None, force=False,
                                  timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Purpose: Wraps the webdriver call in a time-based retry mechanism (retry until match or
        #          the timeout expires). Intended to be a helper method, for internal use
        # WARNING: IF AN EXPECTED VALUE IS SPECIFIED AND NOT MET, THIS METHOD WILL RETURN FALSE!
        end_time = end_time if end_time else time.time() + timeout
        self._refresh(end_time=end_time, expected=expected, force=force, timeout=timeout)
        result = False
        start_time = time.time()
        while True:
            try:
                self._exception_from_refresh = None
                result = call()
            except StaleElementReferenceException:
                print("STALE ELEMENT EXCEPTION===========================================================")
                # if we got a stale element exception, check that we're not over time...
                if time.time() > end_time:
                    break
                # and if we're not, force a refresh
                self._refresh(force=True)
                result = False
                continue
            except Exception as e:
                self._exception_from_refresh = e
            # if expected is None, we're not awaiting a specific response
            if expected is None:
                break
            else:
                # if we got the value we expected, then we're done!
                if result == expected:
                    break
            # if we've exceeded our time, then we're done!
            if time.time() > end_time:
                break
        if expected is not None:
            result = result == expected
        return result, time.time() - start_time

    def validate(self, end_time=None, fatal=False, timeout=cfgdict[SELENIUM_PAGE_DEFAULT_TIMEOUT],
                 validation=None, **kwargs):
        # Purpose: Given a validation dict, or a self.validation dict (if none is passed)
        #          Then validate that each thing is of the correct value
        # Returns: (bool) was the validation successful
        validation = validation or self.validation
        assert validation, "SWADLControl.validate() was called with no validations specified."
        end_time = end_time if end_time else time.time() + timeout
        result = True
        for item in validation:
            time_remaining = end_time - time.time()
            time_remaining = time_remaining if time_remaining > 0 else 1
            validation_call = self.mater_validation_table[item]
            result = validation_call(fatal=fatal, timeout=time_remaining, **kwargs) and result
        return result

    def _validate(self, comments='', elapsed_time='', expected=None, fatal=False, force=None, report=True,
                  result=None, validation_name=None):
        # Purpose: reports on the pass/fail status of a validation call

        if force:
            self.clear_cached_status()
        if report:
            # this next if is to check and see if we're running not under a test
            if FAILURE_LOG not in cfgdict:
                cfgdict[FAILURE_LOG] = Output('automation_failures.log')
                cfgdict[RESULT_LOG] = Output('automation_results.log')
            if isinstance(elapsed_time, str):
                elapsed_time = 'not specified'
            else:
                # linters hate this.
                elapsed_time = (
                    '< 0.0001 seconds' if elapsed_time < 0.0001 else
                    f'{round(elapsed_time, 4)} seconds'
                )
            report_me = None
            if not result:
                if self.save_screen_shots:
                    file_name = f'FAILURE_{self.get_timestamp()}.png'
                    self.driver.save_screenshot(file_name)
                    report_me = f'    saved image: {file_name},\n'
            message_dict = SWADLDict()
            message_dict['result'] = "PASSED" if result else "FAILED"
            message_dict['for control'] = self.get_name()
            message_dict['with selector'] = self.selector
            message_dict['is_text'] = self.is_text
            message_dict['has_text'] = self.has_text
            message_dict['index'] = self.index
            self.get_status(timeout=0)
            filtered_element_count = len(self._cache['filtered_elements'])
            message_dict['# filtered elements'] = filtered_element_count
            message_dict['control status cache'] = self._cache['status']
            message_dict['# raw elements'] = len(self._cache['raw_elements'])
            message_dict['unique text found'] = self._cache['unique_text_values']
            message_dict['validation_name'] = validation_name
            message_dict['expected'] = expected
            message_dict['elapsed_time'] = elapsed_time
            message_dict['fatal'] = fatal
            if report_me:
                message_dict['report_me'] = report_me
            message_dict['comments'] = comments
            message = self.bannerize(data=message_dict, title="SWADL Validation Result")
            cfgdict[RESULT_LOG].add(message)
            entry_name = (
                f'SWADL:Validation:{self.get_name()}'
                f'.{validation_name} '
                f'at {self.get_timestamp()}'
            )
            self.test_data[entry_name] = message_dict
            if result:
                self.log.debug(message)
            else:
                self.log.critical(message)
                cfgdict[FAILURE_LOG].add(message)
                cfgdict[TEST_OBJECT].accumulated_failures.append(message)
            # print(message)
            was_not_fatal = not (result is False and fatal is True)
            assert was_not_fatal, f"A fatal error occurred. {message}"

        return result

    def validate_click(self, end_time=None, expected=True, fatal=False, force=True,
                       timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        """
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
        Purpose: Perform the input as part of the engine based processing of controls
        """
        start_time = time.time()
        result = self.set_value(end_time=end_time, timeout=timeout)
        elapsed_time = time.time() - start_time
        return self._validate(
            elapsed_time=elapsed_time,
            expected=expected,
            fatal=fatal,
            force=force,
            result=result,
            validation_name="Input",
            **kwargs,
        )

    def validate_text(self=None, end_time=None, expected=None, fatal=False, force=False,
                      timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Purpose: verify whether a control's value matches it's VALIDATE_TEXT value
        expected_to_test = expected if expected else getattr(self, VALIDATE_TEXT, None)
        result, elapsed_time = self._get_value(
            end_time=end_time, expected=expected_to_test, force=force, timeout=timeout
        )
        comments = f'expected: "{expected_to_test}", actual: "{self._cache["status"][VALUE]}"'
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

    def mouseover(self, timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # TODO: FINISH BUILDING THIS OUT!
        # JUST HOW DO WE KNOW IF WE WORKED?
        # RETRY?
        self.actions.move_to_element(self.get_elements(timeout=timeout)[0]).perform()
