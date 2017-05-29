#!/tools/bin/python2.7
""" Main processor functions """
import re

from qt_py_convert.coroutines import handle_comments_coroutine

# No shebang line. This module is meant to be imported
import dd.runtime.api
dd.runtime.api.load("qt_py")
from Qt import _common_members


# TODO: Add test module
def process_file(path, dry_run=True):
    """
    do is the main entry point/driver for this module of the qt_py_convert tool.

    :param str path:
        File path to process
    :param bool dry_run:
        If True, print action instead of taking action (nothing is done)
    """
    with open(path, "rb") as fh:
        lines = fh.readlines()

    comments_handler = handle_comments_coroutine()
    next(comments_handler)

    # Note: Do noth redefine these. We want the original line number and line text for reporting.
    for line_num, line in enumerate(lines):

        line_num, code_text = comments_handler.send((line_num, line))
        print line_num, "|", code_text


