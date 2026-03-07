"""
File: swadl_control.py
Purpose: The control proxy object. Wraps a UI element selector with retry logic,
         caching, and engine-based validation.

Timeout model:
  - `timeout` (seconds float): how long to keep retrying from now.
  - `end_time` (time.time() float): absolute deadline, takes precedence over timeout.
  A series of operations should compute end_time once and pass it along so the
  total budget is shared. Each call is attempted at least once regardless.
"""
import time

from SWADL.engine.swadl_base import SWADLBase
from SWADL.engine.swadl_cfg import cfgdict
from SWADL.engine.swadl_constants import (
    ACTIONABLE, CACHE, CLICK, ENABLED, EXIST, FAILURE_LOG, FILTERED_ELEMENTS,
    HAS_TEXT, INDEX, IS_TEXT, PROCESSED_SELECTOR, RAW_ELEMENTS, RESULT_LOG,
    SELECTOR, SELENIUM_CONTROL_DEFAULT_TIMEOUT, SELENIUM_PAGE_DEFAULT_TIMEOUT,
    STATUS, TEST_OBJECT, TIMEOUT, UNIQUE, UNIQUE_TEXT_VALUES, VALIDATE_CLICK,
    VALIDATE_ENABLED, VALIDATE_EXIST, VALIDATE_INPUT, VALIDATE_TEXT,
    VALIDATE_UNIQUE, VALIDATE_VISIBLE, VALUE, VISIBLE,
)
from SWADL.engine.swadl_dict import SWADLDict
from SWADL.engine.swadl_exceptions import SWADLStaleElementError
from SWADL.engine.swadl_output import Output


class SWADLControl(SWADLBase):
    """
    Proxy for a single UI control. Instantiate with a CSS selector (or
    interface-appropriate selector) and a name used in reports.

    Common keyword args accepted everywhere:
      selector  - the selector string (required at init)
      name      - label used in all reports (required at init)
      has_text  - only match elements whose text contains this string
      is_text   - only match elements whose text exactly equals this string
      index     - after text filtering, take the nth match (0-based)
      timeout   - seconds to keep retrying (default varies by operation)
      end_time  - absolute deadline; overrides timeout when provided
      fatal     - if True, a validation failure raises immediately
    """

    key = None       # key into cfgdict[SUBSTITUTION_SOURCES] for validate_input
    has_text = None  # filter: element text contains this
    index = None     # filter: take the nth match after text filtering
    is_text = None   # filter: element text exactly equals this (wins over has_text)
    name = None
    selector = None

    _cache = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.require_in(member=SELECTOR, container=kwargs, fatal=True)
        self.validation = None
        self.clear_cached_status()
        self.mater_validation_table = {
            VALIDATE_ENABLED: self.validate_enabled,
            VALIDATE_EXIST:   self.validate_exist,
            VALIDATE_TEXT:    self.validate_text,
            VALIDATE_UNIQUE:  self.validate_unique,
            VALIDATE_VISIBLE: self.validate_visible,
            # input and click are last: input fills a field, click may navigate away
            VALIDATE_INPUT:   self.validate_input,
            VALIDATE_CLICK:   self.validate_click,
        }

    # ── Cache ─────────────────────────────────────────────────────────────────

    def clear_cached_status(self):
        # Reset all cached state. Forces a re-fetch on next operation.
        self._cache = {
            STATUS:            {},
            RAW_ELEMENTS:      [],
            FILTERED_ELEMENTS: [],
            UNIQUE_TEXT_VALUES:[],
            SELECTOR:          None,
            PROCESSED_SELECTOR:None,
            IS_TEXT:           None,
            HAS_TEXT:          None,
            INDEX:             None,
        }

    # ── Element fetching ──────────────────────────────────────────────────────

    def get_elements(self, end_time=None, force=False,
                     timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        """
        Returns the list of elements matching selector + text/index filters.
        Retries until at least one match is found or end_time is reached.
        """
        self.apply_kwargs(kwargs)
        end_time = end_time if end_time else time.time() + timeout
        processed_selector = self.resolve_substitutions(self.selector)

        while True:
            try:
                new_raw_elements = self.driver.find_elements(processed_selector)
                refresh = (
                    self._cache[RAW_ELEMENTS] != new_raw_elements or
                    self._cache[IS_TEXT] != self.is_text or
                    self._cache[HAS_TEXT] != self.has_text or
                    self._cache[INDEX] != self.index or
                    force is True
                )
                if refresh:
                    self.clear_cached_status()
                    self._cache[SELECTOR] = self.selector
                    self._cache[PROCESSED_SELECTOR] = processed_selector
                    self._cache[IS_TEXT] = self.is_text
                    self._cache[HAS_TEXT] = self.has_text
                    self._cache[INDEX] = self.index
                    self._cache[RAW_ELEMENTS] = new_raw_elements

                    if self.is_text:
                        for element in self._cache[RAW_ELEMENTS]:
                            text = element.text
                            if text not in self._cache[UNIQUE_TEXT_VALUES]:
                                self._cache[UNIQUE_TEXT_VALUES].append(text)
                            if self.is_text == text:
                                self._cache[FILTERED_ELEMENTS].append(element)
                                break
                    elif self.has_text:
                        for element in self._cache[RAW_ELEMENTS]:
                            text = element.text
                            if text not in self._cache[UNIQUE_TEXT_VALUES]:
                                self._cache[UNIQUE_TEXT_VALUES].append(text)
                            if self.has_text in text:
                                self._cache[FILTERED_ELEMENTS].append(element)
                                break
                    else:
                        self._cache[FILTERED_ELEMENTS] = self._cache[RAW_ELEMENTS]

                    if self.index is not None:
                        assert self.index < 0 or len(self._cache[FILTERED_ELEMENTS]) > self.index, (
                            f"Index {self.index} is out of range; "
                            f"found {len(self._cache[FILTERED_ELEMENTS])} elements."
                        )
                        self._cache[FILTERED_ELEMENTS] = [self._cache[FILTERED_ELEMENTS][self.index]]

                if self._cache[FILTERED_ELEMENTS]:
                    break
            except Exception:
                pass
            if time.time() > end_time:
                break

        return self._cache[FILTERED_ELEMENTS]

    def get_status(self, force=True, timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Populate the full STATUS cache entry for the current element state.
        self.get_elements(force=force, timeout=timeout, **kwargs)
        self._cache[STATUS] = {
            EXIST:      False,
            UNIQUE:     False,
            VISIBLE:    None,
            ENABLED:    None,
            VALUE:      None,
            ACTIONABLE: None,
        }
        how_many = len(self._cache[FILTERED_ELEMENTS])
        self._cache[STATUS][EXIST] = how_many > 0
        if self._cache[STATUS][EXIST]:
            self._cache[STATUS][UNIQUE] = how_many == 1
        if self._cache[STATUS][UNIQUE]:
            element = self._cache[FILTERED_ELEMENTS][0]
            self._cache[STATUS][VISIBLE] = element.is_displayed()
            self._cache[STATUS][ENABLED] = element.is_enabled()
            self._cache[STATUS][VALUE] = element.text
            self._cache[STATUS][ACTIONABLE] = (
                self._cache[STATUS][VISIBLE] and self._cache[STATUS][ENABLED]
            )

    # ── Core retry machinery ──────────────────────────────────────────────────

    _exception_from_refresh = None

    def _refresh(self, end_time=None, expected=None, force=False, timeout=0):
        # Reload element list. Uses timeout=0 when expected=False (don't wait for absent things).
        if force or not self.__dict__.get(CACHE):
            self.clear_cached_status()
            if expected is False:
                timeout = 0
            self.get_elements(end_time=end_time, timeout=timeout)

    def _retry_until_expected_met(self, call, end_time=None, expected=None, force=False,
                                  timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Calls `call()` in a loop until the result matches `expected` or end_time passes.
        # If expected is None, runs once and returns whatever `call()` returns.
        # Returns (result, elapsed_seconds).
        end_time = end_time if end_time else time.time() + timeout
        self._refresh(end_time=end_time, expected=expected, force=force, timeout=timeout)
        result = False
        start_time = time.time()
        while True:
            try:
                self._exception_from_refresh = None
                result = call()
            except SWADLStaleElementError:
                if time.time() > end_time:
                    break
                self._refresh(force=True)
                result = False
                continue
            except Exception as e:
                self._exception_from_refresh = e
            if expected is None:
                break
            if result == expected:
                break
            if time.time() > end_time:
                break
        if expected is not None:
            result = result == expected
        return result, time.time() - start_time

    # ── Property queries (collapsed from _get_* + _query_* layers) ───────────

    def _query_property(self, prop):
        # Reads one property from the current filtered elements, updates STATUS cache.
        handlers = {
            EXIST:    lambda: bool(self._cache[FILTERED_ELEMENTS]),
            UNIQUE:   lambda: len(self._cache[FILTERED_ELEMENTS]) == 1,
            ENABLED:  lambda: self._cache[FILTERED_ELEMENTS][0].is_enabled(),
            VISIBLE:  lambda: self._cache[FILTERED_ELEMENTS][0].is_displayed(),
            VALUE:    lambda: self._cache[FILTERED_ELEMENTS][0].text,
        }
        try:
            result = handlers[prop]()
        except (TypeError, IndexError):
            result = False
        self._cache[STATUS][prop] = result
        return result

    def _fetch_property(self, prop, end_time=None, expected=None, force=False,
                        timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Retry _query_property(prop) until expected is met or timeout.
        return self._retry_until_expected_met(
            call=lambda: self._query_property(prop),
            end_time=end_time,
            expected=expected,
            force=force,
            timeout=timeout,
        )

    # ── Actionability check ───────────────────────────────────────────────────

    def _check_actionable(self, end_time=None, force=False, kwargs=None,
                          timeout=cfgdict[SELENIUM_PAGE_DEFAULT_TIMEOUT]):
        """
        Applies kwargs, computes end_time, and asserts the control is uniquely
        present, enabled, and visible. Returns (end_time, element_list).
        Centralises the boilerplate that every action method needs.
        """
        if kwargs:
            self.apply_kwargs(kwargs)
        end_time = end_time if end_time else time.time() + timeout
        if force:
            self.clear_cached_status()
        element_list = self.get_elements(end_time=end_time)

        assert len(element_list) > 0, f"Can't find an element that matches {self.selector}"
        assert len(element_list) == 1, (
            f"{self.get_name()} can't operate on multiple elements, "
            f"found {len(element_list)} matches for {self.selector}"
        )
        assert element_list[0].is_enabled(), f"Element is not enabled: {self.selector}"
        assert element_list[0].is_displayed(), f"Element is not visible: {self.selector}"
        return end_time, element_list

    # ── Public get_* methods ──────────────────────────────────────────────────

    def get_exist(self, end_time=None, expected=True, force=True,
                  timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Returns True if the control exists.
        end_time = end_time if end_time else time.time() + timeout
        self._refresh(force=force)
        self.apply_kwargs(kwargs)
        return self._fetch_property(EXIST, end_time=end_time, expected=expected,
                                    force=force, timeout=timeout)[0]

    def get_enabled(self, end_time=None, expected=True,
                    timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Returns True if the control is enabled.
        end_time, _ = self._check_actionable(end_time=end_time, kwargs=kwargs, timeout=timeout)
        return self._fetch_property(ENABLED, end_time=end_time, expected=expected,
                                    timeout=timeout)[0]

    def get_value(self, end_time=None, expected=None,
                  timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Returns the text value of the control (or True/False if expected is specified).
        end_time, _ = self._check_actionable(end_time=end_time, kwargs=kwargs, timeout=timeout)
        result, _ = self._fetch_property(VALUE, end_time=end_time, expected=expected,
                                         timeout=timeout)
        if expected is None and result:
            result = self._cache[STATUS][VALUE]
        return result

    def get_visible(self, end_time=None, expected=True,
                    timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Returns True if the control is visible.
        end_time, _ = self._check_actionable(end_time=end_time, kwargs=kwargs, timeout=timeout)
        return self._fetch_property(VISIBLE, end_time=end_time, expected=expected,
                                    timeout=timeout)[0]

    def get_unique(self, end_time=None, expected=True,
                   timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Returns True if the selector matches exactly one element.
        end_time, _ = self._check_actionable(end_time=end_time, kwargs=kwargs, timeout=timeout)
        return self._fetch_property(UNIQUE, end_time=end_time, expected=expected,
                                    timeout=timeout)[0]

    # ── Actions ───────────────────────────────────────────────────────────────

    def click(self, end_time=None, force=False,
              timeout=cfgdict[SELENIUM_PAGE_DEFAULT_TIMEOUT], **kwargs):
        # Click the control. Retries on stale element. Returns (result, elapsed).
        end_time, _ = self._check_actionable(
            end_time=end_time, force=force, kwargs=kwargs, timeout=timeout)
        return self._retry_until_expected_met(
            call=self._do_click, expected=True, end_time=end_time, force=force)

    def _do_click(self):
        try:
            self._cache[FILTERED_ELEMENTS][0].click()
            self._cache[STATUS][CLICK] = True
        except (TypeError, IndexError):
            self._cache[STATUS][CLICK] = False
        return self._cache[STATUS][CLICK]

    def set_value(self, end_time=None, fatal=True, force=False, value=None,
                  timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        """
        Send text input to the control.
        Returns True if successful.
        """
        end_time, element_list = self._check_actionable(
            end_time=end_time, force=force, kwargs=kwargs, timeout=timeout)
        if element_list:
            element_list[0].send_keys(value)
            return True
        self.require_true(exper=False, fatal=fatal, message="Failed to set value")
        return False

    def submit(self, end_time=None, fatal=False, force=False,
               timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        # Send submit to the control.
        end_time, element_list = self._check_actionable(
            end_time=end_time, force=force, kwargs=kwargs, timeout=timeout)
        if element_list:
            element_list[0].submit()
        else:
            self.require_true(exper=False, fatal=fatal, message="Failed to submit")

    def mouseover(self, timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT]):
        # Move the mouse over the control.
        self.actions.move_to_element(
            self.get_elements(timeout=timeout)[0]
        ).perform()

    # ── Validation reporting ──────────────────────────────────────────────────

    def _validate(self, comments='', elapsed_time='', expected=None, fatal=False,
                  force=None, report=True, result=None, validation_name=None):
        # Records and logs the pass/fail result of a validation call.
        if force:
            self.clear_cached_status()
        if not report:
            return result

        if FAILURE_LOG not in cfgdict:
            cfgdict[FAILURE_LOG] = Output('automation_failures.log')
            cfgdict[RESULT_LOG] = Output('automation_results.log')

        if isinstance(elapsed_time, str):
            elapsed_time = 'not specified'
        else:
            elapsed_time = (
                '< 0.0001 seconds' if elapsed_time < 0.0001
                else f'{round(elapsed_time, 4)} seconds'
            )

        report_me = None
        if not result and self.save_screen_shots:
            file_name = f'FAILURE_{self.get_timestamp()}.png'
            self.driver.save_screenshot(file_name)
            report_me = f'    saved image: {file_name},\n'

        self.get_status(timeout=0)
        message_dict = SWADLDict()
        message_dict['result'] = "PASSED" if result else "FAILED"
        message_dict['for control'] = self.get_name()
        message_dict['with selector'] = self.selector
        message_dict[IS_TEXT] = self.is_text
        message_dict[HAS_TEXT] = self.has_text
        message_dict[INDEX] = self.index
        message_dict['# filtered elements'] = len(self._cache[FILTERED_ELEMENTS])
        message_dict['control status cache'] = self._cache[STATUS]
        message_dict['# raw elements'] = len(self._cache[RAW_ELEMENTS])
        message_dict['unique text found'] = self._cache[UNIQUE_TEXT_VALUES]
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

        assert not (result is False and fatal is True), f"A fatal error occurred. {message}"
        return result

    # ── validate_* (engine-based validation entry points) ────────────────────

    def validate(self, end_time=None, fatal=False,
                 timeout=cfgdict[SELENIUM_PAGE_DEFAULT_TIMEOUT], validation=None, **kwargs):
        # Run all validations in the provided dict (or self.validation if none given).
        validation = validation or self.validation
        assert validation, "SWADLControl.validate() called with no validations specified."
        end_time = end_time if end_time else time.time() + timeout
        result = True
        for item in validation:
            time_remaining = max(end_time - time.time(), 1)
            result = self.mater_validation_table[item](
                fatal=fatal, timeout=time_remaining, **kwargs) and result
        return result

    def validate_click(self, end_time=None, expected=True, fatal=False, force=True,
                       timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        result, elapsed_time = self.click(force=force, end_time=end_time, timeout=timeout)
        return self._validate(elapsed_time=elapsed_time, expected=expected, fatal=fatal,
                              result=result, validation_name="Click", **kwargs)

    def validate_exist(self, end_time=None, expected=True, fatal=False, force=True,
                       timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        result, elapsed_time = self._fetch_property(
            EXIST, end_time=end_time, expected=expected, force=force, timeout=timeout)
        return self._validate(elapsed_time=elapsed_time, expected=expected, fatal=fatal,
                              result=result, validation_name=EXIST, **kwargs)

    def validate_enabled(self, end_time=None, expected=True, fatal=False, force=False,
                         timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        result, elapsed_time = self._fetch_property(
            ENABLED, end_time=end_time, expected=expected, force=force, timeout=timeout)
        return self._validate(elapsed_time=elapsed_time, expected=expected, fatal=fatal,
                              result=result, validation_name=ENABLED, **kwargs)

    def validate_input(self, end_time=None, expected=True, fatal=False, force=False,
                       timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        start_time = time.time()
        result = self.set_value(end_time=end_time, timeout=timeout)
        elapsed_time = time.time() - start_time
        return self._validate(elapsed_time=elapsed_time, expected=expected, fatal=fatal,
                              force=force, result=result, validation_name="Input", **kwargs)

    def validate_text(self, end_time=None, expected=None, fatal=False, force=False,
                      timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        expected_to_test = expected if expected else getattr(self, VALIDATE_TEXT, None)
        result, elapsed_time = self._fetch_property(
            VALUE, end_time=end_time, expected=expected_to_test, force=force, timeout=timeout)
        comments = (
            f'expected: "{expected_to_test}", '
            f'actual: "{self._cache[STATUS].get(VALUE)}"'
        )
        return self._validate(comments=comments, elapsed_time=elapsed_time, expected=expected,
                              fatal=fatal, result=result, validation_name=VALIDATE_TEXT, **kwargs)

    def validate_visible(self, end_time=None, expected=True, fatal=False, force=False,
                         timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        result, elapsed_time = self._fetch_property(
            VISIBLE, end_time=end_time, expected=expected, force=force, timeout=timeout)
        return self._validate(elapsed_time=elapsed_time, expected=expected, fatal=fatal,
                              result=result, validation_name=VISIBLE, **kwargs)

    def validate_unique(self, end_time=None, expected=True, fatal=False, force=False,
                        timeout=cfgdict[SELENIUM_CONTROL_DEFAULT_TIMEOUT], **kwargs):
        result, elapsed_time = self._fetch_property(
            UNIQUE, end_time=end_time, expected=expected, force=force, timeout=timeout)
        return self._validate(elapsed_time=elapsed_time, expected=expected, fatal=fatal,
                              result=result, validation_name=UNIQUE, **kwargs)
