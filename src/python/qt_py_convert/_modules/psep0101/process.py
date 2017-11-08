__author__ = 'ahughes'
# https://github.com/techtonik/pseps

import re

import six

from qt_py_convert.general import _color
from qt_py_convert._modules.psep0101 import _qsignal


def psep_handler(msg):
    print(
        "[%s] %s" % (_color(35, "psep0101"), msg)
    )


class Processes(object):
    @staticmethod
    def _process_qvariant(red, objects):
        # Replace each node
        for node in objects:
            raw = node.parent.dumps()
            changed = re.sub(
                r"((?:QtCore\.)?QVariant\(?P<value>.*?)\)",
                r"\g<value>",
                raw
            )
            if changed != raw:
                psep_handler(
                    "Replaceing \"%s\" with \"%s\""
                    % (_color(32, raw), _color(34, changed))
                )
                node.parent.replace(changed)

    @staticmethod
    def _process_qstring(red, objects):
        # Replace each node
        for node in objects:
            raw = node.parent.dumps()
            changed = re.sub(
                r"((?:QtCore\.)?QString(?:\.fromUtf8)?)",
                six.text_type.__name__,
                raw
            )
            if changed != raw:
                psep_handler(
                    "Replacing \"%s\" with \"%s\""
                    % (_color(32, raw), _color(34, changed))
                )
                node.parent.replace(changed)

        # Search tree for usages of a QString method. (Good luck with that)
        pass

    @staticmethod
    def _process_qstringlist(red, objects):
        # TODO: find different usage cases of QStringList. Probably just need support for construction and isinstance.
        # Replace each node
        for node in objects:
            raw = node.parent.dumps()
            changed = re.sub(
                r"((?:QtCore\.)?QStringList)",
                "list",
                raw
            )
            if changed != raw:
                psep_handler(
                    "Replacing \"%s\" with \"%s\""
                    % (_color(32, raw), _color(34, changed))
                )
                node.parent.replace(changed)
        # Search tree for usages of a QStringList method. (Good luck with that)
        pass

    @staticmethod
    def _process_qchar(red, objects):
        # Replace each node
        for node in objects:
            raw = node.parent.dumps()
            changed = re.sub(
                r"((?:QtCore\.)?QChar)",
                six.text_type.__name__,
                raw
            )
            if changed != raw:
                psep_handler(
                    "Replacing \"%s\" with \"%s\""
                    % (_color(32, raw), _color(34, changed))
                )
                node.parent.replace(changed)


        # Search tree for usages of a QChar method. (Good luck with that)
        pass

    @staticmethod
    def _process_qsignal(red, objects):
        for node in objects:
            raw = node.parent.dumps()

            if "disconnect" in raw:
                replacement = _qsignal.process_disconnect(raw)
                if replacement != raw:
                    psep_handler(
                        "Replacing \"%s\" with \"%s\""
                        % (_color(32, raw), _color(34, replacement))
                    )
                    node.parent.replace(replacement)
                    continue
            if "connect" in raw:
                replacement = _qsignal.process_connect(raw)
                if replacement != raw:
                    psep_handler(
                        "Replacing \"%s\" with \"%s\""
                        % (_color(32, raw), _color(34, replacement))
                    )
                    node.parent.replace(replacement)
                    continue
            if "emit" in raw:
                replacement = _qsignal.process_emit(raw)
                if replacement != raw:
                    psep_handler(
                        "Replacing \"%s\" with \"%s\""
                        % (_color(32, raw), _color(34, replacement))
                    )
                    node.parent.replace(replacement)
                    continue


    @staticmethod
    def _process_qstringref(red, objects):
        # Replace each node
        for node in objects:
            raw = node.parent.dumps()
            changed = re.sub(
                r"((?:QtCore\.)?QStringRef)",
                six.text_type.__name__,
                raw
            )
            if changed != raw:
                psep_handler(
                    "Replacing \"%s\" with \"%s\""
                    % (_color(32, raw), _color(34, changed))
                )
                node.parent.replace(changed)

        # Search tree for usages of a QStringRef method. (Good luck with that)
        pass

    QSTRING_PROCESS_STR = "QSTRING_PROCESS"
    QSTRINGLIST_PROCESS_STR = "QSTRINGLIST_PROCESS"
    QCHAR_PROCESS_STR = "QCHAR_PROCESS"
    QSTRINGREF_PROCESS_STR = "QSTRINGREF_PROCESS"
    QSTRING_PROCESS = _process_qstring
    QSTRINGLIST_PROCESS = _process_qstringlist
    QCHAR_PROCESS = _process_qchar
    QSTRINGREF_PROCESS = _process_qstringref
    QSIGNAL_PROCESS_STR = "QSIGNAL_PROCESS"
    QSIGNAL_PROCESS = _process_qsignal


def psep_process(store):
    _qstring_expression = re.compile(r"QString(?:[^\w]+(?:.*?))?$")
    _qstringlist_expression = re.compile(r"QStringList(?:[^\w]+(?:.*?))?$")
    _qchar_expression = re.compile(r"QChar(?:[^\w]+(?:.*?))?$")
    _qstringref_expression = re.compile(r"QStringRef(?:[^\w]+(?:.*?))?$")
    _qsignal_expression = re.compile(r"[(?:connect)|(?:disconnect)|(?:emit)].*QtCore\.SIGNAL", re.DOTALL)

    def filter_function(value):
        """
        filter_function takes an AtomTrailersNode or a DottedNameNode and will filter them out if they match something that
        has changed in psep0101
        """
        found = False
        if _qstring_expression.search(value.dumps()):
            store[Processes.QSTRING_PROCESS_STR].add(value)
            found = True
        if _qstringlist_expression.search(value.dumps()):
            store[Processes.QSTRINGLIST_PROCESS_STR].add(value)
            found = True
        if _qchar_expression.search(value.dumps()):
            store[Processes.QCHAR_PROCESS_STR].add(value)
            found = True
        if _qstringref_expression.search(value.dumps()):
            store[Processes.QSTRINGREF_PROCESS_STR].add(value)
            found = True
        if _qsignal_expression.search(value.dumps()):
            store[Processes.QSIGNAL_PROCESS_STR].add(value)
            found = True
        if found:
            return True
    return filter_function


def process(red):
    psep_issues = {
        Processes.QSTRING_PROCESS_STR: set(),
        Processes.QSTRINGLIST_PROCESS_STR: set(),
        Processes.QCHAR_PROCESS_STR: set(),
        Processes.QSTRINGREF_PROCESS_STR: set(),
        Processes.QSIGNAL_PROCESS_STR: set(),
    }
    red.find_all("AtomTrailersNode", value=psep_process(psep_issues))
    red.find_all("DottedNameNode", value=psep_process(psep_issues))

    for issue in psep_issues:
        getattr(Processes, issue)(red, psep_issues[issue]) if psep_issues[issue] else None
