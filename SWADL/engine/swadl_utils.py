# File: SWADLhelpers.py
# Purpose: "everything else"

import datetime
import json


def get_timestamp():
    # Purpose: To have a standardized timestamp for anything that needs it.
    # Returns: yymmdd_hhmmss.xxxxxx as string
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S.%f")

types_found_list = []
class Bannerize:

    indents = 4
    indent = 0
    final_result = ''
    indent_char = ' '
    list_of_completed_objects = []
    OBJECT_ALREADY_DISPLAYED = '*** OBJECT ALREADY DISPLAYED ABOVE ***'
    types_to_treat_as_string = (bool, str, int, tuple, float)

    def ind(self, data):
        return (self.indent * self.indent_char) + data

    def bannerize(self, data=None, iteration=0):
        iteration += 1
        if isinstance(data, dict):
            self.final_result += '{\n'
            self.indent += self.indents
            for key, item in data.items():
                self.final_result += self.ind(f'"{key}": ')

                # make into function? Have to use this below too...
                if (not isinstance(item, self.types_to_treat_as_string)) and (not item is None):
                    if item in self.list_of_completed_objects:
                        item = self.OBJECT_ALREADY_DISPLAYED
                    else:
                        self.list_of_completed_objects.append(item)

                self.bannerize(data=item, iteration=iteration)
            self.indent -= self.indents
            self.final_result += self.ind('}\n')
        elif isinstance(data, list):
            self.final_result += '[\n'
            self.indent += self.indents
            for item in data:

                # make into function? Have to use this above too...
                if (not isinstance(item, self.types_to_treat_as_string)) and (not item is None):
                    if item in self.list_of_completed_objects:
                        item = self.OBJECT_ALREADY_DISPLAYED
                    else:
                        self.list_of_completed_objects.append(item)

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
    bannerizer.bannerize(data)
    return bannerizer.final_result

