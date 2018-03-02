import re

from qt_py_convert.general import ALIAS_DICT, ErrorClass


class Processes(object):

    @staticmethod
    def _process_load_ui_type(red, objects, skip_lineno=False):
        for node in objects:
            ErrorClass(
                node=node,
                reason="""
    The Qt.py module does not support uic.loadUiType as it is not a method in PySide.
    Please see: https://github.com/mottosso/Qt.py/issues/237
        For more information. 

    This will break and you will have to update this or refactor it out."""
            )

    LOADUITYPE_STR = "LOADUITYPE"
    LOADUITYPE = _process_load_ui_type


def unsupported_process(store):
    """
    unsupported_process is one of the more complex handlers for the _modules.

    :param store: Store is the issues dict defined in "process"
    :type store: dict
    :return: The filter_function callable.
    :rtype: callable
    """
    _loaduitype_expression = re.compile(
        r"(?:uic\.)?loadUiType", re.DOTALL
    )

    def filter_function(value):
        """
        filter_function takes an AtomTrailersNode or a DottedNameNode and will
        filter them out if they match something that is unsupported in Qt.py
        """
        found = False
        if _loaduitype_expression.search(value.dumps()):
            store[Processes.LOADUITYPE_STR].add(value)
            found = True
        if found:
            return True
    return filter_function


def process(red, skip_lineno=False, **kwargs):
    """
    process is the main function for the import process.

    :param red: Redbaron ast.
    :type red: redbaron.redbaron
    :param skip_lineno: An optional performance flag. By default, when the
        script replaces something, it will tell you which line it is
        replacing on. This can be useful for tracking the places that
        changes occurred. When you turn this flag on however, it will not
        show the line numbers. This can give great performance increases
        because redbaron has trouble calculating the line number sometimes.
    :type skip_lineno: bool
    :param kwargs: Any other kwargs will be ignored.
    :type kwargs: dict
    """
    issues = {
        Processes.LOADUITYPE_STR: set(),
    }

    red.find_all("AtomTrailersNode", value=unsupported_process(issues))
    red.find_all("DottedNameNode", value=unsupported_process(issues))
    key = Processes.LOADUITYPE_STR

    if issues[key]:
        return getattr(Processes, key)(red, issues[key],
                                       skip_lineno=skip_lineno)
    else:
        return ALIAS_DICT, {}
