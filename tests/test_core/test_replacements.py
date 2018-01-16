from qt_py_convert.run import run


def check(source, dest):
    aliases, mappings, dumps = run(source, True, True)
    try:
        assert dumps == dest
    except AssertionError as err:
        raise AssertionError("\n\"%s\"\n!=\n\"%s\"\n" % (dumps, dest))


def test_multiple_replacements_one_line():
    check(
        """from PyQt4 import QtGui

def fake_function():
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
""",
        """from Qt import QtWidgets

def fake_function():
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
""")


def test_qlineedit_replacement():
    # This makes sure we don't have a regression for module mapping replacements.
    # For example QtCore.QLine matching QtWidgets.QLineEdit
    check(
        """from PyQt4.QtGui import QLineEdit

l = QLineEdit()
x = 42""",
        """from Qt import QtWidgets

l = QtWidgets.QLineEdit()
x = 42"""
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