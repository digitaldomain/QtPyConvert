__author__ = 'ahughes'
# https://github.com/techtonik/pseps

import re

import six

from qt_py_convert.general import _color


def psep_handler(msg):
    print(
        "[%s] %s" % (_color(35, "psep0101"), msg)
    )


class Processes(object):
    @staticmethod
    def _process_qstring(red, objects):
        # Replace each node
        for node in objects:
           node.parent.replace(
               re.sub(
                   r"((?:QtCore\.)?QString)",
                   six.text_type.__name__,
                   node.parent.dumps()
               )
           )

        # Search tree for usages of a QString method. (Good luck with that)
        pass

    @staticmethod
    def _process_qstringlist(red, objects):
        # TODO: find different usage cases of QStringList. Probably just need support for construction and isinstance.
        # Replace each node
        for node in objects:
           node.parent.replace(
               re.sub(
                   r"((?:QtCore\.)?QString)",
                   "list",
                   node.parent.dumps()
               )
           )

        # Search tree for usages of a QStringList method. (Good luck with that)
        pass

    @staticmethod
    def _process_qchar(red, objects):
        # Replace each node
        for node in objects:
           node.parent.replace(
               re.sub(
                   r"((?:QtCore\.)?QChar)",
                   six.text_type.__name__,
                   node.parent.dumps()
               )
           )

        # Search tree for usages of a QChar method. (Good luck with that)
        pass

    @staticmethod
    def _process_qsignal(red, objects):
        # self.connect( <X>, QtCore.SIGNAL('<Y>'), <Z>)
        # <X>.<Y>.connect(<Z>)
        SIGNAL_RE = re.compile(
            r"(?:self\.)?connect\((?:\s+)?(?P<X>.*?),(?:\s+)?QtCore\.SIGNAL\((?:\s+)?[\'\"](?P<Y>.*?)\(\)[\'\"](?:\s+)?\),(?:\s+)?(?P<Z>.*?)(?:\s+)?\)"
        )
        SIGNAL_EMIT_RE = re.compile(
            r"(?:(?P<owner>\w+)\.)?emit\((?:\s+)?(?:QtCore\.)?SIGNAL\((?:\s+)?[\"\'](?P<function>\w+)\((?P<args>.*?)\)[\"\'](?:\s+)?\)(?:\s+)?\)"
        )
        for node in objects:
            raw = node.parent.dumps()
            connect = SIGNAL_RE.sub(
                r"\g<X>.\g<Y>.connect(\g<Z>)",
                raw
            )
            emit = SIGNAL_EMIT_RE.sub(
                r"\g<owner>.\g<function>.emit(\g<args>)",
                raw
            )
            if connect != raw:
                psep_handler(
                    "Replacing \"%s\" with \"%s\""
                    % (_color(32, raw), _color(34, connect))
                )
                node.parent.replace(connect)
            elif emit != raw:
                psep_handler(
                    "Replacing \"%s\" with \"%s\""
                    % (_color(32, raw), _color(34, emit))
                )
                node.parent.replace(emit)


    @staticmethod
    def _process_qstringref(red, objects):
        # Replace each node
        for node in objects:
           node.parent.replace(
               re.sub(
                   r"((?:QtCore\.)?QStringRef)",
                   six.text_type.__name__,
                   node.parent.dumps()
               )
           )

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
    _qsignal_expression = re.compile(r"QtCore\.SIGNAL")

    def filter_function(value):
        """
        filter_function takes an AtomTrailersNode or a DottedNameNode and will filter them out if they match something that
        has changed in psep0101
        """
        if _qstring_expression.search(value.dumps()):
            store[Processes.QSTRING_PROCESS_STR].add(value)
            return True
        elif _qstringlist_expression.search(value.dumps()):
            store[Processes.QSTRINGLIST_PROCESS_STR].add(value)
            return True
        elif _qchar_expression.search(value.dumps()):
            store[Processes.QCHAR_PROCESS_STR].add(value)
            return True
        elif _qstringref_expression.search(value.dumps()):
            store[Processes.QSTRINGREF_PROCESS_STR].add(value)
            return True
        elif _qsignal_expression.search(value.dumps()):
            store[Processes.QSIGNAL_PROCESS_STR].add(value)
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
