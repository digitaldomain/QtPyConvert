#!/usr/bin/env python
import os, sys
import unittest

from qt_py_convert import coroutines

TEST_CODE_REL_PATH = "sources/normalize_namespaces_test_code.py"


class TestNoOpExample(unittest.TestCase):

    def setUp(self):
        source_path = os.path.abspath(TEST_CODE_REL_PATH)
        with open(source_path, "rb") as fh:
            self.lines = fh.readlines()

    def test_example(self):
        """ Demonstrate running the test and some ways to assert results """

        # Initialize coroutine objects
        no_op_example = coroutines.example_coroutine()
        next(no_op_example)  # Start the coroutine to prime it to the first yield

        for line_num, line in enumerate(self.lines):
            # Remove new line character
            line = line.strip("\n")

            # Prove this line is longer than 25 before passing to the coroutine
            if line_num == 2:
                self.assertEquals(len(line), 72)

            line_num, text = no_op_example.send((line_num, line))

            # print "{:<5}| {}".format(line_num, text)

            # Prove all lines are 25 characters or less
            self.assertTrue(len(text) < 26)

            # Prove this exact line was longer and is now cropped to 25 (orig state tested above)
            if line_num == 2:
                self.assertTrue(len(text) == 25)


if __name__ == '__main__':
    unittest.main()
