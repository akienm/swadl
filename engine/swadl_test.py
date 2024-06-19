# File: SWADLtest
# Purpose: to report errors on exit

from pprint import pformat
import unittest

from engine.swadl_base import SWADLBase
from engine.swadl_cfg import cfgdict
from engine.swadl_constants import FAILURE_LOG
from engine.swadl_constants import RESULT_LOG
from engine.swadl_constants import TEST_NAME
from engine.swadl_control import accumulated_failures
from engine.swadl_output import Output


class SWADLTest(unittest.TestCase, SWADLBase):
    # Class: SWADLTest
    # Purpose: to raise an assertion on exit if there have been failures

    def setUp(self):
        # Method: setUp()
        # Purpose: Sets up the test
        self.parent = None  # because tests don't need one
        # now extract the test name
        # This works for Nose2, it is unknown as of this writing whether it will work for pytrest
        extracted_name = self.__str__()
        parts = extracted_name.split(" ")
        test_method_name = parts[0]
        file_and_class = parts[1][1:-1]
        self.name = f"{file_and_class}.{test_method_name}"
        cfgdict[TEST_NAME] = self.name  # and this makes the test name available everywhere
        # and now, if all of that passed, let's initialize the csv output
        cfgdict[FAILURE_LOG] = Output(
            file_name='test_failures.log',
            comment=f"for {self.get_name()}",
        )
        cfgdict[RESULT_LOG] = Output(
            file_name='test_results.log',
            comment=f"for {self.get_name()}",
        )

    def tearDown(self):
        # Method: tearDown
        # Purpose: Clean up all the things
        cfgdict[FAILURE_LOG].close(f"for {self.get_name()}")
        cfgdict[RESULT_LOG].close(f"for {self.get_name()}")
        super().tearDown()
        assert not accumulated_failures, pformat(accumulated_failures)
