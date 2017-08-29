from qt_py_convert._modules.psep0101 import _qsignal


def check_connection(source, dest):
    convert = _qsignal.process_connect(source)
    try:
        assert convert == dest
    except AssertionError as err:
        raise AssertionError("%s is not %s" % (convert, dest))


def check_emit(source, dest):
    convert = _qsignal.process_emit(source)
    try:
        assert convert == dest
    except AssertionError as err:
        raise AssertionError("%s is not %s" % (convert, dest))


def check_disconnect(source, dest):
    convert = _qsignal.process_disconnect(source)
    try:
        assert convert == dest
    except AssertionError as err:
        raise AssertionError("%s is not %s" % (convert, dest))


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

def test_connection_qobject_suite():
    check_connection(
        "QtCore.QObject.connect(self.ui.pushButton, QtCore.SIGNAL('clicked()'), self.refresher)",
        "self.ui.pushButton.clicked.connect(self.refresher)"
    ),
    check_connection(
        "QtCore.QObject.connect(self.ui.pushButton_selAll, QtCore.SIGNAL('clicked()'), self.selectAllChannels)",
        "self.ui.pushButton_selAll.clicked.connect(self.selectAllChannels)"
    ),
    check_connection(
        "QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL('accepted()'), self.configureShuffles)",
        "self.ui.buttonBox.accepted.connect(self.configureShuffles)"
    ),
    check_connection(
        "QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL('rejected()'), self.close)",
        "self.ui.buttonBox.rejected.connect(self.close)"
    ),
    check_connection(
        "QtCore.QObject.connect(self.ui.treeView.selectionModel(), QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'), self.setViewerLayer)",
        "self.ui.treeView.selectionModel().selectionChanged.connect(self.setViewerLayer)"
    ),
    check_connection(
        "QtCore.QObject.connect(self.ui.treeView.selectionModel(), QtCore.SIGNAL('selectedIndexes()'), self.toggleViewerLayer)",
        "self.ui.treeView.selectionModel().selectedIndexes.connect(self.toggleViewerLayer)"
    ),
    check_connection(
        "QtCore.QObject.connect(self.ui.checkBox_inViewer, QtCore.SIGNAL('stateChanged(int)'), self.setViewerLayer)",
        "self.ui.checkBox_inViewer.stateChanged.connect(self.setViewerLayer)"
    ),
    check_connection(
        "QtCore.QObject.connect(self.ui.checkBox_addWrites, QtCore.SIGNAL('stateChanged(int)'), self.togglePath)",
        "self.ui.checkBox_addWrites.stateChanged.connect(self.togglePath)"
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
