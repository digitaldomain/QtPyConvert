from qt_py_convert.general import supported_binding


def test_import_level_styles():
    assert "PySide2" == supported_binding("PySide2")
    assert "PySide2" == supported_binding("PySide2.QtCore")
    assert "PySide2" == supported_binding("PySide2.QtWidgets")
    assert "PySide2" == supported_binding("PySide2.QtGui")

    assert "PySide" == supported_binding("PySide")
    assert "PySide" == supported_binding("PySide.QtCore")
    assert "PySide" == supported_binding("PySide.QtWidgets")
    assert "PySide" == supported_binding("PySide.QtGui")

    assert "PyQt5" == supported_binding("PyQt5")
    assert "PyQt5" == supported_binding("PyQt5.QtCore")
    assert "PyQt5" == supported_binding("PyQt5.QtWidgets")
    assert "PyQt5" == supported_binding("PyQt5.QtGui")
 
    assert "PyQt4" == supported_binding("PyQt4")
    assert "PyQt4" == supported_binding("PyQt4.QtCore")
    assert "PyQt4" == supported_binding("PyQt4.QtWidgets")
    assert "PyQt4" == supported_binding("PyQt4.QtGui")


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
