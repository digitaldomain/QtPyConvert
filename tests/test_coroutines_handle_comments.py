#!/usr/bin/env python
import os
import unittest

from qt_py_convert import coroutines


TEST_CODE_REL_PATH = "sources/test_code.py"


class TestCoroutinesHandleComments(unittest.TestCase):

    def setUp(self):
        source_path = os.path.abspath(TEST_CODE_REL_PATH)
        with open(source_path, "rb") as fh:
            self.lines = fh.readlines()

    def test_example(self):
        """ Demonstrate running the test and some ways to assert results """

        # Initialize coroutine objects
        handle_comments = coroutines.handle_comments_coroutine()
        next(handle_comments)  # Start the coroutine to prime it to the first yield

        for line_num, line in enumerate(self.lines):

            line_num, text = handle_comments.send((line_num, line))

            print "{:<5}| {}".format(line_num, text)


if __name__ == '__main__':
    unittest.main()
