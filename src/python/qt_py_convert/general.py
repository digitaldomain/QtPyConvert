import json
import copy
import os


def _color(color, text):
    return "\033[%dm%s\033[0m" % (color, text)

# Binding support
__supported_bindings__ = ["PySide2", "PySide", "PyQt5", "PyQt4"]  # , "ddg.gui.qt", "pyqode.qt"]
_custom_bindings = os.environ.get("QT_CUSTOM_BINDINGS_SUPPORT")
if _custom_bindings:
    print("Found Custom Bindings. Adding: %s" % _custom_bindings.split(os.pathsep))
    __supported_bindings__ += _custom_bindings.split(os.pathsep)

_custom_misplaced_members = json.loads(
    os.environ.get("QT_CUSTOM_MISPLACED_MEMBERS", '{}')
)


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
