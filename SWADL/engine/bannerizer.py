# File: SWADLhelpers.py
# Purpose: "everything else"

import datetime
import json

import SWADL
from SWADL.engine.swadl_constants import TEST_DATA




OBJECT_ALREADY_DISPLAYED = '*** OBJECT ALREADY DISPLAYED ABOVE ***'
indents = 4


class Bannerize:

    def __init__(self):
        self.indent = 0
        self.final_result = ''
        self.indent_char = ' '
        self.list_of_completed_objects = []
        self.types_that_got_substituted = []
        self.types_to_treat_as_string = (bool, str, int, tuple, float)

    def ind(self, data):
        return (self.indent * self.indent_char) + data

    def check_for_dupes(self, item, key=None):
        # make into function? Have to use this above too...

        key_string = ""
        if key:
            key_string = f'KEY: "{key}" '

        str_item = f'{item}'
        str_item = str_item[:100]
        if item is not None:
            if not isinstance(item, self.types_to_treat_as_string):
                item_id_string = f"{id(item)} {item}"
                if item_id_string in self.list_of_completed_objects:
                    self.types_that_got_substituted.append(item_id_string)
                    item = OBJECT_ALREADY_DISPLAYED
                else:
                    self.list_of_completed_objects.append(item_id_string)
        return item

    def bannerize(self, data=None, iteration=0):
        iteration += 1
        if isinstance(data, dict):
            if len(data.keys()) > 0:
                self.final_result += '{\n'
                self.indent += indents
                for key, item in data.items():
                    self.final_result += self.ind(f'"{key}": ')
                    item = self.check_for_dupes(item, key=key)
                    self.bannerize(data=item, iteration=iteration)
                self.indent -= indents
                self.final_result += self.ind('}\n')
            else:
                self.final_result += '{}}\n'
        elif isinstance(data, list):
            if len(data) > 0:
                self.final_result += '[\n'
                self.indent += indents
                for item in data:
                    item = self.check_for_dupes(item)
                    self.final_result += self.ind('')
                    self.bannerize(data=item, iteration=iteration)
                self.indent -= indents
                self.final_result += self.ind(']')
                self.final_result += '\n'
            else:
                self.final_result += '[]\n'
        else:
            if isinstance(data, str):
                if not data == OBJECT_ALREADY_DISPLAYED:
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
    bannerizer.bannerize(data)
    return bannerizer.final_result

