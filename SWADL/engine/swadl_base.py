# File: SWADLbase.py
# Purpose: Base class for UI interactive code. Wraps interaction with webdriver
import datetime
import gc
import inspect
import logging
import time
import traceback

from SWADL.engine import bannerizer
from SWADL.engine.swadl_cfg import cfgdict
from SWADL.engine.swadl_constants import DRIVER, TEST_DATA, ID, PASSED, FAILED, MESSAGE, REPORTING_DICT, SELF__DICT__, \
    FATAL, TEST_OBJECT, RESULT, ARGSFIELDS, HELPER, ARGS, KWARGS, LOGICAL_RESULT, TIME_STARTED, TIME_FINISHED, \
    ARGSCOUNT, ARGSCOUNT_OK, STACKTRACE, WARN, ASSERT, ERROR, TITLE
from SWADL.engine.swadl_constants import SUBSTITUTION_SOURCES
from SWADL.engine.swadl_constants import TEST_NAME
from SWADL.engine.swadl_constants import TIMEOUT
from SWADL.engine.swadl_dict import SWADLDict
from SWADL.engine.swadl_exceptions import FrameworkError


logger = logging.getLogger(__name__)

class SWADLBase(object):
    # Purpose: Base class for UI interactive code. Wraps interaction with webdriver
    # Notes: Adds cfgdict and driver to all UI control classes

    substitution_sources = None
    # Purpose: on a per item basis, allows us to set dictionaries that will be used to try and resolve
    #          f-string type substitutions (by default self.__dict__ is the only one specified, but
    #          if the cfgdict[SUBSTITUTION_SOURCES] exists and contains a list of dictionaries,
    #          all calls can share that one as well.
    #          WARNING: ALWAYS BEWARE OF KEY COLLISIONS, THAT'S WHY WE HAVE test_data.dump()!

    name = None

    def __init__(self, name=None, substitution_sources=None, **kwargs):
        # Purpose: Initilizes the instance, appies unused kwargs
        # Inputs: - name - The name of this object. Used for reporting. REQUIRED!
        #         - substitution_sources - list of string, values to use when calling resolve_substitutions()
        #           from within this object
        #         - key/value pairs to apply to the instance
        assert name or self.name, (
            f"You must specify a valid 'name' keyword for this {self.__class__.__name__}"
        )
        # Page sections can just have their class as their names, but for all others, it should be added.
        if not self.__class__.__name__ == name:
            name = f"({self.__class__.__name__}){name}"
        self.__dict__[ID] = name
        self.name = name

        self.parent = None
        self.apply_kwargs(kwargs)

        # these are to make this fuctionality avilable to every object using it
        self.cfgdict = cfgdict
        self.driver = self.cfgdict[DRIVER]
        self.test_data = self.cfgdict[TEST_DATA]

        # sort out substitutions. If this has been specified, it's an instance override, so
        # replace the inherited one.
        self.substitution_sources = [self.__dict__]
        if substitution_sources:
            for item in substitution_sources:
                self.substitution_sources.append(substitution_sources)
        if SUBSTITUTION_SOURCES in cfgdict:
            for item in cfgdict[SUBSTITUTION_SOURCES]:
                self.substitution_sources.append(item)

    def __str__(self):
        # Purpose: adds the self.name to the base __str__() result
        base = super().__str__()
        return f'{base}/{self.get_name()}'

    def apply_kwargs(self, kwargs):
        # Purpose: Makes otherwise unused kwargs pairs into members of `self`
        # Inputs: (dict)kwargs: dictionary who's values we want to add
        # We use this to add additional keys to an object that can be picked
        # up later.
        self.__dict__.update(**kwargs)

    def bannerize(self, data=None, title=None):
        # Purpose: This hooks bannerizer into the SWADL classes.
        # See bannerizer.py for more information.
        # Used for reporting.
        if data is None:
            data = self.__dict__
        return bannerizer.bannerize(data=data, title=title)

    def dump(self):
        # Purpose: dump local contents for debugging
        result = self.bannerize(data=self.__dict__, title=self.get_name())
        print(result)
        return result

    def get_name(self):
        # Purpose: Returns the name of the thing
        # Notes: If self.parent is not None, prefixes the name with the parent's name
        # the names get used all over to identify the object we're reporting on
        test_name = cfgdict.get(TEST_NAME, '')
        if test_name:
            if self.name != test_name:
                test_name = f"{test_name}/"
            else:
                test_name = ""
        if hasattr(self, 'parent') and self.parent:
            parent_name = f"{self.parent.name}."
        else:
            parent_name = ""

        return f"{test_name}{parent_name}{self.name}"

    @classmethod
    def get_timestamp(cls, time=None):
        # Purpose: To have a standardized timestamp for anything that needs it.
        # Optionally takes a datetime value, or uses now.
        # Returns: yymmdd_hhmmss.xxxxxx as string
        if time is None:
            time = datetime.datetime.now()
        return time.strftime("%Y%m%d_%H%M%S.%f")

    class _SafeDict(dict):
        # Purpose: Fills in f-string style braced arguments from keys in the
        #          dictionaries copied to cfgdict[SUBSTITUTION_SOURCES]
        # Usage:
        #    print("{a} {b} {c}".format_map(SafeDict("a": "1", "b": "2")))
        #    "1 2 {C}"
        #    Without rendering any errors
        def __missing__(self, key):
            # Purpose: Just substitutes the missing element back into the string
            return '{' + key + '}'

    def resolve_substitutions(self, in_string, substitution_sources=None):
        # Purpose: Perform f-string style substitions without errors for missing keys, and using
        #          sources like global test data or other dicts to feed the substitution engine
        # Inputs: - (str)in_string - the string to do substitutions on
        #         - dict or list of dict - items to use for substition

        if not substitution_sources:
            substitution_sources = self.substitution_sources

        master_hash = self._SafeDict()
        for item in substitution_sources:
            master_hash.update(item)
        master_hash.update(self.__dict__)

        iterations_to_go = 20
        result = in_string
        before = in_string

        # this loop is here so if we won't loop forever
        # we stop as soon as it stops making changes.
        while iterations_to_go > 0:
            iterations_to_go -= 1
            result = result.format_map(master_hash)
            if result == before:
                break
            before = result
        return result

    def _get_method_name(self):
        # Purpose: Get the name of the calling method
        test_name = cfgdict[TEST_NAME]
        class_name = self.__class__.__name__
        method_name = inspect.stack()[1][0].f_code.co_name
        return f'{test_name}/{class_name}.{method_name}'

    def _get_instance_name(self):
        # Purpose: Returns the best guess name of the instance name
        result = 'unknown instance'
        raw = self._get_instance_names()
        if len(raw) > 0:
            result = raw[0]
        return result

    def _get_instance_names(self):
        # Purpose: Returns the best guess of entire set of instance names for this object.
        #         Uses garbage collection library to iterate through instances.
        referrers = gc.get_referrers(self)
        result = []
        dict_of_things = {}
        for item in referrers:
            if isinstance(item, dict):
                dict_of_things = item
                break
        for key, value in dict_of_things.items():
            if value == self:
                result.append(key)
        if not result:
            result = ['unknown instance']
        return result

    def _remove_keys(self, incoming_dict, list_of_keys=None):
        # Purpose: Remove keys from kwargs before passing them on. For instance, most webdriver
        #          calls do not accept timeout as a keyword.
        # Inputs: - (dict)incoming_dict: a kwargs style dict
        #         - (list or set)list_of_keys: keys to remove
        # Returns: a copy of the dict with the noted keys removed
        modified_dict = dict(incoming_dict)  # make me a shallow copy
        list_of_keys = [] if not list_of_keys else list_of_keys
        for key in list_of_keys:
            if key in modified_dict:
                del(modified_dict[key])
        return modified_dict

    def _remove_keys_webdriver_doesnt_like(self, incoming_dict):
        # Purpose: Remove keys from kwargs that webdriver calls don't like
        # Inputs: - (dict)incoming_dict: a kwargs style dict
        # Returns: a copy of the dict with the noted keys removed
        # Notes: It is expected that we'll keep adding to this list
        keys_webdriver_doesnt_like = (
            TIMEOUT,
        )
        return self._remove_keys(incoming_dict, keys_webdriver_doesnt_like)

    def timeout_remaining(self, end_time=None, timeout=0, minimum=1):
        # Purpose: Return timeout remaining
        # Args:
        #     timeout (float, optional): expected timeout. Defaults to 0.
        #     minimum (float, optional): minimum timeout. Defaults to 1.
        time_now = time.time()
        if not end_time:
            end_time = time_now + timeout
        if end_time < time_now:
            end_time = time_now + minimum
        return end_time - time_now

    #######################################################################
    #######################################################################
    #######################################################################
    #######################################################################
    #######################################################################
    #######################################################################
    #######################################################################
    #######################################################################
    #######################################################################
    #######################################################################


    def make_framework_error(self, message=None, reporting_dict=None):
        framework_error = FrameworkError(
            self.bannerize(
                {
                    "FrameworkError": {
                        MESSAGE: message,
                        REPORTING_DICT: reporting_dict,
                        SELF__DICT__: self.__dict__,
                    }
                }
            )
        )
        return framework_error

    def assertion_post_processor(self,
                     argsfields=None,
                     message=None,
                     helper=None,
                     args=None,
                     kwargs=None,
            ):
        reporting_dict = SWADLDict()
        reporting_dict[TITLE] = 'SWADL Validation'
        reporting_dict[ID] = inspect.stack()[1][0].f_code.co_name
        reporting_dict[ARGSFIELDS] = argsfields
        reporting_dict[MESSAGE] = message
        reporting_dict[HELPER] = helper
        reporting_dict[ARGS] = args
        reporting_dict[KWARGS] = kwargs

        reporting_dict[LOGICAL_RESULT] = False
        reporting_dict[RESULT] = "Failed to complete"
        reporting_dict[SELF__DICT__] = self.__dict__
        reporting_dict[TIME_STARTED] = time.time()
        reporting_dict[TIME_FINISHED] = time.time()
        reporting_dict[ARGSCOUNT] = len(reporting_dict[ARGS])
        reporting_dict[ARGSCOUNT_OK] = len(reporting_dict[ARGS]) > 1
        reporting_dict[STACKTRACE] = traceback.format_stack()

        if len(reporting_dict[ARGS]) < len(reporting_dict[ARGSFIELDS]):
            raise self.make_framework_error(
                message="failed because not passed enough args",
                reporting_dict=reporting_dict,
            )

        reporting_dict[LOGICAL_RESULT] = reporting_dict[HELPER](reporting_dict)
        reporting_dict[TIME_FINISHED] = time.time()

        if reporting_dict[LOGICAL_RESULT]:
            reporting_dict[RESULT] = PASSED
        else:
            reporting_dict[RESULT] = FAILED
            self.test_data[TEST_OBJECT].accumulated_failures.append(reporting_dict)

        fatal = reporting_dict[KWARGS].get(FATAL, False)
        message = self.bannerize(reporting_dict)
        if reporting_dict[ID].upper().startswith(ASSERT):
            logger.critical(message)
            if fatal:
                raise AssertionError(message)
        elif reporting_dict[ID].upper().startswith(ERROR):
            logger.error(message)
            if fatal:
                raise Exception(message)
        elif reporting_dict[ID].upper().startswith(WARN):
            logger.warn(message)

        return reporting_dict[LOGICAL_RESULT]

    ################################################################################

    def _logical_test_equal(self, reporting_dict=None):
        return reporting_dict[ARGS][0] == reporting_dict[ARGS][1]

    def assertEqual(self, *args, **kwargs):
        return self.assertion_post_processor(
            argsfields=['x', 'y'],
            message='{x} and {y} should be equal',
            helper=self._logical_test_equal,
            args=args,
            kwargs=kwargs,
        )
    def requireEqual(self, *args, **kwargs):
        return self.assertion_post_processor(
            argsfields=['x', 'y'],
            message='{x} and {y} should be equal',
            helper=self._logical_test_equal,
            args=args,
            kwargs=kwargs,
        )
    def expectEqual(self, *args, **kwargs):
        return self.assertion_post_processor(
            argsfields=['x', 'y'],
            message='{x} and {y} should NOT be equal',
            helper=self._logical_test_equal,
            args=args,
            kwargs=kwargs,
        )

    ################################################################################
    def _logical_test_not_equal(self, *args, **kwargs):
        self._args_to_kwargs(
            args=args, kwargs=kwargs,
            fields=[FIRST, SECOND, MESSAGE],
            defaults={
                FIRST: None,
                SECOND: None,
                MESSAGE: None,
                VALIDATION_TESTS: NOT_EQUAL,
            })

        kwargs[const.VALIDATION_LOGICAL_RESULT] = (kwargs[FIRST] == kwargs[SECOND]) is False
        return self._post_process_logic(kwargs)

    def expectNotEqual(self, *args, **kwargs):
        return self._logical_test_not_equal(*args, validation_type=EXPECT, **kwargs)

    def verifyNotEqual(self, *args, **kwargs):
        return self._logical_test_not_equal(*args, validation_type=VERIFY, **kwargs)

    def assertNotEqual(self, *args, **kwargs):
        return self._logical_test_not_equal(*args, validation_type=ASSERT, **kwargs)

    expect_not_equal = expectNotEqual
    verify_not_equal = verifyNotEqual
    assert_not_equal = assertNotEqual

    ################################################################################
    def _logical_test_error(self, *args, **kwargs):
        """
        Method:
            _logical_test_error

        Purpose:
            Used by verify_error, assert_error, expected_error to perform the requisite
            setup and teardown to report a failed validation.

        Parameters:
            No parameters are required, but some optional, useful ones include:
            - fatal (bool): the result should exit the test
            - message (str): the message to use to report success

        Returns:
            - False (because after all, the test failed)
        """
        self._args_to_kwargs(
            args=args, kwargs=kwargs,
            fields=[MESSAGE, FATAL],
            defaults={
                MESSAGE: f'{kwargs[VALIDATION_TYPE]} error',
                FATAL: False,
                VALIDATION_TESTS: ERROR,
                TEST_RESULT_STRING: ERROR
            })

        kwargs[const.VALIDATION_LOGICAL_RESULT] = False
        return self._post_process_logic(kwargs)

    def expectError(self, *args, **kwargs):
        return self._logical_test_error(
            *args,
            validation_type=EXPECT,
            test_result_string=ERROR,
            **kwargs  # pycharm complained about trailing comma after **, so removed it. -amm
        )

    def verifyError(self, *args, **kwargs):
        return self._logical_test_error(
            *args,
            validation_type=VERIFY,
            test_result_string=ERROR,
            **kwargs  # pycharm complained about trailing comma after **, so removed it. -amm
        )

    def assertError(self, *args, **kwargs):
        return self._logical_test_error(
            *args,
            validation_type=ASSERT,
            test_result_string=ERROR,
            **kwargs  # pycharm complained about trailing comma after **, so removed it. -amm
        )

    expect_error = expectError
    verify_error = verifyError
    assert_error = assertError

    ################################################################################
    def _logical_test_fail(self, *args, **kwargs):
        """
        Method:
            _logical_test_fail

        Purpose:
            Used by verify_fail, assert_fail, expected_fail to perform the requisite
            setup and teardown to report a failed validation.

        Parameters:
            No parameters are required, but some optional, useful ones include:
            - fatal (bool): the result should exit the test
            - message (str): the message to use to report success

        Returns:
            - False (because after all, the test failed)
        """
        self._args_to_kwargs(
            args=args, kwargs=kwargs,
            fields=[MESSAGE, FATAL],
            defaults={
                MESSAGE: '{} error'.format(kwargs[VALIDATION_TYPE]),
                FATAL: False,
                VALIDATION_TESTS: FAILED,
                TEST_RESULT_STRING: FAILED
            })

        kwargs[const.VALIDATION_LOGICAL_RESULT] = False
        return self._post_process_logic(kwargs)

    def expectFailed(self, *args, **kwargs):
        return self._logical_test_error(
            *args,
            validation_type=EXPECT,
            test_result_string=FAILED,
            **kwargs  # pycharm complained about trailing comma after **, so removed it. -amm
        )

    def verifyFailed(self, *args, **kwargs):
        return self._logical_test_error(
            *args,
            validation_type=VERIFY,
            test_result_string=FAILED,
            **kwargs  # pycharm complained about trailing comma after **, so removed it. -amm
        )

    def assertFailed(self, *args, **kwargs):
        return self._logical_test_error(
            *args,
            validation_type=ASSERT,
            test_result_string=FAILED,
            **kwargs  # pycharm complained about trailing comma after **, so removed it. -amm
        )

    expect_failed = expectFailed
    verify_failed = verifyFailed
    assert_failed = assertFailed

    ################################################################################
    def _logical_test_passed(self, *args, **kwargs):
        """
        Method:
            _logical_test_passed

        Purpose:
            Used by verify_passed, assert_passed, expected_passed to perform the requisite
            setup and teardown to report a passed validation.

        Parameters:
            No parameters are required, but some optional, useful ones include:
            - message (str) the message to use to report success

        Returns:
            - True (because after all, the test passed)
        """
        self._args_to_kwargs(
            args=args, kwargs=kwargs,
            fields=[MESSAGE, FATAL],
            defaults={
                MESSAGE: '{} passed'.format(kwargs[VALIDATION_TYPE]),
                FATAL: False,
                VALIDATION_TESTS: PASSED,
                TEST_RESULT_STRING: PASSED
            })

        kwargs[const.VALIDATION_LOGICAL_RESULT] = True
        return self._post_process_logic(kwargs)

    def expectPassed(self, *args, **kwargs):
        return self._logical_test_passed(
            *args,
            validation_type=EXPECT,
            test_result_string=PASSED,
            **kwargs  # pycharm complained about trailing comma after **, so removed it. -amm
        )

    def verifyPassed(self, *args, **kwargs):
        return self._logical_test_passed(
            *args,
            validation_type=VERIFY,
            test_result_string=PASSED,
            **kwargs  # pycharm complained about trailing comma after **, so removed it. -amm
        )

    def assertPassed(self, *args, **kwargs):
        return self._logical_test_passed(
            *args,
            validation_type=ASSERT,
            test_result_string=PASSED,
            **kwargs  # pycharm complained about trailing comma after **, so removed it. -amm
        )

    expect_passed = expectPassed
    verify_passed = verifyPassed
    assert_passed = assertPassed

    ################################################################################
    def _logical_test_true(self, *args, **kwargs):
        self._args_to_kwargs(
            args=args, kwargs=kwargs,
            fields=[ACTUAL_VALUE, MESSAGE],
            defaults={
                EXPECTED_VALUE: True,
                ACTUAL_VALUE: None,
                MESSAGE: None,
                VALIDATION_TESTS: TRUE,
            })

        # this is exactly how it's implemented in unittest.testcase
        kwargs[const.VALIDATION_LOGICAL_RESULT] = False
        if kwargs[ACTUAL_VALUE]:
            kwargs[const.VALIDATION_LOGICAL_RESULT] = True
        return self._post_process_logic(kwargs)

    def expectTrue(self, *args, **kwargs):
        return self._logical_test_true(*args, validation_type=EXPECT, **kwargs)

    def verifyTrue(self, *args, **kwargs):
        return self._logical_test_true(*args, validation_type=VERIFY, **kwargs)

    def assertTrue(self, *args, **kwargs):
        return self._logical_test_true(*args, validation_type=ASSERT, **kwargs)

    expect_true = expectTrue
    verify_true = verifyTrue
    assert_true = assertTrue

    ################################################################################
    def _logical_test_false(self, *args, **kwargs):
        self._args_to_kwargs(
            args=args, kwargs=kwargs,
            fields=[ACTUAL_VALUE, MESSAGE],
            defaults={
                EXPECTED_VALUE: False,
                ACTUAL_VALUE: None,
                MESSAGE: None,
                VALIDATION_TESTS: FALSE,
            })

        # this is exactly how it's implemented in unittest.testcase
        kwargs[const.VALIDATION_LOGICAL_RESULT] = False
        if not kwargs[ACTUAL_VALUE]:
            kwargs[const.VALIDATION_LOGICAL_RESULT] = True
        return self._post_process_logic(kwargs)

    def expectFalse(self, *args, **kwargs):
        return self._logical_test_false(*args, validation_type=EXPECT, **kwargs)

    def verifyFalse(self, *args, **kwargs):
        return self._logical_test_false(*args, validation_type=VERIFY, **kwargs)

    def assertFalse(self, *args, **kwargs):
        return self._logical_test_false(*args, validation_type=ASSERT, **kwargs)

    expect_false = expectFalse
    verify_false = verifyFalse
    assert_false = assertFalse

    ################################################################################
    def _logical_test_is(self, *args, **kwargs):
        self._args_to_kwargs(
            args=args, kwargs=kwargs,
            fields=[FIRST, SECOND, MESSAGE],
            defaults={
                FIRST: None,
                SECOND: None,
                MESSAGE: None,
                VALIDATION_TESTS: 'is',
            })

        kwargs[const.VALIDATION_LOGICAL_RESULT] = kwargs[FIRST] is kwargs[SECOND]
        return self._post_process_logic(kwargs)

    def expectIs(self, *args, **kwargs):
        return self._logical_test_is(*args, validation_type=EXPECT, **kwargs)

    def verifyIs(self, *args, **kwargs):
        return self._logical_test_is(*args, validation_type=VERIFY, **kwargs)

    def assertIs(self, *args, **kwargs):
        return self._logical_test_is(*args, validation_type=ASSERT, **kwargs)

    expect_is = expectIs
    verify_is = verifyIs
    assert_is = assertIs

    ################################################################################
    def _logical_test_is_not(self, *args, **kwargs):
        self._args_to_kwargs(
            args=args, kwargs=kwargs,
            fields=[FIRST, SECOND, MESSAGE],
            defaults={
                FIRST: None,
                SECOND: None,
                MESSAGE: None,
                VALIDATION_TESTS: 'is_not',
            })

        kwargs[const.VALIDATION_LOGICAL_RESULT] = kwargs[FIRST] is not kwargs[SECOND]
        return self._post_process_logic(kwargs)

    def expectIsNot(self, *args, **kwargs):
        return self._logical_test_is_not(*args, validation_type=EXPECT, **kwargs)

    def verifyIsNot(self, *args, **kwargs):
        return self._logical_test_is_not(*args, validation_type=VERIFY, **kwargs)

    def assertIsNot(self, *args, **kwargs):
        return self._logical_test_is_not(*args, validation_type=ASSERT, **kwargs)

    expect_is_not = expectIsNot
    verify_is_not = verifyIsNot
    assert_is_not = assertIsNot

    ################################################################################
    def _logical_test_is_none(self, *args, **kwargs):
        self._args_to_kwargs(
            args=args, kwargs=kwargs,
            fields=[ACTUAL_VALUE, MESSAGE],
            defaults={
                EXPECTED_VALUE: None,
                ACTUAL_VALUE: None,
                MESSAGE: None,
                VALIDATION_TESTS: 'is_none'
            })

        kwargs[const.VALIDATION_LOGICAL_RESULT] = kwargs[EXPECTED_VALUE] is kwargs[ACTUAL_VALUE]
        return self._post_process_logic(kwargs)

    def expectIsNone(self, *args, **kwargs):
        return self._logical_test_is_none(*args, validation_type=EXPECT, **kwargs)

    def verifyIsNone(self, *args, **kwargs):
        return self._logical_test_is_none(*args, validation_type=VERIFY, **kwargs)

    def assertIsNone(self, *args, **kwargs):
        return self._logical_test_is_none(*args, validation_type=ASSERT, **kwargs)

    expect_is_none = expectIsNone
    verify_is_none = verifyIsNone
    assert_is_none = assertIsNone

    ################################################################################
    def _logical_test_is_not_none(self, *args, **kwargs):
        self._args_to_kwargs(
            args=args, kwargs=kwargs,
            fields=[ACTUAL_VALUE, MESSAGE],
            defaults={
                ACTUAL_VALUE: "not none",
                MESSAGE: None,
                VALIDATION_TESTS: 'is_not_none',
            })

        kwargs[const.VALIDATION_LOGICAL_RESULT] = kwargs[ACTUAL_VALUE] is not None
        return self._post_process_logic(kwargs)

    def expectIsNotNone(self, *args, **kwargs):
        return self._logical_test_is_not_none(*args, validation_type=EXPECT, **kwargs)

    def verifyIsNotNone(self, *args, **kwargs):
        return self._logical_test_is_not_none(*args, validation_type=VERIFY, **kwargs)

    def assertIsNotNone(self, *args, **kwargs):
        return self._logical_test_is_not_none(*args, validation_type=ASSERT, **kwargs)

    expect_is_not_none = expectIsNotNone
    verify_is_not_none = verifyIsNotNone
    assert_is_not_none = assertIsNotNone

    ################################################################################
    def _logical_test_in(self, *args, **kwargs):
        self._args_to_kwargs(
            args=args, kwargs=kwargs,
            fields=[MEMBER, CONTAINER, MESSAGE],
            defaults={
                MEMBER: None,
                CONTAINER: None,
                MESSAGE: None,
                VALIDATION_TESTS: 'in'
            })

        kwargs[const.VALIDATION_LOGICAL_RESULT] = kwargs[MEMBER] in kwargs[CONTAINER]
        return self._post_process_logic(kwargs)

    def expectIn(self, *args, **kwargs):
        return self._logical_test_in(*args, validation_type=EXPECT, **kwargs)

    def verifyIn(self, *args, **kwargs):
        return self._logical_test_in(*args, validation_type=VERIFY, **kwargs)

    def assertIn(self, *args, **kwargs):
        return self._logical_test_in(*args, validation_type=ASSERT, **kwargs)

    expect_in = expectIn
    verify_in = verifyIn
    assert_in = assertIn

    ################################################################################
    def _logical_test_not_in(self, *args, **kwargs):
        self._args_to_kwargs(
            args=args, kwargs=kwargs,
            fields=[MEMBER, CONTAINER, MESSAGE],
            defaults={
                MEMBER: None,
                CONTAINER: None,
                MESSAGE: None,
                VALIDATION_TESTS: 'not_in',
            })

        kwargs[const.VALIDATION_LOGICAL_RESULT] = kwargs[MEMBER] not in kwargs[CONTAINER]
        return self._post_process_logic(kwargs)

    def expectNotIn(self, *args, **kwargs):
        return self._logical_test_not_in(*args, validation_type=EXPECT, **kwargs)

    def verifyNotIn(self, *args, **kwargs):
        return self._logical_test_not_in(*args, validation_type=VERIFY, **kwargs)

    def assertNotIn(self, *args, **kwargs):
        return self._logical_test_not_in(*args, validation_type=ASSERT, **kwargs)

    expect_not_in = expectNotIn
    verify_not_in = verifyNotIn
    assert_not_in = assertNotIn
