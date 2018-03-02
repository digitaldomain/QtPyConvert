from qt_py_convert.run import run
from qt_py_convert.general import _highlight_diffs


def check(source, dest):
    aliases, mappings, dumps = run(source, True, True)
    try:
        assert dumps == dest
    except AssertionError as err:
        raise AssertionError("\n\"%s\"\n!=\n\"%s\"\n" %
            _highlight_diffs(dumps, dest)
        )


def test_qapplication_translate_basic():
    check(
        """from PySide import QtGui

QtGui.QApplication.translate(context, text, disambig)
""",
        """from Qt import QtCompat

QtCompat.translate(context, text, disambig)
"""
    )


def test_qcoreapplication_translate_basic():
    check(
        """from PySide import QtCore

QtCore.QCoreApplication.translate(context, text, disambig)
""",
        """from Qt import QtCompat

QtCompat.translate(context, text, disambig)
"""
    )


def test_qinstallmessagehandler_basic():
    check(
        """from PySide import QtCore

def handler(*args):
    pass

QtCore.qInstallMsgHandler(handler)
""",
        """from Qt import QtCompat

def handler(*args):
    pass

QtCompat.qInstallMessageHandler(handler)
"""
    )


if __name__ == "__main__":
    import traceback
    _tests = filter(
        lambda key: True if key.startswith("test_") else False,
        globals().keys()
    )

    failed = []
    for test in _tests:
        try:
            print("Running %s" % test)
            globals()[test]()
            print("    %s succeeded!" % test)
        except AssertionError as err:
            print("    %s failed!" % test)
            failed.append((test, traceback.format_exc()))
        print("")
    for failure_name, failure_error in failed:
        print("""
------------ %s FAILED ------------
%s
""" % (failure_name, failure_error))

    print(
        "\n\n%d failures, %d success, %s%%" % (
            len(failed),
            len(_tests)-len(failed),
            "%.1f" % ((float(len(_tests)-len(failed))/len(_tests))*100)
        )
    )
