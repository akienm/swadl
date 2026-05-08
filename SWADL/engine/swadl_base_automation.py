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

from __future__ import annotations

from pathlib import Path

from SWADL.engine.swadl_base import SWADLBase
from SWADL.engine.swadl_cfg import _quit_driver_if_running, cfgdict
from SWADL.engine.swadl_constants import TEST_OBJECT

_DEFAULT_LOG_ROOT = Path("swadl_logs")


class SWADLBaseAutomation(SWADLBase):
    # Purpose: Non-test automation root — driver + plumbing, no unittest glue.

    accumulated_failures = None
    # Purpose: Collects non-fatal validation results from
    # _assertion_post_processor. Lives here (not just in SWADLTest) so
    # non-test automation can also gather expect_*/require_* findings.

    _tagged_logger = None

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

    # ── Performance stopwatch ─────────────────────────────────────────────

    @property
    def logger(self):
        """Tagged loguru proxy. self.logger.perf('msg') logs with tag=perf."""
        if self.__class__._tagged_logger is None:
            from diagnostic_base.tagged_logger import TaggedLogger

            self.__class__._tagged_logger = TaggedLogger()
        return self.__class__._tagged_logger

    def stopwatch(
        self,
        stopwatch_id: str,
        *,
        comment: str = "",
        log_root: Path | None = None,
    ):
        """Return a Stopwatch bound to this automation class.

        Usage:
            with self.stopwatch("load_page") as t:
                self.load_page()
        """
        from diagnostic_base.perf import Stopwatch

        return Stopwatch(
            stopwatch_id,
            device_id=type(self).__name__.lower(),
            class_name=type(self).__name__,
            comment=comment,
            log_root=log_root or _DEFAULT_LOG_ROOT,
        )

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def quit(self):
        # Purpose: Explicit cleanup — quit the driver if one was created.
        # Safe to call when no driver exists (no-op).
        _quit_driver_if_running()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()
        return False
