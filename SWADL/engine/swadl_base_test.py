# File: SWADLtest
# Purpose: pytest/unittest test base — inherits SWADLBaseAutomation and adds
#          test-runner glue (FAILURE_LOG, RESULT_LOG, accumulated_failures
#          assertion in tearDown, auto driver-quit on tearDown).
#
# For non-test automation (Gmail flows, real product use, agent-driven
# scripting), use SWADLBaseAutomation directly — no unittest dependency.

import unittest

from SWADL.engine.swadl_base_automation import SWADLBaseAutomation
from SWADL.engine.swadl_cfg import cfgdict
from SWADL.engine.swadl_constants import FAILURE_LOG
from SWADL.engine.swadl_constants import RESULT_LOG
from SWADL.engine.swadl_constants import TEST_NAME
from SWADL.engine.swadl_constants import TEST_OBJECT
from SWADL.engine.swadl_output import Output


class SWADLTest(unittest.TestCase, SWADLBaseAutomation):
    # Purpose: Test base — BaseAutomation + unittest test-runner glue.
    # Adds: FAILURE_LOG/RESULT_LOG creation, tearDown that asserts no
    # accumulated failures and quits the driver to prevent browser leaks.

    def __init__(self, *args, **kwargs):
        # First, finish initializing the unittest component
        unittest.TestCase.__init__(self, *args, **kwargs)

        # Extract the test name (Nose2/pytest format)
        extracted_name = self.__str__()
        parts = extracted_name.split(" ")
        name = parts[1][1:-1]
        cfgdict[TEST_NAME] = name  # makes the test name available everywhere

        # Initialize BaseAutomation (sets self.test_data[TEST_OBJECT] = self,
        # self.accumulated_failures = [], etc.)
        SWADLBaseAutomation.__init__(self, name=name)

        # Test-runner reporting setup — only for actual tests, not for
        # general automation, hence kept here and not in BaseAutomation.
        cfgdict[FAILURE_LOG] = Output(
            file_name="test_failures.log",
            comment=f"for {self.get_name()}",
            name=FAILURE_LOG,
        )
        cfgdict[RESULT_LOG] = Output(
            file_name="test_results.log",
            comment=f"for {self.get_name()}",
            name=RESULT_LOG,
        )

    def setUp(self):
        # Purpose: Sets up the test
        super().setUp()

    def tearDown(self):
        # Purpose: Clean up all the things and ensure no browser leaks.
        cfgdict[FAILURE_LOG].close(f"for {self.get_name()}")
        cfgdict[RESULT_LOG].close(f"for {self.get_name()}")
        super().tearDown()
        self.log.debug(self.bannerize(data=self.cfgdict))
        self.assert_true(exper=len(self.accumulated_failures) == 0)
        # Always quit the driver — prevents the orphan-browser leak that
        # used to happen when driver creation lived at module-import time.
        self.quit()
