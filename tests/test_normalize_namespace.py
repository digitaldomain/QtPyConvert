#!/usr/bin/env python

import os, sys
import unittest

from qt_py_convert import normalize_namespace

TEST_CODE_REL_PATH = "sources/normalize_namespaces_test_code.py"


class TestNamespaceReplace(unittest.TestCase):

    def test_replace(self):
        source_path = os.path.abspath(TEST_CODE_REL_PATH)
        result = normalize_namespace.do(source_path)



if __name__ == '__main__':
    unittest.main()
