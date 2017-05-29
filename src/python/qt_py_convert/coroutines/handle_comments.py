# No shebang line. This module is meant to be imported
""" Fix comments and doc strings """
import tokenize


def handle_comments_coroutine():
    """ Return the first 25 characters of each line """
    # Initialize all state and send() arguments
    line_num = ""
    line = ""
    line_text = ""

    continue_comment = False
    while True:
        line_num, line = yield line_num, line

