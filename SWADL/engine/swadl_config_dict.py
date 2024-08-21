"""
File: SWADLconfig_dict.py
Purpose: Master global configuration dictionary
"""

from SWADL.engine.swadl_dict import SWADLDict


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

    def test_config_dict(self):
        # Purpose: Validate that singleton works
        a = ConfigDict(a=1)
        d = a
        assert d['a'] == 1
        b = ConfigDict(b=2)
        d = b
        assert d['b'] == 2
        c = ConfigDict(c=3)
        d = c
        assert d['c'] == 3
        assert str(d) == "{'a': 1, 'b': 2, 'c': 3}"
        print("test_ConfigDict: PASSED")
