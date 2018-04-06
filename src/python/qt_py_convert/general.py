# Copyright 2018 Digital Domain 3.0
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
"""
general is utility functions for the qt_py_convert library
"""
import copy
import json
import os
import re

from qt_py_convert.color import ANSI, color_text
from qt_py_convert.diff import highlight_diffs
from qt_py_convert.log import get_logger
from qt_py_convert.external import Qt

GENERAL_LOGGER = get_logger("general", name_color=ANSI.colors.green)


class WriteFlag(object):
    WRITE_TO_FILE = 0b0001
    WRITE_TO_STDOUT = 0b0010


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
            color_text(color=ANSI.colors.orange, text="WARNING:") +
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
__supported_bindings__ = Qt._QT_PREFERRED_BINDING_DEFAULT_ORDER
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


def supported_binding(binding_str):
    bindings_by_length = [
        re.escape(binding)
        for binding in sorted(__supported_bindings__, reverse=True)
    ]
    match = re.match(
        r"^(?P<binding>{bindings})(:?\..*)?".format(
            bindings="|".join(bindings_by_length)
        ),
        binding_str
    )
    if match:
        return match.groupdict().get("binding")
    return None


def is_py(path):
    """
    My helper method for process_folder to decide if a file is a python file
    or not.
    It is currently checking the file extension and then falling back to
    checking the first line of the file.

    :param path: The filepath to the file that we are querying.
    :type path: str
    :return: True if it's a python file. False otherwise
    :rtype: bool
    """
    if path.endswith(".py"):
        return True
    elif not os.path.splitext(path)[1] and os.path.isfile(path):
        with open(path, "rb") as fh:
            if "python" in fh.readline():
                return True
    return False


def build_exc(error, line_data):
    """
    raises a UserInputRequiredException from an instance of an ErrorClass.

    :param error: The ErrorClass instance that was created somewhere in
        qt_py_convert.
    :type error: qt_py_convert.general.ErrorClass
    :param line_data: List of lines from the file we are working on.
    :type line_data: List[str...]
    """
    line_no_start = error.row
    line_no_end = error.row_to + 1
    lines = line_data[line_no_start:line_no_end]
    line = "".join(line_data[line_no_start:line_no_end])

    line_no = "Line"
    if len(lines) > 1:
        line_no += "s "
        line_no += "%d-%d" % (line_no_start + 1, line_no_end)
    else:
        line_no += " %d" % (line_no_start + 1)

    template = """
{line_no}
{line}
{reason}
"""
    raise UserInputRequiredException(color_text(
        text=template.format(
            line_no=line_no,
            line=color_text(text=line.rstrip("\n"), color=ANSI.colors.gray),
            reason=color_text(text=error.reason, color=ANSI.colors.red),
        ),
        color=ANSI.colors.red,
    ))
