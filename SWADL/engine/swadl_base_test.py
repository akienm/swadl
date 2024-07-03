# File: SWADLtest
# Purpose: to report errors on exit

from pprint import pformat
import unittest

from SWADL.engine.swadl_base import SWADLBase
from SWADL.engine.swadl_cfg import cfgdict
from SWADL.engine.swadl_constants import FAILURE_LOG, TEST_OBJECT, TEST_DATA
from SWADL.engine.swadl_constants import RESULT_LOG
from SWADL.engine.swadl_constants import TEST_NAME
from SWADL.engine.swadl_output import Output


class SWADLTest(unittest.TestCase, SWADLBase):
    # Purpose: to raise an assertion on exit if there have been failures

    accumulated_failures = None
    # This is used for non-fatal failures related to this test.
    # Control objects can add entries that are non-fatal validations
    # as well as non-fatal assertions. this is used in the
    # tearDown method

    def __init__(self, *args, **kwargs):
        # Set me up!
        # First, finish initalizing the unittest component
        unittest.TestCase.__init__(self, *args, **kwargs)

        # now extract the test name
        # This works for Nose2, it is unknown as of this writing whether it will work for pytrest
        extracted_name = self.__str__()
        parts = extracted_name.split(" ")
        self.name = parts[1][1:-1]
        cfgdict[TEST_NAME] = self.name  # and this makes the test name available everywhere

        # Now init the swadl part
        SWADLBase.__init__(self, *args, **kwargs)

        # Things that swadl needs tests to have
        self.parent = None  # because tests don't need one
        self.test_data[TEST_OBJECT] = self


        # and now, if all of that passed, let's initialize the csv output
        # TODO: Move this to a new module that will handle reporting
        # to allow other frameworks to make use of this without it
        # being a whole framework unto itself that none other may do differ't
        cfgdict[FAILURE_LOG] = Output(
            file_name='test_failures.log',
            comment=f"for {self.get_name()}",
            name=FAILURE_LOG,
        )
        cfgdict[RESULT_LOG] = Output(
            file_name='test_results.log',
            comment=f"for {self.get_name()}",
            name=RESULT_LOG,
        )

    def setUp(self):
        # Purpose: Sets up the test
        super().setUp()

    def tearDown(self):
        # Purpose: Clean up all the things
        cfgdict[FAILURE_LOG].close(f"for {self.get_name()}")
        cfgdict[RESULT_LOG].close(f"for {self.get_name()}")
        super().tearDown()
        print(self.bannerize(data=self.__dict__, title='test object'))
        assert not self.accumulated_failures, pformat(self.accumulated_failures)
