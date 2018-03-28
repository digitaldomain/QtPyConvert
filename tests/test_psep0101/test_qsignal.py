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


def test_connection_ddqt_1():
    check_connection(
        '''QtCore.QObject.connect(self, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("handle_click()"))''',
        '''self.clicked.connect(self.handle_click)'''
    )


def test_connection_texturepipeline_whitespace():
    check_connection(
        '''self.seq_combo.connect  (QtCore.SIGNAL("currentIndexChanged(int)"),
                                 self._updateShot)''',
        'self.seq_combo.currentIndexChanged.connect(self._updateShot)'
    )

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


def test_connection_qobject1():
    check_connection(
        "QtCore.QObject.connect(self.ui.pushButton, QtCore.SIGNAL('clicked()'), self.refresher)",
        "self.ui.pushButton.clicked.connect(self.refresher)"
    )


def test_connection_qobject2():
    check_connection(
        "QtCore.QObject.connect(self.ui.pushButton_selAll, QtCore.SIGNAL('clicked()'), self.selectAllChannels)",
        "self.ui.pushButton_selAll.clicked.connect(self.selectAllChannels)"
    )


def test_connection_qobject3():
    check_connection(
        "QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL('accepted()'), self.configureShuffles)",
        "self.ui.buttonBox.accepted.connect(self.configureShuffles)"
    )


def test_connection_qobject4():
    check_connection(
        "QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL('rejected()'), self.close)",
        "self.ui.buttonBox.rejected.connect(self.close)"
    )


def test_connection_qobject5():
    check_connection(
        "QtCore.QObject.connect(self.ui.treeView.selectionModel(), QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'), self.setViewerLayer)",
        "self.ui.treeView.selectionModel().selectionChanged.connect(self.setViewerLayer)"
    )


def test_connection_qobject6():
    check_connection(
        "QtCore.QObject.connect(self.ui.treeView.selectionModel(), QtCore.SIGNAL('selectedIndexes()'), self.toggleViewerLayer)",
        "self.ui.treeView.selectionModel().selectedIndexes.connect(self.toggleViewerLayer)"
    )


def test_connection_qobject7():
    check_connection(
        "QtCore.QObject.connect(self.ui.checkBox_inViewer, QtCore.SIGNAL('stateChanged(int)'), self.setViewerLayer)",
        "self.ui.checkBox_inViewer.stateChanged.connect(self.setViewerLayer)"
    )


def test_connection_qobject8():
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


def test_connect_old_style_slot():
    check_connection(
        'self.connect(cancel_button, QtCore.SIGNAL("clicked()"), QtCore.SLOT("close()"))',
        "cancel_button.clicked.connect(self.close)"
    )


def test_connect_converted_fromUTF():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_svn_check_out, QtCore.SIGNAL(_fromUtf8("pressed()")), OTLpublisher.checkOut)',
        "self.BUTTON_svn_check_out.pressed.connect(OTLpublisher.checkOut)"
    )


def test_connect_converted_fromUTF_1():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_svn_check_in, QtCore.SIGNAL(_fromUtf8("pressed()")), OTLpublisher.checkIn)',
        "self.BUTTON_svn_check_in.pressed.connect(OTLpublisher.checkIn)"
    )


def test_connect_converted_fromUTF_2():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_refresh_info, QtCore.SIGNAL(_fromUtf8("pressed()")), OTLpublisher.refreshInfo)',
        "self.BUTTON_refresh_info.pressed.connect(OTLpublisher.refreshInfo)"
    )


def test_connect_converted_fromUTF_3():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_svn_cancel_check_out, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.checkOutCancel)',
        "self.BUTTON_svn_cancel_check_out.released.connect(OTLpublisher.checkOutCancel)"
    )


def test_connect_converted_fromUTF_4():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_svn_revert_to_earlier_version, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.revertToEarlierSvnVersion)',
        "self.BUTTON_svn_revert_to_earlier_version.released.connect(OTLpublisher.revertToEarlierSvnVersion)"
    )


def test_connect_converted_fromUTF_5():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_digital_asset_create, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.createDigitalAsset)',
        "self.BUTTON_digital_asset_create.released.connect(OTLpublisher.createDigitalAsset)"
    )


def test_connect_converted_fromUTF_6():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_digital_asset_edit_type_properties, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.editTypeProperties)',
        "self.BUTTON_digital_asset_edit_type_properties.released.connect(OTLpublisher.editTypeProperties)"
    )
def test_connect_converted_fromUTF_7():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_digital_asset_match_cur_def, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.matchCurDef)',
        "self.BUTTON_digital_asset_match_cur_def.released.connect(OTLpublisher.matchCurDef)"
    )


def test_connect_converted_fromUTF_8():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_digital_asset_allow_editing, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.allowEditing)',
        "self.BUTTON_digital_asset_allow_editing.released.connect(OTLpublisher.allowEditing)"
    )


def test_connect_converted_fromUTF_9():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_digital_asset_use_this_def, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.useThisDef)',
        "self.BUTTON_digital_asset_use_this_def.released.connect(OTLpublisher.useThisDef)"
    )


def test_connect_converted_fromUTF_10():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_digital_asset_copy, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.copyDigitalAsset)',
        "self.BUTTON_digital_asset_copy.released.connect(OTLpublisher.copyDigitalAsset)"
    )


def test_connect_converted_fromUTF_11():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_digital_asset_save, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.saveDigitalAsset)',
        "self.BUTTON_digital_asset_save.released.connect(OTLpublisher.saveDigitalAsset)"
    )


def test_connect_converted_fromUTF_12():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_digital_asset_delete, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.deleteDigitalAsset)',
        "self.BUTTON_digital_asset_delete.released.connect(OTLpublisher.deleteDigitalAsset)"
    )


def test_connect_converted_fromUTF_13():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_select_node, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.selectNode)',
        "self.BUTTON_select_node.released.connect(OTLpublisher.selectNode)"
    )


def test_connect_converted_fromUTF_14():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_digital_asset_publish, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.publishDigitalAsset)',
        "self.BUTTON_digital_asset_publish.released.connect(OTLpublisher.publishDigitalAsset)"
    )


def test_connect_converted_fromUTF_15():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_libsvn_copy, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.libSvnCopyDigitalAsset)',
        "self.BUTTON_libsvn_copy.released.connect(OTLpublisher.libSvnCopyDigitalAsset)"
    )


def test_connect_converted_fromUTF_16():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_digital_asset_version_up, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.versionUp)',
        "self.BUTTON_digital_asset_version_up.released.connect(OTLpublisher.versionUp)"
    )


def test_connect_converted_fromUTF_17():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_digital_asset_op_type_manager, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.opTypeManager)',
        "self.BUTTON_digital_asset_op_type_manager.released.connect(OTLpublisher.opTypeManager)"
    )


def test_connect_converted_fromUTF_18():
    check_connection(
        'QtCore.QObject.connect(self.BUTTON_help, QtCore.SIGNAL(_fromUtf8("released()")), OTLpublisher.help)',
        "self.BUTTON_help.released.connect(OTLpublisher.help)"
    )


def test_connect_old_style_multiline():
    check_connection(
        """self.connect(
            self.data.ui,
            QtCore.SIGNAL("launchPublishPopup"),
            self.publishDigitalAssetPopup
        )""",
        "self.data.ui.launchPublishPopup.connect(self.publishDigitalAssetPopup)"
    )


def test_connect_old_style_pyargs():
    check_connection(
        'QtCore.QObject.connect(self.ticket_tool, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(unicode)")), Flaregun.infoEntered)',
        "self.ticket_tool.currentIndexChanged.connect(Flaregun.infoEntered)",
    )


def test_connect_old_style_no_owner():
    check_connection(
        """self.__shot_combo.connect(QtCore.SIGNAL("currentIndexChanged(int)"),
                              self.__updateLinkVersionLabel)""",
        """self.__shot_combo.currentIndexChanged.connect(self.__updateLinkVersionLabel)""",
    )
    check_connection(
        """action.connect(QtCore.SIGNAL("triggered()"), self.selectPatches)""",
        """action.triggered.connect(self.selectPatches)""",
    )
    check_connection(
        """channel_all_check.connect(QtCore.SIGNAL("stateChanged(int)"),
                              self.__updateChannelStates)""",
        """channel_all_check.stateChanged.connect(self.__updateChannelStates)""",
    )


def test_connect_for_refchef():
    check_connection(
        """self.connect(self.thumbs_panel, QtCore.SIGNAL('loadImage'), self.preview_panel.loadImage)""",
        """self.thumbs_panel.loadImage.connect(self.preview_panel.loadImage)"""
    )


def test_connect_for_refchef2():
    check_connection(
        """self.connect(self.dir_panel, QtCore.SIGNAL("dirClicked(unicode, bool)"), self.thumbs_panel.loadFromDir)""",
        """self.dir_panel.dirClicked.connect(self.thumbs_panel.loadFromDir)"""
    )


def test_emit_for_refchef():
    check_emit(
        """self.emit(SIGNAL('imageLoadInterrupted'))""",
        """self.imageLoadInterrupted.emit()"""
    )


def test_emit_for_refchef2():
    check_emit(
        """self.emit(SIGNAL('imageLoaded'), self.image, self.is_linear, self.is_float)""",
        """self.imageLoaded.emit(self.image, self.is_linear, self.is_float)"""
    )


def test_emit_for_refchef3():
    check_emit(
        """self.emit(SIGNAL('loadFromData'), data)""",
        """self.loadFromData.emit(data)"""
    )


def test_emit_for_refchef4():
    check_emit(
        """self.emit(SIGNAL('itemClicked'), self.model().at(index.row()))""",
        """self.itemClicked.emit(self.model().at(index.row()))"""
    )


def test_emit_for_refchef5():
    check_emit(
        """QObject.emit(self, SIGNAL("dataChanged(const QModelIndex&, const QModelIndex &)"), index, index)""",
        """self.dataChanged.emit(index, index)"""
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
