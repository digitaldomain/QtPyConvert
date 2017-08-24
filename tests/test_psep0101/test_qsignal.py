from qt_py_convert._modules.psep0101 import _qsignal


def check_connection(source, dest):
    assert _qsignal.process_connect(source) == dest


def check_emit(source, dest):
    assert _qsignal.process_emit(source) == dest


def check_disconnect(source, dest):
    assert _qsignal.process_disconnect(source) == dest


def test_connection_no_args():
    check_connection(
        'self.connect(self.filterBox, QtCore.SIGNAL("textChanged()"), self.slot_filterBoxEdited)',
        "self.filterBox.textChanged.connect(self.slot_filterBoxEdited)"
    )

def test_connection_single_arg():
    check_connection(
        'self.connect(self.filterBox, QtCore.SIGNAL("textChanged(QString)"), self.slot_filterBoxEdited)',
        "self.filterBox.textChanged.connect(self.slot_filterBoxEdited)"
    )

def test_connection_single_arg_const():
    check_connection(
        'self.connect(self.filterBox, QtCore.SIGNAL("textChanged(const QString)"), self.slot_filterBoxEdited)',
        "self.filterBox.textChanged.connect(self.slot_filterBoxEdited)"
    )

def test_connection_single_arg_ref():
    check_connection(
        'self.connect(self.filterBox, QtCore.SIGNAL("textChanged(QString &)"), self.slot_filterBoxEdited)',
        "self.filterBox.textChanged.connect(self.slot_filterBoxEdited)"
    )

def test_connection_single_arg_ref_alt():
    check_connection(
        'self.connect(self.filterBox, QtCore.SIGNAL("textChanged(QString&)"), self.slot_filterBoxEdited)',
        "self.filterBox.textChanged.connect(self.slot_filterBoxEdited)"
    )

def test_connection_single_arg_constref():
    check_connection(
        'self.connect(self.filterBox, QtCore.SIGNAL("textChanged(const QString &)"), self.slot_filterBoxEdited)',
        "self.filterBox.textChanged.connect(self.slot_filterBoxEdited)"
    )

def test_connection_multi_arg():
    check_connection(
        'self.connect(self.filterBox, QtCore.SIGNAL("textChanged(const QString &, QVariant &)"), self.slot_filterBoxEdited)',
        "self.filterBox.textChanged.connect(self.slot_filterBoxEdited)"
    )

def test_connection_multi_arg_alt():
    check_connection(
        'self.connect(self.filterBox, QtCore.SIGNAL("textChanged(const QStringList &, QVariant &)"), self.slot_filterBoxEdited)',
        "self.filterBox.textChanged.connect(self.slot_filterBoxEdited)"
    )

def test_emit_no_args():
    check_emit(
        'self.emit(QtCore.SIGNAL("atomicPreflightChangedFrameRange()"))',
        "self.atomicPreflightChangedFrameRange.emit()"
    )

def test_emit_multi_args():
    check_emit(
        'self.dagEditor.emit(QtCore.SIGNAL("nodeNameEdited(PyQt_PyObject, PyQt_PyObject)"), node, newName)',
        "self.dagEditor.nodeNameEdited.emit(node, newName)"
    )

def test_disconnect_no_args():
    check_disconnect(
        'self.disconnect(self, QtCore.SIGNAL("textChanged()"), self.slot_textChanged)',
        "self.textChanged.disconnect(self.slot_textChanged)"
    )

def test_disconnect_single_arg_newlines():
    check_disconnect(
        'self.disconnect(self.batchGlobalsNode,\n                            QtCore.SIGNAL("attributeChanged(PyQt_PyObject)"),\n                            self.slot_raceGlobalsAttributeChanged)',
        "self.batchGlobalsNode.attributeChanged.disconnect(self.slot_raceGlobalsAttributeChanged)"
    )

def test_disconnect_local_var_newlines():
    check_disconnect(
        'self.disconnect(validation_message, QtCore.SIGNAL("atomicPreflightChangedFrameRange()"),\n                            self.slot_clientFrameRangeChanged)',
        "validation_message.atomicPreflightChangedFrameRange.disconnect(self.slot_clientFrameRangeChanged)"
    )

def test_disconnect_no_arg_alt():
    check_disconnect(
        'self.disconnect(self, QtCore.SIGNAL("atomicLevelEnvironmentChanged()"), self._slotLevelEnvironmentChanged)',
        "self.atomicLevelEnvironmentChanged.disconnect(self._slotLevelEnvironmentChanged)"
    )

def test_disconnect_single_arg():
    check_disconnect(
        'self.disconnect(self.sceneDag, QtCore.SIGNAL("dagChanged(PyQt_PyObject)"), self._slotDagChanged)',
        "self.sceneDag.dagChanged.disconnect(self._slotDagChanged)"
    )


if __name__ == "__main__":
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
            failed.append((test, err))
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
