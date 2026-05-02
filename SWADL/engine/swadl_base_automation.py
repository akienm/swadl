"""
File: swadl_base_automation.py
Purpose: Base class for non-test process automation. Provides driver +
         page/flow plumbing without unittest test-runner glue.

Use this when you want SWADL's automation power but you're NOT running a
unittest/pytest test — e.g. driving Gmail for real, automating a Windows
app via pywinauto, scripting a chat UI for an agent. For tests, use
SWADLTest, which inherits from this class and adds the test-runner
machinery.

Pattern:
    class GmailReader(SWADLBaseAutomation):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.inbox_page = GmailInboxPage()

        def fetch_unread(self):
            self.inbox_page.load_page()
            return [...]

    with GmailReader() as reader:
        msgs = reader.fetch_unread()
    # browser quits automatically on context exit
"""

from SWADL.engine.swadl_base import SWADLBase
from SWADL.engine.swadl_cfg import _quit_driver_if_running, cfgdict
from SWADL.engine.swadl_constants import TEST_OBJECT


class SWADLBaseAutomation(SWADLBase):
    # Purpose: Non-test automation root — driver + plumbing, no unittest glue.

    accumulated_failures = None
    # Purpose: Collects non-fatal validation results from
    # _assertion_post_processor. Lives here (not just in SWADLTest) so
    # non-test automation can also gather expect_*/require_* findings.

    def __init__(self, name=None, **kwargs):
        # Auto-name from class if not provided. Automation roots usually
        # don't need an explicit name keyword — different from page sections,
        # which Akien's convention names explicitly.
        if name is None:
            name = self.__class__.__name__
        SWADLBase.__init__(self, name=name, **kwargs)

        self.parent = None
        self.accumulated_failures = []

        # Make this automation root the TEST_OBJECT so accumulated_failures
        # routing in SWADLBase._assertion_post_processor lands here, not on
        # a None reference. SWADLTest overrides this anyway with itself.
        self.test_data[TEST_OBJECT] = self
        cfgdict[TEST_OBJECT] = self

    def quit(self):
        # Purpose: Explicit cleanup — quit the driver if one was created.
        # Safe to call when no driver exists (no-op).
        _quit_driver_if_running()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()
        return False
