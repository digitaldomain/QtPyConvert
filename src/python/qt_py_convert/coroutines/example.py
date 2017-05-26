"""
Example of the coroutine co-routine pattern. Run like::

    def do(path):
        with open(path, "rb") as fh:
            lines = fh.readlines()

        # Initialize coroutine objects
        no_op_example = no_op_example_coroutine()
        next(no_op_example)  # Start the coroutine to prep the first yeild

        for line_num, line in enumerate(lines):

            line_num, text = no_op_example.send((line_num, line))

            print line_num, "|",text

"""


def no_op_example_coroutine():
    # Initialize all state and send() arguments
    line_num = ""
    line = ""
    while True:
        line_num, line = yield line_num, line

