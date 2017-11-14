import copy
import json
import os
import subprocess
import sys


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


def _color(color, text):
    if not __supports_color:
        return text
    return "\033[%dm%s\033[0m" % (color, text)

# Binding support
__supported_bindings__ = ["PySide2", "PySide", "PyQt5", "PyQt4"]  # , "ddg.gui.qt", "pyqode.qt"]
_custom_bindings = os.environ.get("QT_CUSTOM_BINDINGS_SUPPORT")
if _custom_bindings:
    print("Found Custom Bindings. Adding: %s" % _custom_bindings.split(os.pathsep))
    __supported_bindings__ += _custom_bindings.split(os.pathsep)

# Note: Pattern here is a little more complex than needed to make the print lines optional
_custom_misplaced_members = {}
misplaced_members_python_str = os.environ.get("QT_CUSTOM_MISPLACED_MEMBERS")
if misplaced_members_python_str:
    print ("QT_CUSTOM_MISPLACED_MEMBERS = {0!r}".format(misplaced_members_python_str))

    _custom_misplaced_members = json.loads(misplaced_members_python_str)

    # Colored green
    print (_color(32, "Resolved QT_CUSTOM_MISPLACED_MEMBERS to json: {0!r}".format(_custom_misplaced_members)))


AliasDict = dict([
    ("bindings", set()),
    ("root_aliases", set()),
    ("used", set()),
])


def merge_dict(lhs, rhs, keys=None, keys_both=False):
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
