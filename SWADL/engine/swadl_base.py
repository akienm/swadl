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
from SWADL.engine.swadl_constants import ASSERT
from SWADL.engine.swadl_constants import CALLER
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
from SWADL.engine.swadl_constants import TRACEBACK_SPACES
from SWADL.engine.swadl_constants import X
from SWADL.engine.swadl_constants import Y
from SWADL.engine.swadl_dict import SWADLDict
from SWADL.engine.swadl_exceptions import SWADLTestError
from SWADL.engine.swadl_validator import SWADLValidator


# noinspection SpellCheckingInspection
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
    _logger = None

    #######################################################################
    def __init__(self, name=None, substitution_sources=None, **kwargs):
        # Purpose: Initializes the instance, applies unused kwargs
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

        # these are to make this functionality available to every object using it
        self.cfgdict = cfgdict
        self.driver = self.cfgdict[DRIVER]
        self.test_data = self.cfgdict[TEST_DATA]

        # sort out substitutions. If this has been specified, it's an instance override, so
        # replace the inherited one.
        self.substitution_sources = [self.__dict__]
        if substitution_sources:
            for item in substitution_sources:
                self.substitution_sources.append(item)
        if SUBSTITUTION_SOURCES in cfgdict:
            for item in cfgdict[SUBSTITUTION_SOURCES]:
                self.substitution_sources.append(item)

        # And apply the validations
        self.error_if_equal = SWADLValidator.make_validation()

    def __str__(self):
        # Purpose: adds the self.name to the base __str__() result
        base = super().__str__()
        return f'{base}/{self.get_name()}'

    #######################################################################
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
    #######################################################################

    @property
    def log(self):
        # Purpose: To provide access to logs everywhere without another import
        # returns a logger instance
        # usage: self.log.debug('foo')
        if not self.__class__._logger:
            self.__class__._logger = logging.getLogger(__name__)
        return self.__class__._logger

    @classmethod
    def get_timestamp(cls, time_to_format=None):
        # Purpose: To have a standardized timestamp for anything that needs it.
        # Optionally takes a datetime value, or uses now.
        # Returns: yymmdd_hhmmss.xxxxxx as string
        if time_to_format is None:
            time_to_format = datetime.datetime.now()
        return time_to_format.strftime("%Y%m%d_%H%M%S.%f")

    #######################################################################
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
        # Purpose: Perform f-string style substitutions without errors for missing keys, and using
        #          sources like global test data or other dicts to feed the substitution engine
        # Inputs: - (str)in_string - the string to do substitutions on
        #         - dict or list of dict - items to use for substitution

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

    #######################################################################
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

    #######################################################################
    @staticmethod
    def _remove_keys(incoming_dict, list_of_keys=None):
        # Purpose: Remove keys from kwargs before passing them on. For instance, most webdriver
        #          calls do not accept timeout as a keyword.
        # Inputs: - (dict)incoming_dict: a kwargs style dict
        #         - (list or set)list_of_keys: keys to remove
        # Returns: a copy of the dict with the noted keys removed
        modified_dict = dict(incoming_dict)  # make me a shallow copy
        list_of_keys = [] if not list_of_keys else list_of_keys
        for key in list_of_keys:
            if key in modified_dict:
                del (modified_dict[key])
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

    @staticmethod
    def timeout_remaining(end_time=None, timeout=0, minimum=1):
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


