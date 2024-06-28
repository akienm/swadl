# File: SWADLhelpers.py
# Purpose: "everything else"

import datetime
import json

import SWADL
from SWADL.engine.swadl_constants import TEST_DATA


def get_timestamp():
    # Purpose: To have a standardized timestamp for anything that needs it.
    # Returns: yymmdd_hhmmss.xxxxxx as string
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S.%f")


class Bannerize:

    indents = 4
    indent = 0
    final_result = ''
    indent_char = ' '
    list_of_completed_objects = []
    types_that_got_substituted = []
    OBJECT_ALREADY_DISPLAYED = '*** OBJECT ALREADY DISPLAYED ABOVE ***'
    types_to_treat_as_string = (bool, str, int, tuple, float)

    def ind(self, data):
        return (self.indent * self.indent_char) + data

    def check_for_dupes(self, item, key=None):
        # make into function? Have to use this above too...

        key_string = ""
        if key:
            key_string = f'KEY: "{key}" '
        if item is SWADL.engine.swadl_cfg.cfgdict[TEST_DATA]:
            print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print(f'!!!!!!!!!! {key_string}item is test_data! !!!!!!!!!!')
            print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

        str_item = f'{item}'
        str_item = str_item[:100]
        print(f'***** {key_string}LIST ITEM: {str_item}')
        if item is not None:
            print(f'***** {key_string}item is not none')
            if not isinstance(item, self.types_to_treat_as_string):
                print(f'***** {key_string}item is not stringlike')
                if item in self.list_of_completed_objects:
                    print(f'***** {key_string}item disposition already in list_of_completed_objects')
                    self.types_that_got_substituted.append(item)
                    item = self.OBJECT_ALREADY_DISPLAYED
                else:
                    print(f'***** {key_string}item disposition is added to list_of_completed_objects')
                    self.list_of_completed_objects.append(item)
            print(f'LIST {key_string}ITEM COMPLETE')
        return item

    def bannerize(self, data=None, iteration=0):
        iteration += 1
        if isinstance(data, dict):
            self.final_result += '{\n'
            self.indent += self.indents
            for key, item in data.items():
                self.final_result += self.ind(f'"{key}": ')
                item = self.check_for_dupes(item, key=key)
                self.bannerize(data=item, iteration=iteration)
            self.indent -= self.indents
            self.final_result += self.ind('}\n')
        elif isinstance(data, list):
            self.final_result += '[\n'
            self.indent += self.indents
            for item in data:
                item = self.check_for_dupes(item)
                self.final_result += self.ind('')
                self.bannerize(data=item, iteration=iteration)
            self.indent -= self.indents
            self.final_result += self.ind(']')
            self.final_result += '\n'
        else:
            if isinstance(data, str):
                if not data == self.OBJECT_ALREADY_DISPLAYED:
                    data = f'"{data}"'
            self.final_result += data.__str__()
            self.final_result += '\n'

        iteration -= 1
        if iteration > 20:
            raise Exception(f"infinite loop in bannerizer: {data}")


def bannerize(data, title=None):
    if title:
        data = {title: data}
    bannerizer = Bannerize()
    print("*"*100)
    print("*"*100)
    print("*"*100)
    bannerizer.bannerize(data)
    return bannerizer.final_result

