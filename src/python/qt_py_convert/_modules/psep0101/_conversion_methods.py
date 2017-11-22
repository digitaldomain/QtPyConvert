import re


def to_methods(function_str):
    """
    to_methods is a helper function that aims to replace all the "toX" methods
    from PyQt4-apiV1.0.

    :param function_str: String that represents something that may have the
        toX methods in it.
    :type function_str: str
    :return: A string that, if a method was found, has been cleaned.
    :rtype: str
    """
    match = re.match(
        r"""
(?P<object>.*?)                                       # Whatever was before it.
\.to(?:                                               # Get all the options of.
    String|                                           # toString
    Int|                                              # toInt
    Bool|                                             # toBool
    PyObject                                          # toPyObject
)\(.*?\)(?P<end>.*)""",
        function_str,
        re.VERBOSE | re.MULTILINE
    )
    if match:
        replacement = match.groupdict()["object"]
        replacement += match.groupdict()["end"]
        return replacement
    return function_str
