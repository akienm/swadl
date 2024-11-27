import inspect
import logging
import traceback
from datetime import time

from SWADL.engine.swadl_base import SWADLBase
from SWADL.engine.swadl_constants import ASSERT
from SWADL.engine.swadl_constants import CALLER
from SWADL.engine.swadl_constants import CONTAINER
from SWADL.engine.swadl_constants import DIVIDER
from SWADL.engine.swadl_constants import EXPECT
from SWADL.engine.swadl_constants import EXPER
from SWADL.engine.swadl_constants import EXPER1
from SWADL.engine.swadl_constants import EXPER2
from SWADL.engine.swadl_constants import FAILED
from SWADL.engine.swadl_constants import FATAL
from SWADL.engine.swadl_constants import HELPER
from SWADL.engine.swadl_constants import ID
from SWADL.engine.swadl_constants import KWARGS
from SWADL.engine.swadl_constants import LOGICAL_RESULT
from SWADL.engine.swadl_constants import MEMBER
from SWADL.engine.swadl_constants import MESSAGE
from SWADL.engine.swadl_constants import OBJ
from SWADL.engine.swadl_constants import PASSED
from SWADL.engine.swadl_constants import REPORTING_DICT
from SWADL.engine.swadl_constants import REQUIRE
from SWADL.engine.swadl_constants import RESULT
from SWADL.engine.swadl_constants import SELF__DICT__
from SWADL.engine.swadl_constants import STACKTRACE
from SWADL.engine.swadl_constants import TEST_OBJECT
from SWADL.engine.swadl_constants import TIME_FINISHED
from SWADL.engine.swadl_constants import TIME_STARTED
from SWADL.engine.swadl_constants import TRACEBACK_SPACES
from SWADL.engine.swadl_constants import X
from SWADL.engine.swadl_constants import Y
from SWADL.engine.swadl_dict import SWADLDict
from SWADL.engine.swadl_exceptions import SWADLTestError


class SWADLValidator(SWADLBase):
    """
    Who am i? SWADLValidator

    Why? A starting place for all validators (assertions, errors, etc)
         Will interface to logging, and perhaps even add logging levels for
         test errors vs test failures (assertions) vs test warnings vs
         test info, test debug, framework errors, framework info, framework debug
         in addition to all the usual python message classes.

    Why the why? Because  i wanna accomplish the following:
        * allow AutomationBlox BloxBuilders (mostly non programmers) to
          write automation
        * show BloxBuilders only information they can act upon, even if that
          action is simply to see a BloxMechanic (test automation developer)
          for more help.
        * this means hiding messages they can't act upon. so we create new
          logging levels for BloxBuilders and BloxMechanics to isolate
          that traffic from that of other python libraries.
        * A validator would be a validation for a single kind of test.
          like "value is true"
        * Different kinds of validators can have different:
          * Expected arguments
            * x, y, member, container, exper, exper1, exper2, obj,
            * section, control, timeout, color, fatal, rect, value
          * Expected argument names -- for reporting
          * Expected argument default values
          * Data acquisition methods
            - like a webdriver call to check exist
          * Logging levels
          * Logical test methods
          * Reporting strings
          * Different exceptions they can throw
        * a control with a table of validations will kinda look like this:
          self.fault_if_not_color:'ffffffff',
          self.fault_if_color:'ffffffff',
          self.fault_if_not_text:'this is a message',
          self.fault_if_not_exists: True,
          self.fault_if_not_visible: True,
        * If an "Assertion" is the thing the test case is there to validate,
          then "Fault" means "another failure found along the way"
          * self.assert_in(member)  # where self is the container
          * self.fault_if_not_in(member)  # where self is the container
          * self.error_if_not_in(member)  # where self is the container
          * self.warn_if_not_in(member)  # where self is the container
        * require_in and expect_in, don't make an ideal set of names for
          what they do. They've irritated me ever since i decided they were
          the least irritating solution i could come up with. error_if_in
          and warn_if_in make lots more sense, even if they "don't fit" with
          the assert_in in terms of logical specificity. By that i mean that
          assert_in asserts a positive and progresses if that's ok. otoh
          error_if_not_in does the same task, throws a different kind of error
          but must be specified as the negative case instead of the positive
          one. once upon a time i thought it simpler to try and follow the
          logic pattern of assert. But as I looked at adding more logging
          levels, it stopped making sense.
        * So the point of this class is to build a data driven way to
          produce validation methods that are tailored to the specific
          needs, and to produce an easy way to refactor existing ones,
          and to build new ones.
    """
    @classmethod
    def make_validation(
            cls,
            arguments=None,   # eg {'x':None, 'y':None},
            exception_class=None,
            expected=None,
            fatal=False,
            logging_channel=None,  # eg logging.DEBUG,
            name=None,  # causes self lookup
            test=None,  # this is the method like logical_test_equal()
            timeout=None,
        ):


    @staticmethod
    def _process_stack_trace(exc_info=None):
        # Purpose: Standardizes the traceback information
        # Parameters: exc_info (list of string) the traceback info to process
        # Returns: the normalized list
        # Usage: exc_info = process_stack_trace(exc_info)
        # sometimes we have a trailing blank line or two
        exc_info = exc_info if exc_info else traceback.format_stack()
        while exc_info[-1].strip() == '':
            del (exc_info[-1])
        return exc_info

    @staticmethod
    def _this_code_is_unreachable_so_there(exc_info):
        # now we're going to chop off all the nose2 traceback entries
        line_added = False
        recording = False
        result = [DIVIDER + 'test part:']
        for exc_item in exc_info:

            # break this up into lines
            interim_value = [exc_item.replace('\n', '')]

            # see if we should start reporting yet or not
            if ('Project\demos' in exc_item) and recording is False:
                # as soon as 'Project/demos' appears, we want to capture
                # all of the remaining entries
                recording = True

            # and if we've already started recording the lines
            if recording:
                # the 'spaces' appear before the file name, and before the
                # 'code' line.
                if TRACEBACK_SPACES in interim_value[0]:
                    interim_value = interim_value[0].split(TRACEBACK_SPACES)
                    interim_value[1] = TRACEBACK_SPACES + interim_value[1]

                # finally, go thru the "sub-lines" and add them to the result
                for item in interim_value:
                    # check for blank lines and give those a miss
                    if not line_added and 'SWADL\engine' in item:
                        line_added = True
                        result.append(DIVIDER + 'SWADL framework part:')
                    if len(item.strip()) > 0:
                        result.append(item)

        if result:
            result.append(DIVIDER + 'error part:')
        return result

    def _make_swadl_test_error(self, message=None, reporting_dict=None):
        # Purpose: Produces a FrameworkError with the passed data
        framework_error = SWADLTestError(
            self.bannerize(
                {
                    "SWADLTestError": {
                        MESSAGE: message,
                        REPORTING_DICT: reporting_dict,
                        SELF__DICT__: self.__dict__,
                    }
                }
            )
        )
        return framework_error

    def _assertion_post_processor(self,
                                  message=None,
                                  helper=None,
                                  **kwargs,
                                  ):
        # Purpose; Takes information provided by the caller about the
        # kind of assertion/error/warning, and completes the test,
        # recording and logging steps.

        # This should return the name of the calling method, such as
        # assert_true and so on.
        caller = inspect.stack()[2][0].f_code.co_name

        # This is the dictionary that will have all the final information on this
        # reporting action.
        reporting_dict = SWADLDict()
        reporting_dict[ID] = (
            f'SWADL:Validation:'
            f'{self.get_name()}'
            f'.{caller} '
            f'at {self.get_timestamp()} '
            f'with OID {id(reporting_dict)}'
        )
        self.test_data[reporting_dict[ID]] = reporting_dict

        # now assume each group will have a group processor
        # we want the method name that called that, not our
        # direct caller. Hence the [2] in the line below
        reporting_dict[CALLER] = caller
        reporting_dict[MESSAGE] = f"Validating {caller} which wants {message}"
        reporting_dict[KWARGS] = kwargs
        reporting_dict[HELPER] = helper

        reporting_dict[LOGICAL_RESULT] = False  # overwritten later we hope :)
        reporting_dict[RESULT] = "Failed to complete"  # overwritten later we hope :)
        reporting_dict[TIME_STARTED] = time.time()
        reporting_dict[TIME_FINISHED] = time.time()  # this is here just in case it doesn't finish

        # now we do the compare, protected from any kind of unexpected data types or whatever
        try:
            reporting_dict[LOGICAL_RESULT] = reporting_dict[HELPER](reporting_dict)
        except Exception as e:
            # this next line re-raises the same class with additional data
            self.test_data[TEST_OBJECT].accumulated_failures.append(reporting_dict)
            raise e.__class__(
                "INVALID RESULT WHEN PERFORMING LOGICAL COMPARE\n" +
                self.bannerize(title=e.__class__.__name__, data=e.__dict__) + "\n" +
                self.bannerize(self.cfgdict) + "\n"
            )

        # and if that didn't blow up, now we finish up.
        reporting_dict[TIME_FINISHED] = time.time()

        if reporting_dict[LOGICAL_RESULT]:
            reporting_dict[RESULT] = PASSED
        else:
            reporting_dict[RESULT] = FAILED
            reporting_dict[STACKTRACE] = self._process_stack_trace(traceback.format_stack())
            message = self.bannerize(reporting_dict)
            self.test_data[TEST_OBJECT].accumulated_failures.append(reporting_dict)
            caller = reporting_dict[CALLER].upper()
            if caller.startswith(ASSERT):
                self.log.critical(message)
                if reporting_dict[KWARGS].get(FATAL, False):
                    raise AssertionError(message)
            elif caller.upper().startswith(REQUIRE):
                self.log.error(message)
                if reporting_dict[KWARGS].get(FATAL, False):
                    raise Exception(message)
            elif caller.upper().startswith(EXPECT):
                self.log.warning(message)
                if reporting_dict[KWARGS].get(FATAL, False):
                    raise Exception("A WARNING WAS MARKED AS FATAL, THIS SHOULDN'T BE!\n" + message)
            else:
                message = "UNKNOWN ORIGIN POINT FOR VALIDATION, THIS SHOULDN'T BE!\n" + message
                self.log.error(message)
                raise Exception(message)

        return reporting_dict[LOGICAL_RESULT]


    ################################################################################

    @staticmethod
    def _logical_test_equal(reporting_dict=None):
        # Purpose: performs the actual comparison
        return reporting_dict[KWARGS][X] == reporting_dict[KWARGS][Y]

    def _test_equal_common(self, **kwargs):
        # Purpose: to get all the data passed to the post processor
        return self._assertion_post_processor(
            message=f'x={kwargs[X]} == y={kwargs[Y]}',
            helper=self._logical_test_equal,
            **kwargs,
        )

    def require_equal(self, x=None, y=None, **kwargs):
        # Description: records error if condition not met
        return self._test_equal_common(x=x, y=y, **kwargs)

    def expect_equal(self, x=None, y=None, **kwargs):
        # Description: records a warning if condition not met
        return self._test_equal_common(x=x, y=y, **kwargs)

    ################################################################################
    @staticmethod
    def _logical_test_not_equal(reporting_dict=None):
        # Purpose: performs the actual comparison
        return not (reporting_dict[KWARGS][X] == reporting_dict[KWARGS][Y])

    def _test_not_equal_common(self, **kwargs):
        # Purpose: to get all the data passed to the post processor
        return self._assertion_post_processor(
            message=f'x={kwargs[X]} != y={kwargs[Y]}',
            helper=self._logical_test_not_equal,
            **kwargs,
        )

    def require_not_equal(self, x=None, y=None, **kwargs):
        # Description: records error if condition not met
        return self._test_equal_common(x=x, y=y, **kwargs)

    def expect_not_equal(self, x=None, y=None, **kwargs):
        # Description: records a warning if condition not met
        return self._test_equal_common(x=x, y=y, **kwargs)

    ################################################################################
    @staticmethod
    def _logical_test_true(reporting_dict=None):
        # Purpose: performs the actual comparison
        return True if reporting_dict[KWARGS][EXPER] is True else False

    def _test_true_common(self, **kwargs):
        # Purpose: to get all the data passed to the post processor
        return self._assertion_post_processor(
            message=f'exper={kwargs[EXPER]} is True',
            helper=self._logical_test_true,
            **kwargs,
        )

    def require_true(self, exper=None, **kwargs):
        # Description: records error if condition not met
        return self._test_true_common(exper=exper, **kwargs)

    def expect_true(self, exper=None, **kwargs):
        # Description: records warning if condition not met
        return self._test_true_common(exper=exper, **kwargs)

    ################################################################################
    @staticmethod
    def _logical_test_false(reporting_dict=None):
        # Purpose: performs the actual comparison
        return True if reporting_dict[KWARGS][EXPER] is False else False

    def _test_false_common(self, **kwargs):
        return self._assertion_post_processor(
            message=f'exper={kwargs[EXPER]} should evaluate to False',
            helper=self._logical_test_false,
            **kwargs,
        )

    def require_false(self, exper=None, **kwargs):
        # Description: records error if condition not met
        return self._test_false_common(exper=exper, **kwargs)

    def expect_false(self, exper=None, **kwargs):
        # Description: records warning if condition not met
        return self._test_false_common(exper=exper, **kwargs)

    ################################################################################
    @staticmethod
    def _logical_test_is(reporting_dict=None):
        # Purpose: performs the actual comparison
        return reporting_dict[KWARGS][EXPER1] is reporting_dict[KWARGS][EXPER2]

    def _test_is_common(self, **kwargs):
        return self._assertion_post_processor(
            message=f'exper1={kwargs[EXPER1]} is exper2={kwargs[EXPER2]}',
            helper=self._logical_test_is,
            **kwargs,
        )

    def require_is(self, exper1=None, exper2=None, **kwargs):
        # Description: records error if condition not met
        return self._test_is_common(exper1=exper1, exper2=exper2, **kwargs)

    def expect_is(self, exper1=None, exper2=None, **kwargs):
        # Description: records warning if condition not met
        return self._test_is_common(exper1=exper1, exper2=exper2, **kwargs)

    ################################################################################
    @staticmethod
    def _logical_test_is_not(reporting_dict=None):
        # Purpose: performs the actual comparison
        return reporting_dict[KWARGS][EXPER1] is not reporting_dict[KWARGS][EXPER2]

    def _test_is_not_common(self, **kwargs):
        return self._assertion_post_processor(
            message=f'exper1={kwargs[EXPER1]} is not exper2={kwargs[EXPER2]}',
            helper=self._logical_test_is_not,
            **kwargs,
        )

    def require_is_not(self, exper1=None, exper2=None, **kwargs):
        # Description: records error if condition not met
        return self._test_is_not_common(exper1=exper1, exper2=exper2, **kwargs)

    def expect_is_not(self, exper1=None, exper2=None, **kwargs):
        # Description: records warning if condition not met
        return self._test_is_not_common(exper1=exper1, exper2=exper2, **kwargs)

    ################################################################################
    @staticmethod
    def _logical_test_is_none(reporting_dict=None):
        # Purpose: performs the actual comparison
        return reporting_dict[KWARGS][OBJ] is None

    def _test_is_none_common(self, **kwargs):
        return self._assertion_post_processor(
            message=f'obj={kwargs[OBJ]} is None',
            helper=self._logical_test_is_none,
            **kwargs,
        )

    def require_is_none(self, obj=None, **kwargs):
        # Description: records error if condition not met
        return self._test_is_none_common(obj=obj, **kwargs)

    def expect_is_none(self, obj=None, **kwargs):
        # Description: records warning if condition not met
        return self._test_is_none_common(obj=obj, **kwargs)

    ################################################################################
    @staticmethod
    def _logical_test_is_not_none(reporting_dict=None):
        # Purpose: performs the actual comparison
        return reporting_dict[KWARGS][OBJ] is not None

    def _test_is_not_none_common(self, **kwargs):
        return self._assertion_post_processor(
            message=f'obj={kwargs[OBJ]} is not None',
            helper=self._logical_test_is_not_none,
            **kwargs,
        )

    def require_is_not_none(self, obj=None, **kwargs):
        # Description: records error if condition not met
        return self._test_is_not_none_common(obj=obj, **kwargs)

    def expect_is_not_none(self, obj=None, **kwargs):
        # Description: records warning if condition not met
        return self._test_is_not_none_common(obj=obj, **kwargs)

    ################################################################################
    @staticmethod
    def _logical_test_in(reporting_dict=None):
        # Purpose: performs the actual comparison
        return reporting_dict[KWARGS][MEMBER] in reporting_dict[KWARGS][CONTAINER]

    def _test_in_common(self, **kwargs):
        return self._assertion_post_processor(
            message=f'member={kwargs[MEMBER]} is in container={kwargs[CONTAINER]}',
            helper=self._logical_test_in,
            **kwargs,
        )

    def require_in(self, member=None, container=None, **kwargs):
        # Description: records error if condition not met
        return self._test_in_common(member=member, container=container, **kwargs)

    def expect_in(self, member=None, container=None, **kwargs):
        # Description: records warning if condition not met
        return self._test_in_common(member=member, container=container, **kwargs)

    ################################################################################
    @staticmethod
    def _logical_test_not_in(reporting_dict=None):
        # Purpose: performs the actual comparison
        return reporting_dict[KWARGS][MEMBER] not in reporting_dict[KWARGS][CONTAINER]

    def _test_not_in_common(self, **kwargs):
        return self._assertion_post_processor(
            message=f'member={kwargs[MEMBER]} is not in container={kwargs[CONTAINER]}',
            helper=self._logical_test_not_in,
            **kwargs,
        )

    def require_not_in(self, member=None, container=None, **kwargs):
        # Description: records error if condition not met
        return self._test_not_in_common(member=member, container=container, **kwargs)

    def expect_not_in(self, member=None, container=None, **kwargs):
        # Description: records warning if condition not met
        return self._test_not_in_common(member=member, container=container, **kwargs)
