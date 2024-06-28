
from collections import OrderedDict

from SWADL.engine.swadl_utils import bannerize


class SWADLDict(OrderedDict):
    def __init__(self, **kwargs):
        self.update(kwargs)

    def set(self, key, value):
        self[key] = value

    def dump(self):
        result = bannerize(data=self)
        # max_width = 0
        # for key in self.keys():
        #     current_key_len = len(key)
        #     if current_key_len > max_width:
        #         max_width = current_key_len
        # max_width += 2
        # dots = '.' * max_width
        # result = ""
        # for key, value in self.items():
        #     result += f"{(key + dots)[:max_width]}: {value}\n"

        # NOTE: Since this is only for debugging, this is the one place print is allowed - AMM
        print(result)
        return result
