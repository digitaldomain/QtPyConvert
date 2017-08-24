from qt_py_convert._modules.psep0101 import _qsignal


def check_connection(source, dest):
    assert _qsignal.process_connect(source) == dest


def check_emit(source, dest):
    assert _qsignal.process_emit(source) == dest


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

if __name__ == "__main__":
    test_emit_multi_args()
