"""
general is utility functions for the qt_py_convert library
"""
import copy
import difflib
import json
import os
import subprocess
import sys


class ANSI(object):
    """ANSI is a namespace object. Useful for passing values into "_color" """
    class colors(object):
        white = 29
        black = 30
        red = 31
        green = 32
        orange = 33
        blue = 34
        purple = 35
        teal = 36
        gray = 37

    class styles(object):
        plain = 0
        strong = 1
        underline = 4
        reversed = 7
        strike = 9


def supports_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                  'ANSICON' in os.environ)
    p = subprocess.Popen(
        ["tput", "colors"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    has_colors = p.communicate()[0].strip("\n")
    try:
        has_colors = int(has_colors)
    except:
        has_colors = False

    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if (not supported_platform or not is_a_tty) and not has_colors:
        return False
    return True


__supports_color = supports_color()


def _color(color=ANSI.colors.white, text="", style=ANSI.styles.plain):
    """
    _color will print the ansi text coloring code for the text.

    :param color: Ansi color code number.
    :type color: int
    :param text: Text that you want colored.
    :type text: str
    :return: The colored version of the text
    :rtype: str
    """
    if not __supports_color:
        return text
    return "\033[%d;%dm%s\033[0m" % (style, color, text)


def _highlight_diffs(start, finish, sep=(".", " ", ",", "(")):
    if not __supports_color:
        return start, finish

    slist = start.split(sep[0])
    flist = finish.split(sep[0])
    seqm = difflib.SequenceMatcher(a=slist, b=flist)
    slist_out = []
    flist_out = []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == "replace":
            slist_intermediate = []
            flist_intermediate = []
            for start_part, finish_part in zip(slist[a0:a1],
                                               flist[b0:b1]):
                spart_repl, fpart_repl = start_part, finish_part
                if len(sep) > 1:
                    spart_repl, fpart_repl = \
                        _highlight_diffs(start_part, finish_part, sep=sep[1:])
                if spart_repl != start_part or fpart_repl != finish_part:
                    slist_intermediate.append(spart_repl)
                    flist_intermediate.append(fpart_repl)
                else:
                    slist_intermediate.append(start_part)
                    flist_intermediate.append(finish_part)

            for sitem, fitem in zip(slist_intermediate, flist_intermediate):
                if sitem != fitem:
                    slist_out.append(_color(
                        color=ANSI.colors.green,
                        text=sitem,
                        style=ANSI.styles.strong
                    ))
                    flist_out.append(_color(
                        color=ANSI.colors.green,
                        text=fitem,
                        style=ANSI.styles.strong
                    ))
                else:
                    slist_out.append(sitem)
                    flist_out.append(fitem)
        elif opcode == "equal":
            slist_out.extend(map(
                lambda x: _color(color=ANSI.colors.gray, text=x),
                slist[a0:a1]
            ))
            flist_out.extend(map(
                lambda x: _color(color=ANSI.colors.gray, text=x),
                flist[b0:b1]
            ))
        elif opcode == "delete":
            slist_out.extend(map(
                lambda x: _color(
                    color=ANSI.colors.green,
                    text=x,
                    style=ANSI.styles.strike
                ),
                slist[a0:a1]
            ))
            flist_out.extend(map(
                lambda x: _color(
                    color=ANSI.colors.green,
                    text=x,
                    style=ANSI.styles.strike),
                flist[b0:b1]
            ))
        else:
            slist_out += slist[a0:a1]
            flist_out += flist[b0:b1]
    return sep[0].join(slist_out), sep[0].join(flist_out)


def _change_verbose(handler, node, replacement, skip_lineno=False, msg=None):
    """
    A helper function to print information about replacing a node.

    :param handler: A handler function, basically something that takes a
        message.
    :type handler: callable
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
            _color(color=ANSI.colors.red, text="ERROR:") +
            " Could not replace \"{original}\" with \"{replacement}\""
    )
    if msg is None:
        msg = "Replacing \"{original}\" with \"{replacement}\""

    _orig = str(node).strip("\n")
    _repl = replacement
    original, replacement = _highlight_diffs(_orig, _repl)
    if not skip_lineno:
        msg += " at line {line}"
        if not hasattr(node, "absolute_bounding_box"):
            msg = failure_message
            line = "N/A"
        else:
            line = node.absolute_bounding_box.top_left.line - 1

    result = handler(
            msg.format(**locals())
        )
    if msg == failure_message:
        result = 1
    return result


# Default binding support out of the box.
__supported_bindings__ = ["PySide2", "PySide", "PyQt5", "PyQt4"]
# Adding support for custom bindings.
_custom_bindings = os.environ.get("QT_CUSTOM_BINDINGS_SUPPORT")
if _custom_bindings:
    print(
        "Found Custom Bindings. Adding: %s"
        % _custom_bindings.split(os.pathsep)
    )
    __supported_bindings__ += _custom_bindings.split(os.pathsep)

# Note: Pattern here is a little more complex than needed to make the
#       print lines optional.
_custom_misplaced_members = {}
misplaced_members_python_str = os.environ.get("QT_CUSTOM_MISPLACED_MEMBERS")
if misplaced_members_python_str:
    print(
        "QT_CUSTOM_MISPLACED_MEMBERS = {0!r}".format(
            misplaced_members_python_str
        )
    )

    _custom_misplaced_members = json.loads(misplaced_members_python_str)

    # Colored green
    print(_color(
        color=ANSI.colors.green,
        text="Resolved QT_CUSTOM_MISPLACED_MEMBERS to json: {0!r}".format(
            _custom_misplaced_members)
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
        AliasDict["errors"].add(self)


class UserInputRequiredException(BaseException):
    """
    UserInputRequiredException is an exception that states that the user is
    required to make the fix. It is used to alert the user to issues.
    """


class AliasDictClass(dict):
    """
    Global state data store
    """
    def __init__(self):
        super(AliasDictClass, self).__init__(
            dict([
                ("bindings", set()),
                ("root_aliases", set()),
                ("used", set()),
                ("warnings", set()),
                ("errors", set()),
            ])
        )

    def clean(self):
        """clean will reset the AliasDict global object."""
        print(_color(
            color=ANSI.colors.red, text="Cleaning the global AliasDict"
        ))
        self["bindings"] = set()
        self["root_aliases"] = set()
        self["used"] = set()
        self["warnings"] = set()
        self["errors"] = set()


AliasDict = AliasDictClass()


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
