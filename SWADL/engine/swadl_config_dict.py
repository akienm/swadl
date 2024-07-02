"""
File: SWADLconfig_dict.py
Purpose: Master global configuration dictionary
"""

import logging
from SWADL.engine.swadl_dict import SWADLDict

logger = logging.getLogger(__name__)


class ConfigDict(SWADLDict):
    # Purpose: To provide a singleton for configuration information.

    _instance = None

    def __new__(cls, *args, **kwargs):
        # Purpose: Replaces dunder method that returns the instance
        if cls._instance is None:
            cls._instance = SWADLDict()
        cls._instance.update(**kwargs)
        return cls._instance


class TestConfigDict:
    # Purpose: Unit tests for ConfigDict. Intended for pytest

    def test_ConfigDict(self):
        # Purpose: Validate that singleton works
        a = ConfigDict(a=1)
        b = ConfigDict(b=2)
        c = ConfigDict(c=3)
        d = a
        d = b
        d = c
        assert d['a'] == 1
        assert d['b'] == 2
        assert d['c'] == 3
        assert str(d) == "{'a': 1, 'b': 2, 'c': 3}"
        print("test_ConfigDict: PASSED")
