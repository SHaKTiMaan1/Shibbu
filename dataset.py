from PyQt5 import QtCore, QtGui, QtWidgets

from main import *


class ButtonHeaderView(QtWidgets.QHeaderView):
    def __init__(self, parent):
        super().__init__(QtCore.Qt.Vertical, parent)
        self.m_buttons = []
        self.sectionResized.connect(self.adjustPositions)
        self.sectionCountChanged.connect(self.onSectionCountChanged)
        self.parent().horizontalScrollBar().valueChanged.connect(self.adjustPositions)

    @QtCore.pyqtSlot()
    def onSectionCountChanged(self):
        while self.m_buttons:
            button = self.m_buttons.pop()
            button.deleteLater()
        for i in range(self.count()):
            button = QtWidgets.QPushButton(self)
            button.setCursor(QtCore.Qt.ArrowCursor)
            self.m_buttons.append(button)
            self.update_data()
            self.adjustPositions()

    def setModel(self, model):
        super().setModel(model)
        if self.model() is not None:
            self.model().headerDataChanged.connect(self.update_data)

    def update_data(self):
        for i, button in enumerate(self.m_buttons):
            text = self.model().headerData(i, self.orientation(), QtCore.Qt.DisplayRole)
            button.setText(str(text))

    def updateGeometries(self):
        super().updateGeometries()
        self.adjustPositions()

    @QtCore.pyqtSlot()
    def adjustPositions(self):
        w = 0
        for index, button in enumerate(self.m_buttons):
            geom = QtCore.QRect(
                0,
                self.sectionViewportPosition(index),
                button.height(),
                self.sectionSize(index),
            )
            w = max(w, button.height())
            geom.adjust(0, 2, 0, -2)
            button.setGeometry(geom)
        self.setFixedWidth(w)


'''if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QTableWidget(3, 4)
    header = ButtonHeaderView(w)
    w.setVerticalHeader(header)
    w.setHorizontalHeaderLabels(["Field 1", "Field 2", "Field 3", "Field N"])

    header_buttons = []
    for i in range(w.columnCount()):
        header_button = "+"
        header_buttons.append(header_button)
    w.setVerticalHeaderLabels(header_buttons)

    w.resize(320, 240)
    w.show()
    sys.exit(app.exec_())
    '''