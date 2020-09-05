from PySide2.QtCore import Qt
from PySide2.QtGui import QPen, QColor, QPixmap
from PySide2.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsSimpleTextItem, QApplication, \
    QGraphicsPixmapItem

from leaguedirector.widgets import respath


class SequenceHeader(QGraphicsRectItem):
    height = 22

    def __init__(self, api, name, index, callback):
        QGraphicsRectItem.__init__(self)
        self.api = api
        self.name = name
        self.index = index
        self.callback = callback
        self.setPos(0, self.height * self.index)
        self.setRect(0, 0, 160, self.height)
        self.setToolTip(self.label())
        self.setPen(QPen(Qt.NoPen))
        self.setBrush(QColor(20, 20, 50, 255))
        self.setFlags(QGraphicsItem.ItemIgnoresTransformations)
        self.text = QGraphicsSimpleTextItem(self.label(), self)
        self.text.setBrush(QApplication.palette().brightText())
        self.text.setPos(145 - self.text.boundingRect().width() - 20, 4)
        self.button = QGraphicsPixmapItem(QPixmap(respath('plus.png')), self)
        self.button.setPos(140, 4)
        self.button.setCursor(Qt.ArrowCursor)
        self.button.mousePressEvent = lambda event: self.callback(self.name)

    def label(self):
        return self.api.sequence.getLabel(self.name)