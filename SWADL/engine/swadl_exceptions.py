class SWADLFrameworkError(Exception):
    pass


class SWADLTestError(Exception):
    pass


class SWADLStaleElementError(Exception):
    # Raised by driver adapters when an element reference goes stale.
    # Caught by _retry_until_expected_met to trigger a refresh and retry.
    pass
