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
from SWADL.engine.swadl_constants import ARGS
from SWADL.engine.swadl_constants import ARGSCOUNT
from SWADL.engine.swadl_constants import ARGSCOUNT_OK
from SWADL.engine.swadl_constants import ARGSFIELDS
from SWADL.engine.swadl_constants import ASSERT
from SWADL.engine.swadl_constants import CONTAINER
from SWADL.engine.swadl_constants import DIVIDER
from SWADL.engine.swadl_constants import DRIVER
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
from SWADL.engine.swadl_constants import SUBSTITUTION_SOURCES
from SWADL.engine.swadl_constants import TEST_DATA
from SWADL.engine.swadl_constants import TEST_NAME
from SWADL.engine.swadl_constants import TEST_OBJECT
from SWADL.engine.swadl_constants import TIMEOUT
from SWADL.engine.swadl_constants import TIME_FINISHED
from SWADL.engine.swadl_constants import TIME_STARTED
from SWADL.engine.swadl_constants import TITLE
from SWADL.engine.swadl_constants import TRACEBACK_SPACES
from SWADL.engine.swadl_constants import X
from SWADL.engine.swadl_constants import Y
from SWADL.engine.swadl_dict import SWADLDict
from SWADL.engine.swadl_exceptions import FrameworkError


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

    _logger = None
    @property
    def log(self):
        # Purpose: To provide access to logs everywhere without another import
        # returns a logger instance
        # usage: self.log.debug('foo')
        if not self.__class__._logger:
            self.__class__._logger = logging.getLogger(__name__)
        return self.__class__._logger

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
    def _process_stack_trace(self, exc_info=None):
        # Purpose: Standardizes the traceback information
        # Parameters: exc_info (list of string) the traceback info to process
        # Returns: the normalized list
        # Usage: exc_info = process_stack_trace(exc_info)
        # sometimes we have a trailing blank line or two
        #import pdb ; pdb.set_trace()
        exc_info = exc_info if exc_info else traceback.format_stack()
        while exc_info[-1].strip() == '':
            del (exc_info[-1])

        # now we're going to chop off all the nose2 traceback entries
        line_added = False
        recording = False
        result = [DIVIDER + 'test part:']
        for exc_item in exc_info:

            # break this up into lines
            interim_value = [exc_item.replace('\n', '')]

            # see if we should start reporting yet or not
            if 'Project\demos' in exc_item and recording is False:
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
                        result.append(DIVIDER + 'framework part:')
                    if len(item.strip()) > 0:
                        result.append(item)

        if result:
            result.append(DIVIDER + 'error part:')
        return result

    def _make_framework_error(self, message=None, reporting_dict=None):
        # Purpose: Produces a FrameworkError with the passed data
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

    def _assertion_post_processor(self,
                                  argsfields=None,
                                  message=None,
                                  helper=None,
                                  args=None,
                                  kwargs=None,
                                  ):
        # Purpose; Takes information provided by the caller about the
        # kind of assertion/error/warning, and completes the test,
        # recording and logging steps.
        reporting_dict = SWADLDict()
        reporting_dict[TITLE] = 'SWADL:Assertion'
        self.test_data[f'VALIDATION at {self.get_timestamp()}'] = reporting_dict
        # now assume each group will have a group processor
        # we want the method name that called that, not our
        # direct caller. Hence the [2] in the lione below
        reporting_dict[ID] = inspect.stack()[2][0].f_code.co_name
        reporting_dict[MESSAGE] = message
        reporting_dict[ARGSFIELDS] = argsfields
        reporting_dict[ARGS] = args
        reporting_dict[KWARGS] = kwargs
        
        reporting_dict[HELPER] = helper
        reporting_dict[LOGICAL_RESULT] = False  # overwritten later we hope :)
        reporting_dict[RESULT] = "Failed to complete"  # overwritten later we hope :)
        reporting_dict[SELF__DICT__] = self.__dict__
        reporting_dict[TIME_STARTED] = time.time()
        reporting_dict[TIME_FINISHED] = time.time()

        # rebuild args from kwargs
        # first, copy the args to the kwargs by field name, if any were specified
        for index in range(0, len(reporting_dict[ARGS])):
            kwargs[reporting_dict[ARGSFIELDS][index]] = reporting_dict[ARGS][index]
        # now test whether all are present
        args_found_by_name = []
        for index in range(0, len(reporting_dict[ARGSFIELDS])):
            field_name = reporting_dict[ARGSFIELDS][index]
            if field_name in reporting_dict[KWARGS]:
                args_found_by_name.append(field_name)
            else:
                raise self._make_framework_error(
                    message=f"failed because missing arg: {field_name}",
                    reporting_dict=reporting_dict,
                )
        reporting_dict[ARGSCOUNT] = len(args_found_by_name)
        reporting_dict[ARGSCOUNT_OK] = reporting_dict[ARGSCOUNT] >= len(reporting_dict[ARGSFIELDS])
        if not reporting_dict[ARGSCOUNT_OK]:
            reporting_dict[STACKTRACE] = self._process_stack_trace(traceback.format_stack())
            raise self._make_framework_error(
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

        if reporting_dict[ID].upper().startswith(ASSERT):
            reporting_dict[STACKTRACE] = self._process_stack_trace(traceback.format_stack())
            message = self.bannerize(reporting_dict)
            self.log.critical(message)
            if reporting_dict[KWARGS].get(FATAL, False):
                raise AssertionError(message)
        elif reporting_dict[ID].upper().startswith(REQUIRE):
            reporting_dict[STACKTRACE] = self._process_stack_trace(traceback.format_stack())
            message = self.bannerize(reporting_dict)
            self.log.error(message)
            if reporting_dict[KWARGS].get(FATAL, False):
                raise Exception(message)
        elif reporting_dict[ID].upper().startswith(EXPECT):
            message = self.bannerize(reporting_dict)
            self.log.warning(message)

        return reporting_dict[LOGICAL_RESULT]

    ################################################################################

    def _logical_test_equal(self, reporting_dict=None):
        # Purpose: performs the actual comparison
        return reporting_dict[KWARGS][X] == reporting_dict[KWARGS][Y]

    def _test_equal_common(self, args, kwargs):
        # Purpose: to get all the data passed to the post processor
        return self._assertion_post_processor(
            argsfields=[X, Y],
            message='{x} and {y} should be equal',
            helper=self._logical_test_equal,
            args=args,
            kwargs=kwargs,
        )

    def assert_equal(self, *args, **kwargs):
        # Description: records assertion failure if condition not met
        return self._test_equal_common(args, kwargs)

    def require_equal(self, *args, **kwargs):
        # Description: records error if condition not met
        return self._test_equal_common(args, kwargs)

    def expect_equal(self, *args, **kwargs):
        # Description: records warning if condition not met
        return self._test_equal_common(args, kwargs)

    ################################################################################
    def _logical_test_not_equal(self, reporting_dict=None):
        # Purpose: performs the actual comparison
        return not (reporting_dict[KWARGS][X] == reporting_dict[KWARGS][Y])

    def _test_not_equal_common(self, args, kwargs):
        # Purpose: to get all the data passed to the post processor
        return self._assertion_post_processor(
            argsfields=[X, Y],
            message='{x} and {y} should NOT be equal',
            helper=self._logical_test_not_equal,
            args=args,
            kwargs=kwargs,
        )

    def assert_not_equal(self, *args, **kwargs):
        # Description: records assertion failure if condition not met
        return self._test_not_equal_common(args, kwargs)

    def require_not_equal(self, *args, **kwargs):
        # Description: records error if condition not met
        return self._test_not_equal_common(args, kwargs)

    def expect_not_equal(self, *args, **kwargs):
        # Description: records warning if condition not met
        return self._test_not_equal_common(args, kwargs)

    ################################################################################
    def _logical_test_true(self, reporting_dict=None):
        # Purpose: performs the actual comparison
        return True if reporting_dict[KWARGS][EXPER] else False

    def _test_true_common(self, args, kwargs):
        # Purpose: to get all the data passed to the post processor
        return self._assertion_post_processor(
            argsfields=[EXPER],
            message='{exper} should evaluate to True',
            helper=self._logical_test_true,
            args=args,
            kwargs=kwargs,
        )

    def assert_true(self, *args, **kwargs):
        # Description: records assertion failure if condition not met
        return self._test_true_common(args, kwargs)

    def require_true(self, *args, **kwargs):
        # Description: records error if condition not met
        return self._test_true_common(args, kwargs)

    def expect_true(self, *args, **kwargs):
        # Description: records warning if condition not met
        return self._test_true_common(args, kwargs)

    ################################################################################
    def _logical_test_false(self, reporting_dict=None):
        # Purpose: performs the actual comparison
        return True if reporting_dict[KWARGS][EXPER] is False else False

    def _test_False_common(self, args, kwargs):
        return self._assertion_post_processor(
            argsfields=[EXPER],
            message='{exper} should evaluate to False',
            helper=self._logical_test_false,
            args=args,
            kwargs=kwargs,
        )

    def assert_false(self, *args, **kwargs):
        # Description: records assertion failure if condition not met
        return self._test_False_common(args, kwargs)

    def require_false(self, *args, **kwargs):
        # Description: records error if condition not met
        return self._test_False_common(args, kwargs)

    def expect_false(self, *args, **kwargs):
        # Description: records warning if condition not met
        return self._test_False_common(args, kwargs)

    ################################################################################
    def _logical_test_is(self, reporting_dict=None):
        # Purpose: performs the actual comparison
        return reporting_dict[KWARGS][EXPER1] is reporting_dict[KWARGS][EXPER2]

    def _test_is_common(self, args, kwargs):
        return self._assertion_post_processor(
            argsfields=[EXPER1, EXPER2],
            message='{exper1} is {exper2} should evaluate to True',
            helper=self._logical_test_is,
            args=args,
            kwargs=kwargs,
        )

    def assert_is(self, *args, **kwargs):
        # Description: records assertion failure if condition not met
        return self._test_is_common(args, kwargs)

    def require_is(self, *args, **kwargs):
        # Description: records error if condition not met
        return self._test_is_common(args, kwargs)

    def expect_is(self, *args, **kwargs):
        # Description: records warning if condition not met
        return self._test_is_common(args, kwargs)

    ################################################################################
    def _logical_test_is_not(self, reporting_dict=None):
        # Purpose: performs the actual comparison
        return reporting_dict[KWARGS][EXPER1] is not reporting_dict[KWARGS][EXPER2]

    def _test_is_not_common(self, args, kwargs):
        return self._assertion_post_processor(
            argsfields=[EXPER1, EXPER2],
            message='{exper1} is not {exper2} should evaluate to True',
            helper=self._logical_test_is_not,
            args=args,
            kwargs=kwargs,
        )

    def assert_is_not(self, *args, **kwargs):
        # Description: records assertion failure if condition not met
        return self._test_is_not_common(args, kwargs)

    def require_is_not(self, *args, **kwargs):
        # Description: records error if condition not met
        return self._test_is_not_common(args, kwargs)

    def expect_is_not(self, *args, **kwargs):
        # Description: records warning if condition not met
        return self._test_is_not_common(args, kwargs)

    ################################################################################
    def _logical_test_is_none(self, reporting_dict=None):
        # Purpose: performs the actual comparison
        return reporting_dict[KWARGS][OBJ] is None

    def _test_is_none_common(self, args, kwargs):
        return self._assertion_post_processor(
            argsfields=[OBJ],
            message='{obj} is None',
            helper=self._logical_test_is_none,
            args=args,
            kwargs=kwargs,
        )

    def assert_is_none(self, *args, **kwargs):
        # Description: records assertion failure if condition not met
        return self._test_is_none_common(args, kwargs)

    def require_is_none(self, *args, **kwargs):
        # Description: records error if condition not met
        return self._test_is_none_common(args, kwargs)

    def expect_is_none(self, *args, **kwargs):
        # Description: records warning if condition not met
        return self._test_is_none_common(args, kwargs)

    ################################################################################
    def _logical_test_is_not_none(self, reporting_dict=None):
        # Purpose: performs the actual comparison
        return reporting_dict[KWARGS][OBJ] is not None

    def _test_is_not_none_common(self, args, kwargs):
        return self._assertion_post_processor(
            argsfields=[OBJ],
            message='{obj} is not None',
            helper=self._logical_test_is_not_none,
            args=args,
            kwargs=kwargs,
        )

    def assert_is_not_none(self, *args, **kwargs):
        # Description: records assertion failure if condition not met
        return self._test_is_not_none_common(args, kwargs)

    def require_is_not_none(self, *args, **kwargs):
        # Description: records error if condition not met
        return self._test_is_not_none_common(args, kwargs)

    def expect_is_not_none(self, *args, **kwargs):
        # Description: records warning if condition not met
        return self._test_is_not_none_common(args, kwargs)

    ################################################################################
    def _logical_test_in(self, reporting_dict=None):
        # Purpose: performs the actual comparison
        return reporting_dict[KWARGS][MEMBER] in reporting_dict[KWARGS][CONTAINER]

    def _test_in_common(self, args, kwargs):
        return self._assertion_post_processor(
            argsfields=[MEMBER, CONTAINER],
            message='{member} is in {container}',
            helper=self._logical_test_in,
            args=args,
            kwargs=kwargs,
        )

    def assert_in(self, *args, **kwargs):
        # Description: records assertion failure if condition not met
        return self._test_in_common(args, kwargs)

    def require_in(self, *args, **kwargs):
        # Description: records error if condition not met
        return self._test_in_common(args, kwargs)

    def expect_in(self, *args, **kwargs):
        # Description: records warning if condition not met
        return self._test_in_common(args, kwargs)

    ################################################################################
    def _logical_test_not_in(self, reporting_dict=None):
        # Purpose: performs the actual comparison
        return reporting_dict[KWARGS][MEMBER] not in reporting_dict[KWARGS][CONTAINER]

    def _test_not_in_common(self, args, kwargs):
        return self._assertion_post_processor(
            argsfields=[MEMBER, CONTAINER],
            message='{member} is in {container}',
            helper=self._logical_test_not_in,
            args=args,
            kwargs=kwargs,
        )

    def assert_not_in(self, *args, **kwargs):
        # Description: records assertion failure if condition not met
        return self._test_not_in_common(args, kwargs)

    def require_not_in(self, *args, **kwargs):
        # Description: records error if condition not met
        return self._test_not_in_common(args, kwargs)

    def expect_not_in(self, *args, **kwargs):
        # Description: records warning if condition not met
        return self._test_not_in_common(args, kwargs)
