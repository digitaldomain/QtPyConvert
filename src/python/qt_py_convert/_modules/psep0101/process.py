"""
The psep0101 module is designed to make the changes set out in psep0101.

These are the changes that created "api v2.0", which is what PySide uses and
PyQt4 has the option of.
"""
__author__ = 'ahughes'
# https://github.com/techtonik/pseps

import re
import sys

from qt_py_convert.general import change, ErrorClass
from qt_py_convert.log import get_logger
from qt_py_convert._modules.psep0101 import _qsignal
from qt_py_convert._modules.psep0101 import _conversion_methods


PSEP_LOG = get_logger("psep0101")

# Pulled out of six because I don't want to have to bind this package to DD
# code to load six.
# That seems a little insane to me...So because I am only using six.text_type,
# I am removing the six import and inlining the code.
# TODO: rely on six when this is OSS
text_type = str if sys.version_info[0] == 3 else unicode


class Processes(object):
    """Processes class for psesp0101"""
    @staticmethod
    def _process_qvariant(red, objects, skip_lineno=False):
        """
        _process_qvariant is designed to replace QVariant code.

        :param red: redbaron process. Unused in this method.
        :type red: redbardon.RedBaron
        :param objects: List of redbaron nodes that matched for this proc.
        :type objects: list
        :param skip_lineno: Global "skip_lineno" flag.
        :type skip_lineno: bool
        """
        qvariant_expr = re.compile(
            r"(?:QtCore\.)?QVariant(?P<is_instance>\((?P<value>.*)\))?"
        )

        # Replace each node
        for node in objects:
            raw = node.parent.dumps()
            matched = qvariant_expr.search(raw)
            if matched:
                if not matched.groupdict()["is_instance"]:
                    # We have the usage of a QVariant Class object.
                    # This leads to an invalid statement and cannot be
                    #   resolved in api 2.0.
                    # We are adding it to warnings and continuing on.
                    ErrorClass(
                        node=node,
                        reason="""
As of api v2.0, there is no concept of a "QVariant" object.
Usage of the class object directly cannot be translated into something that \
can consistantly be relied on.

You will probably want to remove the usage of this entirely."""
                        )
                    continue
                else:  # If it was used as an instance (most cases).
                    def replacement(match):
                        """regex sub function"""
                        # Some edge case logic here.
                        # Was having issues replacing the following code:
                        # return QtCore.QVariant()
                        # There was no parameter...So now that becomes:
                        # return None
                        if not match.groupdict()["value"]:
                            return "None"
                        return match.groupdict()["value"]

                    # We have an instance of a QVariant used.
                    changed = qvariant_expr.sub(
                        replacement, raw
                    )

                if changed != raw:
                    change(
                        logger=PSEP_LOG,
                        node=node.parent,
                        replacement=changed,
                        skip_lineno=skip_lineno,
                    )
                    node.parent.replace(changed)

    @staticmethod
    def _process_qstring(red, objects, skip_lineno=False):
        """
        _process_qstring is designed to replace QString code.

        :param red: redbaron process. Unused in this method.
        :type red: redbardon.RedBaron
        :param objects: List of redbaron nodes that matched for this proc.
        :type objects: list
        :param skip_lineno: Global "skip_lineno" flag.
        :type skip_lineno: bool
        """
        # Replace each node
        for node in objects:
            raw = node.parent.dumps()
            changed = re.sub(
                r"((?:QtCore\.)?QString(?:\.fromUtf8)?)",
                text_type.__name__,
                raw
            )
            if changed != raw:
                change(
                    logger=PSEP_LOG,
                    node=node.parent,
                    replacement=changed,
                    skip_lineno=skip_lineno,
                )

                node.parent.replace(changed)

    @staticmethod
    def _process_qstringlist(red, objects, skip_lineno=False):
        """
        _process_qstringlist is designed to replace QStringList code.

        :param red: redbaron process. Unused in this method.
        :type red: redbardon.RedBaron
        :param objects: List of redbaron nodes that matched for this proc.
        :type objects: list
        :param skip_lineno: Global "skip_lineno" flag.
        :type skip_lineno: bool
        """
        # TODO: Find different usage cases of QStringList.
        #       Probably just need support for construction and isinstance.
        # Replace each node
        for node in objects:
            raw = node.parent.dumps()
            changed = re.sub(
                r"((?:QtCore\.)?QStringList)",
                "list",
                raw
            )
            if changed != raw:
                change(
                    logger=PSEP_LOG,
                    node=node.parent,
                    replacement=changed,
                    skip_lineno=skip_lineno,
                )

                node.parent.replace(changed)

    @staticmethod
    def _process_qchar(red, objects, skip_lineno=False):
        """
        _process_qchar is designed to replace QChar code.

        :param red: redbaron process. Unused in this method.
        :type red: redbardon.RedBaron
        :param objects: List of redbaron nodes that matched for this proc.
        :type objects: list
        :param skip_lineno: Global "skip_lineno" flag.
        :type skip_lineno: bool
        """
        # Replace each node
        for node in objects:
            raw = node.parent.dumps()
            changed = re.sub(
                r"((?:QtCore\.)?QChar)",
                text_type.__name__,
                raw
            )
            if changed != raw:
                change(
                    logger=PSEP_LOG,
                    node=node.parent,
                    replacement=changed,
                    skip_lineno=skip_lineno,
                )

                node.parent.replace(changed)

    @staticmethod
    def _process_to_methods(red, objects, skip_lineno=False):
        """
        Attempts at fixing the "toString" "toBool" "toPyObject" etc
        PyQt4-apiv1.0 helper methods.

        :param red: redbaron process. Unused in this method.
        :type red: redbardon.RedBaron
        :param objects: List of redbaron nodes that matched for this proc.
        :type objects: list
        :param skip_lineno: Global "skip_lineno" flag.
        :type skip_lineno: bool
        """
        for node in objects:
            raw = node.parent.dumps()
            changed = _conversion_methods.to_methods(raw)
            if changed != raw:
                    change(
                        logger=PSEP_LOG,
                        node=node.parent,
                        replacement=changed,
                        skip_lineno=skip_lineno,
                    )

                    node.parent.replace(changed)
                    continue

    @staticmethod
    def _process_qsignal(red, objects, skip_lineno=False):
        """
        _process_qsignal is designed to replace QSignal code.
        It calls out to the _qsignal module and can fix disconnects, connects,
        and emits.

        :param red: redbaron process. Unused in this method.
        :type red: redbardon.RedBaron
        :param objects: List of redbaron nodes that matched for this proc.
        :type objects: list
        :param skip_lineno: Global "skip_lineno" flag.
        :type skip_lineno: bool
        """
        for node in objects:
            raw = node.parent.dumps()

            if "disconnect" in raw:
                changed = _qsignal.process_disconnect(raw)
                if changed != raw:
                    change(
                        logger=PSEP_LOG,
                        node=node.parent,
                        replacement=changed,
                        skip_lineno=skip_lineno,
                    )

                    node.parent.replace(changed)
                    continue
            if "connect" in raw:
                changed = _qsignal.process_connect(raw)
                if changed != raw:
                    change(
                        logger=PSEP_LOG,
                        node=node.parent,
                        replacement=changed,
                        skip_lineno=skip_lineno,
                    )
                    node.parent.replace(changed)
                    continue
            if "emit" in raw:
                changed = _qsignal.process_emit(raw)
                if changed != raw:

                    change(
                        logger=PSEP_LOG,
                        node=node.parent,
                        replacement=changed,
                        skip_lineno=skip_lineno,
                    )
                    node.parent.replace(changed)
                    continue

    @staticmethod
    def _process_qstringref(red, objects, skip_lineno=False):
        """
        _process_qstringref is designed to replace QStringRefs

        :param red: redbaron process. Unused in this method.
        :type red: redbardon.RedBaron
        :param objects: List of redbaron nodes that matched for this proc.
        :type objects: list
        :param skip_lineno: Global "skip_lineno" flag.
        :type skip_lineno: bool
        """
        # Replace each node
        for node in objects:
            raw = node.parent.dumps()
            changed = re.sub(
                r"((?:QtCore\.)?QStringRef)",
                text_type.__name__,
                raw
            )
            if changed != raw:
                change(
                    logger=PSEP_LOG,
                    node=node.parent,
                    replacement=changed,
                    skip_lineno=skip_lineno,
                )
                node.parent.replace(changed)

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
    QVARIANT_PROCESS_STR = "QVARIANT_PROCESS"
    QVARIANT_PROCESS = _process_qvariant
    TOMETHOD_PROCESS_STR = "TOMETHOD_PROCESS"
    TOMETHOD_PROCESS = _process_to_methods


def psep_process(store):
    """
    psep_process is one of the more complex handlers for the _modules.

    :param store: Store is the psep_issues dict defined in "process"
    :type store: dict
    :return: The filter_function callable.
    :rtype: callable
    """
    _qstring_expression = re.compile(
        r"QString(?:[^\w]+(?:.*?))+?$"
    )
    _qstringlist_expression = re.compile(
        r"QStringList(?:[^\w]+(?:.*?))+?$"
    )
    _qchar_expression = re.compile(
        r"QChar(?:[^\w]+(?:.*?))+?$"
    )
    _qstringref_expression = re.compile(
        r"QStringRef(?:[^\w]+(?:.*?))+?$"
    )
    _qsignal_expression = re.compile(
        r"(?:connect|disconnect|emit).*QtCore\.SIGNAL", re.DOTALL
    )
    _qvariant_expression = re.compile(
        r"^QVariant(?:[^\w]+(?:.*?))?$"
    )
    _to_method_expression = re.compile(
        r"to[A-Z][A-Za-z]+\(\)"
    )

    def filter_function(value):
        """
        filter_function takes an AtomTrailersNode or a DottedNameNode and will
        filter them out if they match something that has changed in psep0101.
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
        if _qvariant_expression.search(value.dumps()):
            store[Processes.QVARIANT_PROCESS_STR].add(value)
            found = True
        if Processes.TOMETHOD_PROCESS_STR in store:
            if _to_method_expression.search(value.dumps()):
                store[Processes.TOMETHOD_PROCESS_STR].add(value)
                found = True
        if found:
            return True
    return filter_function


def process(red, skip_lineno=False, tometh_flag=False, **kwargs):
    """
    process is the main function for the psep0101 process.

    :param red: Redbaron ast.
    :type red: redbaron.redbaron
    :param skip_lineno: An optional performance flag. By default, when the
        script replaces something, it will tell you which line it is
        replacing on. This can be useful for tracking the places that
        changes occurred. When you turn this flag on however, it will not
        show the line numbers. This can give great performance increases
        because redbaron has trouble calculating the line number sometimes.
    :type skip_lineno: bool
    :param tometh_flag: tometh_flag is an optional feature flag. Once turned
        on, it will attempt to replace any QString/QVariant/etc apiv1.0 methods
        that are being used in your script. It is currently not smart enough to
        confirm that you don't have any custom objects with the same method
        signature to PyQt4's apiv1.0 ones.
    :type tometh_flag: bool
    :param kwargs: Any other kwargs will be ignored.
    :type kwargs: dict
    """
    psep_issues = {
        Processes.QSTRING_PROCESS_STR: set(),
        Processes.QSTRINGLIST_PROCESS_STR: set(),
        Processes.QCHAR_PROCESS_STR: set(),
        Processes.QSTRINGREF_PROCESS_STR: set(),
        Processes.QSIGNAL_PROCESS_STR: set(),
        Processes.QVARIANT_PROCESS_STR: set(),
    }

    # Start running the to_method_process if we turn on the flag.
    if tometh_flag:
        psep_issues[Processes.TOMETHOD_PROCESS_STR] = set()

    red.find_all("AtomTrailersNode", value=psep_process(psep_issues))
    red.find_all("DottedNameNode", value=psep_process(psep_issues))

    name_nodes = red.find_all("NameNode")
    filter_function = psep_process(psep_issues)
    for name in name_nodes:
        filter_function(name)

    for issue in psep_issues:
        if psep_issues[issue]:
            getattr(Processes, issue)(
                red,
                psep_issues[issue],
                skip_lineno=skip_lineno
            )
