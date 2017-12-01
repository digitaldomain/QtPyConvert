"""
_qsignal module has helper replacement methods for the psep0101 qsignal
replacement methods.

It uses _c_args to attempt o parse C style args from api v1.0
"""
import re

from qt_py_convert._modules.psep0101._c_args import parse_args


def _connect_repl(match_obj):
    template = r"{owner}.{signal}.connect({slot})"
    groups = match_obj.groupdict()
    if "strslot" in groups and groups["strslot"]:
        template = template.replace("{slot}", "{root}.{strslot}")

    if "owner" not in groups or not groups["owner"]:
        template = template.replace("{owner}", "{root}")

    groups["args"] = parse_args(groups["args"] or "")
    return template.format(**groups)


def _disconnect_repl(match_obj):
    template = r"{owner}.{signal}.disconnect({slot})"
    groups = match_obj.groupdict()
    if "strslot" in groups and groups["strslot"]:
        template = template.replace("{slot}", "{root}.{strslot}")

    groups["args"] = parse_args(groups["args"] or "")
    return template.format(**groups)


def _emit_repl(match_obj):
    template = r"{owner}.{signal}.emit({args})"
    groups = match_obj.groupdict()
    # groups["args"] = parse_args(groups["args"])
    return template.format(**groups)


def process_connect(function_str):
    SIGNAL_RE = re.compile(
        r"""
(?P<root>[\w\.]+)?\.connect\((?:[\s\n]+)?

# Making the owner optional. 
# _connect_repl has been updated to use root if owner is missing.
(?:(?P<owner>.*>?),(?:[\s\n]+)?)?   

(?:QtCore\.)?SIGNAL\((?:[\s\n]+)?(?:_fromUtf8\()?(?:[\s\n]+)?[\'\"](?P<signal>\w+)(?:\((?P<args>.*?)\))?[\'\"](?:[\s\n]+)?\)?(?:[\s\n]+)?\),(?:[\s\n]+)?

  # Either QtCore.SLOT("thing()") or an actual callable in scope.
  # If it is the former, we are assuming that the str name is owned by root.
    (?:(?:(?:QtCore\.)?SLOT\((?:[\s\n]+)?(?:_fromUtf8\()?(?:[\s\n]+)?[\'\"](?P<strslot>.*?)\((?P<slot_args>.*?)\)[\'\"](?:[\s\n]+)?\)?(?:[\s\n]+)?\))
  |
    (?:(?:[\s\n]+)?(?P<slot>.*?)(?:[\s\n]+)?))
\)""",
        re.VERBOSE | re.MULTILINE
    )
    # match = SIGNAL_RE.search(function_str)
    replacement_str = SIGNAL_RE.sub(
        _connect_repl,
        function_str
    )
    if replacement_str != function_str:
        return replacement_str
    return function_str


def process_disconnect(function_str):
    SIGNAL_RE = re.compile(
        r"""
(?P<root>[\w\.]+)?\.disconnect\((?:[\s\n]+)?
(?P<owner>.*>?),(?:[\s\n]+)?
(?:QtCore\.)?SIGNAL\((?:[\s\n]+)?(?:_fromUtf8\()?(?:[\s\n]+)?[\'\"](?P<signal>\w+)\((?P<args>.*?)\)[\'\"](?:[\s\n]+)?\)?(?:[\s\n]+)?\),(?:[\s\n]+)?

  # Either QtCore.SLOT("thing()") or an actual callable in scope.
  # If it is the former, we are assuming that the str name is owned by root.
    (?:(?:(?:QtCore\.)?SLOT\((?:[\s\n]+)?(?:_fromUtf8\()?(?:[\s\n]+)?[\'\"](?P<strslot>.*?)\((?P<slot_args>.*?)\)[\'\"](?:[\s\n]+)?\)?(?:[\s\n]+)?\))
  |
    (?:(?:[\s\n]+)?(?P<slot>.*?)(?:[\s\n]+)?))
\)""",
        re.VERBOSE
    )

    # SIGN = re.compile(
    #     r"(?P<root>\w+)?\.disconnect\((?:[\s\n]+)?(?P<owner>.*?),(?:[\s\n]+)?(?:QtCore\.)?SIGNAL\((?:[\s\n]+)?[\'\"](?P<signal>\w+)\((?P)"
    # )
    """
    'self.disconnect(self, QtCore.SIGNAL("textChanged()"), self.slot_textChanged)',
    "self.textChanged.disconnect(self.slot_textChanged)"
    """
    replacement_str = SIGNAL_RE.sub(
        _disconnect_repl,
        function_str
    )
    if replacement_str != function_str:
        return replacement_str
    return function_str


def process_emit(function_str):
    SIGNAL_RE = re.compile(
        r"(?P<owner>[\w\.]+)?\.emit\((?:[\s\n]+)?(?:QtCore\.)?SIGNAL\((?:[\s\n]+)?[\"\'](?P<signal>\w+)\((?P<arg_types>.*?)\)[\"\'](?:[\s\n]+)?\)(?:[\s\n]+)?(?:,(?:[\s\n]+)?)?(?P<args>.*?)\)"
    )
    match = SIGNAL_RE.search(function_str)
    replacement_str = SIGNAL_RE.sub(
        _emit_repl,
        function_str
    )
    if replacement_str != function_str:
        return replacement_str
    return function_str
