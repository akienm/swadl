
from collections import OrderedDict

from SWADL.engine.bannerizer import bannerize


class SWADLDict(OrderedDict):
    # Purpose: The OrderedDict means that because items will show in the order they
    # were created, we can use the dict to also show the order of things. So banners
    # for validations can list their most important things at the top, for instance.

    def __init__(self, **kwargs):
        # Purpose: Mostly to allow arguments to be specified at creation time
        # and sucked up at that point.
        super().__init__()
        self.update(kwargs)

    def set(self, key, value):
        # Purpose: There wasn't a set()?! Really?!
        self[key] = value

    def dump(self):
        # Purpose: So we can examine the bannerized data during debugging
        result = bannerize(data=self)
        # NOTE: Since this is only for debugging, this is the one place print is allowed - AMM
        print(result)
        return result
