"""
DO NOT CHANGE THIS CODE! Tests will use specific lines to assert results
Module with a mix of namespaces and code and comment mentions (including a css snippit.

Mentioning a QWidget and QtCore.QRect here in the module comment too. These should be ignored when
moving to the new QWidgets namespace.
"""
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QPushButton, QColor
from PyQt4.QtCore import Qt


class AutoExpandingPlainTextEdit(QtGui.QPlainTextEdit):
    """ A QPlainTextEdit that provides auto-expanding behavior. """

    def __init__(self, parent=None):
        super(AutoExpandingPlainTextEdit, self).__init__(parent)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.max_height = 300
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), QtGui.QSizePolicy.Fixed)

        self.textChanged.connect(self.onTextChanged)  # To update the geometry for sizeHint(0

    def sizeHint(self):
        """ Set the size hint to the total content height """
        # This starts off larger for a few iterations and then seems to find the right value
        font_height = QtGui.QFontMetrics(self.font()).height()
        num_lines = self.document().size().height()  # Docs make it sound like px
        height = num_lines * font_height

        # Add decoration
        height += self.contentsMargins().top()
        height += self.contentsMargins().bottom()
        height += font_height * 0.7  # Magical extra space for new-line space I guess

        if height >= self.max_height:
            height = self.max_height
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        else:
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # QSize: Only affect the height. Width is from base class
        return QtCore.QSize(super(AutoExpandingPlainTextEdit, self).sizeHint().width(), height)

    def onTextChanged(self):
        """ Qt slot to update the geometry which will update the sizeHint() """
        self.updateGeometry()


class Color(QtGui.QWidget):
    """Base class for limited-length float/color vectors."""

    def __init__(self, r=0, b=0, g=0, a=1, parent=None):
        super(Color, self).__init__(parent)

        self.values = [r, g, b, a]

        self.color_button = QPushButton('c', self)
        self.color_button.setFlat(True)
        self.color_button.setMinimumWidth(24)
        self.color_button.setMaximumWidth(24)
        self.color_button.clicked.connect(self.pickColor)

        self.layout().addWidget(self.color_button)

        self.setColorIcon()

    def setColorIcon(self):
        """ Update the widget used for color feedback """
        # Takes rgb and rgba as floats (0-1) and the name is a hex.
        color = QColor()
        color.setRgbF(*self.values)
        self.color_button.setStyleSheet(
            "QPushButton {"
            "   padding: 1px 1px 2px 1px;"  # top right bottom left
            "   border-radius: 2px;"
            "   background-color: rgba(%s, %s, %s, %s);"
            "}" % (
                color.red(), color.green(), color.blue(), color.alpha()
            )
        )

    def pickColor(self):
        """Show a gui to interactively pick a color."""
        # we might want HDRI, ie. V > 1 in film/vfx
        current = QtGui.QColor()
        current.setRgbF(*self.values)
        options = QtGui.QColorDialog.ShowAlphaChannel
        color = QtGui.QColorDialog.getColor(current, self, 'Choose a color', options)
        if not color.isValid():
            return

        self.values = color.getRgbF()
        self.setColorIcon()

