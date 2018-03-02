"""
general is utility functions for the qt_py_convert library
"""
import copy
import json
import os

from qt_py_convert.color import ANSI, color_text, highlight_diffs
from qt_py_convert.log import get_logger
from qt_py_convert.external import Qt

GENERAL_LOGGER = get_logger("general", name_color=ANSI.colors.green)


class WriteMode(object):
    STDOUT = 1
    RELATIVE_ROOT = 2
    OVERWRITE = 3


def change(logger, node, replacement, skip_lineno=False, msg=None):
    """
    A helper function to print information about replacing a node.

    :param logger: A python logger
    :type logger: logger.Logger
    :param node: Redbaron node that you are going to replace.
    :type node: redbaron.node
    :param replacement: Replacement string.
    :type replacement: str
    :param skip_lineno: Skip lineno flag.
    :type skip_lineno: bool
    :param msg: Optional custom message to write out.
    :type msg: None|str
    :return: Returns the result of the handler.
    :rtype: None
    """
    failure_message = (
            color_text(color=ANSI.colors.red, text="ERROR:") +
            " Could not replace \"{original}\" with \"{replacement}\""
    )
    if msg is None:
        msg = "Replacing \"{original}\" with \"{replacement}\""

    _orig = str(node).strip("\n")
    _repl = replacement
    original, replacement = highlight_diffs(_orig, _repl)
    if not skip_lineno:
        msg += " at line {line}"
        if not hasattr(node, "absolute_bounding_box"):
            msg = failure_message
            line = "N/A"
        else:
            line = node.absolute_bounding_box.top_left.line - 1

    result = logger.debug(
            msg.format(**locals())
        )
    if msg == failure_message:
        result = 1
    return result


# Default binding support out of the box.
__supported_bindings__ = Qt._misplaced_members.keys()
__suplimentary_bindings__ = ["sip", "shiboken"]
# Adding support for custom bindings.
CUSTOM_MISPLACED_MEMBERS = "QT_CUSTOM_MISPLACED_MEMBERS"
_custom_bindings = os.environ.get("QT_CUSTOM_BINDINGS_SUPPORT")
if _custom_bindings:
    GENERAL_LOGGER.debug(
        "Found Custom Bindings. Adding: {bindings}".format(
            bindings=_custom_bindings.split(os.pathsep)
        )
    )
    __supported_bindings__ += _custom_bindings.split(os.pathsep)

# Note: Pattern here is a little more complex than needed to make the
#       print lines optional.
_custom_misplaced_members = {}
misplaced_members_python_str = os.environ.get(CUSTOM_MISPLACED_MEMBERS)
if misplaced_members_python_str:
    GENERAL_LOGGER.debug(
        "{} = {0!r}".format(
            CUSTOM_MISPLACED_MEMBERS, misplaced_members_python_str
        )
    )

    _custom_misplaced_members = json.loads(misplaced_members_python_str)

    # Colored green
    GENERAL_LOGGER.debug(color_text(
        text="Resolved {} to json: {0!r}".format(
            CUSTOM_MISPLACED_MEMBERS, _custom_misplaced_members
        ),
        color=ANSI.colors.green
    ))


class ErrorClass(object):
    """
    ErrorClass is a structured data block that represents a problem with the
    converted file that cannot be automatically fixed from qy_py_convert.

    It takes a redbaron node and a str to describe why it can't be fixed.
    """
    def __init__(self, node, reason):
        """
        :param node: Redbaron node that can't be fixed.
        :type node: redbaron.Node
        :param reason: Reason that the thing cannot be fixed.
        :type reason: str
        """
        super(ErrorClass, self).__init__()
        bbox = node.absolute_bounding_box

        self.row = bbox.top_left.line - 1
        self.row_to = bbox.bottom_right.line - 1
        self.reason = reason
        ALIAS_DICT["errors"].add(self)


class UserInputRequiredException(BaseException):
    """
    UserInputRequiredException is an exception that states that the user is
    required to make the fix. It is used to alert the user to issues.
    """


class AliasDictClass(dict):
    """
    Global state data store
    """
    BINDINGS = "bindings"
    ALIASES = "root_aliases"
    USED = "used"
    WARNINGS = "warnings"
    ERRORS = "errors"

    def __init__(self):
        super(AliasDictClass, self).__init__(
            dict([
                (self.BINDINGS, set()),
                (self.ALIASES, set()),
                (self.USED, set()),
                (self.WARNINGS, set()),
                (self.ERRORS, set()),
            ])
        )

    def clean(self):
        """clean will reset the AliasDict global object."""
        GENERAL_LOGGER.debug(color_text(
            text="Cleaning the global AliasDict",
            color=ANSI.colors.red
        ))
        self[self.BINDINGS] = set()
        self[self.ALIASES] = set()
        self[self.USED] = set()
        self[self.WARNINGS] = set()
        self[self.ERRORS] = set()


ALIAS_DICT = AliasDictClass()


def merge_dict(lhs, rhs, keys=None, keys_both=False):
    """
    Basic merge dictionary function. I assume it works, I haven't looked at
    it for eons.

    :param lhs: Left dictionary.
    :type lhs: dict
    :param rhs: Right dictionary.
    :type rhs: dict
    :param keys: Keys to merge.
    :type keys: None|List[str...]
    :param keys_both: Use the union of the keys from both?
    :type keys_both: bool
    :return: Merged dictionary.
    :rtype: dict
    """
    out = {}
    lhs = copy.copy(lhs)
    rhs = copy.copy(rhs)
    if not keys:
        keys = lhs.keys()
        if keys_both:
            keys.extend(rhs.keys())
    for key in keys:
        if key not in rhs:
            rhs[key] = type(lhs[key])()
        if key not in lhs:
            lhs[key] = type(rhs[key])()
        if isinstance(lhs[key], set):
            op = "union"
        elif isinstance(lhs[key], str):
            op = "__add__"
        else:
            op = None
        if op:
            out[key] = getattr(lhs[key], op)(rhs[key])
        # out[key] = lhs[key].union(rhs[key])
    return out
