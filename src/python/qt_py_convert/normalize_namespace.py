#!/tools/bin/python2.7

import re

import dd.runtime.api
dd.runtime.api.load("qt_py")
from Qt import _common_members


def do(path, dry_run=True):
    """
    do is the main entry point/driver for this module of the qt_py_convert tool.

    :param str path:
        File path to process
    :param bool dry_run:
        If True, print action instead of taking action (nothing is done)
    """
    with open(path, "rb") as fh:
        lines = fh.readlines()

    no_op_example = no_op_example_coroutine()
    next(no_op_example)

    for line_num, line in enumerate(lines):

        line_num, text = no_op_example.send((line_num, line))
        print line_num, "|",text

        # comments_handler = comments_handler_coroutine()

        # line_num, code_text, comment_text = handle_comments(lines)
        # print line_num, "|", code_text, " -- comment text:", comment_text

def do(path, dry_run=True):
    """
    do is the main entry point/driver for this module of the qt_py_convert tool.

    :param str path:
        File path to process
    :param bool dry_run:
        If True, print action instead of taking action (nothing is done)
    """
    with open(path, "rb") as fh:
        lines = fh.readlines()

    no_op_example = no_op_example_coroutine()
    next(no_op_example)

    for line_num, line in enumerate(lines):

        line_num, text = no_op_example.send((line_num, line))
        print line_num, "|",text

def no_op_example_coroutine():
    line_num = line = ""
    while True:
        line_num, line = yield line_num, line


def comments_handler_coroutine(lines):
    """

    """
    continue_comment = False
    result_lines = []
    for line_num, line_text in enumerate(lines):
        # print line_num, line_text

        test_text = line_text.strip()

        # Skip comments and if opening a block comment, track it to skip next lines
        for block_quote in [r'"""', r"'''"]:
            if block_quote in line_text:
                chunks = test_text.split(block_quote)

                test_text = chunks[0]

                if not len(chunks) % 2:
                    continue_comment = not continue_comment

                break

        if continue_comment or not test_text:
            continue

        # Ignore anything after a comment
        test_text = test_text.split("#")[0]

        if test_text:
            result_lines.append((line_num, test_text))

    return result_lines
