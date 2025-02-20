# File: SWADLoutput
# Purpose: To produce a simplified output files of test results and failures

import os

from SWADL.engine.swadl_base import SWADLBase


class Output(SWADLBase):
    # Purpose: A write only logging mechanism to output test results to files instead of the
    #          console.

    # Datum: writing_started
    # Purpose: To determine whether or not we need to push the start time into the log
    writing_started = False

    # Datum: writing_done
    # Purpose: To determine if we're shutting down and we should ignore anything else
    writing_done = False

    def __init__(self, file_name, comment='', name=None):
        # Purpose: Store the filename
        # Inputs: - str:file_name
        self.name = name
        SWADLBase.__init__(self, file_name=file_name, comment=comment, name=name)
        self.file_name = file_name
        if os.path.exists(self.file_name):
            os.remove(self.file_name)
        if not self.writing_started:
            self.writing_started = True
            self.add(f"Started {file_name} {comment}")

    def add(self, stuff_to_add):
        # Purpose: Takes a string or collection of strings and adds them to the file
        # Inputs: - (list, tuple, str):stuff_to_add - the things to be added
        if not self.writing_done:
            if not isinstance(stuff_to_add, (list, tuple)):
                stuff_to_add = [stuff_to_add]
            with open(self.file_name, "a", encoding='utf-8') as handle:
                for line in stuff_to_add:
                    handle.write(f'{self.get_timestamp()}::{line}\n')

    def close(self, comment=''):
        # Purpose: Write and end point into the log
        if not self.writing_done:
            self.add(f"Done test_failures.log {comment}")
            self.writing_done = True

    def __del__(self):
        # Purpose: Close the log
        self.close()
