import copy
from operator import methodcaller

from PySide2.QtCore import QTimer, QPointF
from PySide2.QtGui import QPen, QColor, QLinearGradient, QGradient, QBrush
from PySide2.QtWidgets import QGraphicsRectItem

from leaguedirector.sequence.constant import PRECISION, OVERLAP
from leaguedirector.sequence.sequenceKeyframe import SequenceKeyframe


class SequenceTrack(QGraphicsRectItem):
    height = 22

    def __init__(self, api, name, index):
        QGraphicsRectItem.__init__(self)
        self.api = api
        self.name = name
        self.index = index
        self.setPos(0, self.height * self.index)
        self.setToolTip(self.api.sequence.getLabel(self.name))
        self.setPen(QPen(QColor(70, 70, 70, 255)))
        self.updateOverlapTimer = QTimer()
        self.updateOverlapTimer.timeout.connect(self.updateOverlapNow)
        self.updateOverlapTimer.setSingleShot(True)
        self.gradient = QLinearGradient(QPointF(0, 0), QPointF(120 * PRECISION, 0))
        self.gradient.setColorAt(0, QColor(30, 30, 30, 255))
        self.gradient.setColorAt(0.49999999999999, QColor(30, 30, 30, 255))
        self.gradient.setColorAt(0.5, QColor(40, 40, 40, 255))
        self.gradient.setColorAt(1, QColor(40, 40, 40, 255))
        self.gradient.setSpread(QGradient.RepeatSpread)
        self.setBrush(QBrush(self.gradient))
        self.reload()
        self.update()

    def viewport(self):
        return self.scene().views()[0]

    def paint(self, *args):
        self.updateOverlap()
        return QGraphicsRectItem.paint(self, *args)

    def reload(self):
        for item in self.childItems():
            if isinstance(item, SequenceKeyframe):
                self.scene().removeItem(item)
        for item in self.api.sequence.getKeyframes(self.name):
            SequenceKeyframe(self.api, item, self)

    def addKeyframe(self):
        item = self.api.sequence.createKeyframe(self.name)
        return SequenceKeyframe(self.api, item, self)

    def duplicateKeyframe(self, keyframe):
        item = copy.deepcopy(keyframe.item)
        self.api.sequence.appendKeyframe(self.name, item)
        return SequenceKeyframe(self.api, item, self)

    def clearKeyframes(self):
        for item in self.childItems():
            if isinstance(item, SequenceKeyframe):
                item.delete()

    def updateOverlapNow(self):
        viewport = self.viewport()
        distance = viewport.mapToScene(OVERLAP, 0).x() - viewport.mapToScene(0, 0).x()
        previous = None
        for child in sorted(self.childItems(), key=methodcaller('x')):
            if isinstance(child, SequenceKeyframe):
                if previous and abs(child.x() - previous.x()) < distance:
                    child.setOverlapping(True)
                    previous.setOverlapping(True)
                else:
                    child.setOverlapping(False)
                previous = child

    def updateOverlap(self):
        self.updateOverlapTimer.start(100)

    def update(self):
        self.setRect(0, 0, int(self.api.playback.length * PRECISION), self.height)