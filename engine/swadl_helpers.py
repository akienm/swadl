# File: SWADLhelpers.py
# Purpose: "everything else"

import datetime


def get_timestamp():
    # Method: get_timestamp
    # Purpose: To have a standardized timestamp for anything that needs it.
    # Returns: yymmdd_hhmmss.xxxxxx as string
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S.%f")
