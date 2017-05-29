#!/usr/bin/env python
import os
import sys
import unittest

from qt_py_convert import process


TEST_CODE_REL_PATH = "sources/test_code.py"


class TestCoroutinesExample(unittest.TestCase):
    """ Test anything that isn't covered by individual coroutines tests """

    def test_process_file(self):

        # TODO: Test things.
        source_path = os.path.abspath(TEST_CODE_REL_PATH)
        result = process.process_file(source_path)


if __name__ == '__main__':
    unittest.main()
