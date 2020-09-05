from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QGraphicsPixmapItem, QGraphicsItem, QApplication

from leaguedirector.sequence.sequenceTime import SequenceTime
from leaguedirector.sequence.constant import PRECISION, SNAPPING
from leaguedirector.widgets import respath


class SequenceKeyframe(QGraphicsPixmapItem):

    def __init__(self, api, item, track):
        self.pixmapNormal = QPixmap(respath('kfnormal.png'))
        self.pixmapOverlap = QPixmap(respath('kfoverlap.png'))
        QGraphicsPixmapItem.__init__(self, self.pixmapNormal, track)
        self.api = api
        self.track = track
        self.item = item
        self.duplicate = None
        self.setCursor(Qt.ArrowCursor)
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        flags = QGraphicsItem.ItemIgnoresTransformations
        flags |= QGraphicsItem.ItemIsMovable
        flags |= QGraphicsItem.ItemIsSelectable
        flags |= QGraphicsItem.ItemSendsGeometryChanges
        self.setFlags(flags)
        self.setOffset(-10, 3)
        self.update()

    def viewport(self):
        return self.scene().views()[0]

    @property
    def time(self):
        return self.item['time']

    @time.setter
    def time(self, value):
        if self.item['time'] != value:
            self.item['time'] = value
            self.api.sequence.update()
            self.track.updateOverlap()
            self.update()

    @property
    def valueType(self):
        value = self.item['value']
        if isinstance(value, float):
            return 'float'
        elif isinstance(value, bool):
            return 'bool'
        elif isinstance(value, dict):
            if 'x' in value and 'y' in value and 'z' in value:
                return 'vector'
            if 'r' in value and 'g' in value and 'b' in value and 'a' in value:
                return 'color'
        return ''

    @property
    def value(self):
        return self.item['value']

    @value.setter
    def value(self, value):
        if self.item['value'] != value:
            self.item['value'] = value
            self.api.sequence.update()
            self.update()

    @property
    def blend(self):
        return self.item.get('blend')

    @blend.setter
    def blend(self, value):
        if self.item.get('blend') != value:
            self.item['blend'] = value
            self.api.sequence.update()
            self.update()

    def update(self):
        self.setPos(int(self.time * PRECISION), 0)
        self.setToolTip(self.tooltip())

    def tooltip(self):
        value = self.value
        if isinstance(value, dict):
            value = tuple(value.values())
        return 'Time: {}\nBlend: {}\nValue: {}'.format(self.time, self.blend, value)

    def delete(self):
        self.api.sequence.removeKeyframe(self.track.name, self.item)
        self.scene().removeItem(self)

    def setOverlapping(self, overlapping):
        self.setPixmap(self.pixmapOverlap if overlapping else self.pixmapNormal)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and event.modifiers() == Qt.NoModifier:
            if len(self.scene().selectedItems()) < 2:
                self.api.playback.pause(self.time)
                event.accept()
        QGraphicsPixmapItem.mouseDoubleClickEvent(self, event)

    def mouseReleaseEvent(self, event):
        for key in self.scene().selectedItems():
            if isinstance(key, SequenceKeyframe):
                key.duplicate = None
        QGraphicsPixmapItem.mouseReleaseEvent(self, event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            value.setX(self.performSnapping(value.x()))
            value.setX(max(0, value.x()))
            value.setY(0)
            self.performDuplication()
            return value
        elif change == QGraphicsItem.ItemPositionHasChanged:
            if value:
                self.time = value.x() / PRECISION
        return QGraphicsPixmapItem.itemChange(self, change, value)

    def performDuplication(self):
        if self.isSelected() and self.duplicate is None:
            if QApplication.mouseButtons() == Qt.LeftButton:
                if QApplication.keyboardModifiers() == Qt.AltModifier:
                    self.duplicate = self.track.duplicateKeyframe(self)

    def performSnapping(self, time):
        if QApplication.mouseButtons() == Qt.LeftButton:
            if QApplication.keyboardModifiers() == Qt.NoModifier:
                if len(self.scene().selectedItems()) < 2:
                    scene = self.scene()
                    viewport = self.viewport()
                    screenPosition = viewport.mapFromScene(time, 0).x()
                    left = viewport.mapToScene(screenPosition - SNAPPING, 0).x()
                    right = viewport.mapToScene(screenPosition + SNAPPING, 0).x()
                    items = scene.items(left, float(0), right - left, scene.height(), Qt.IntersectsItemBoundingRect,
                                        Qt.AscendingOrder)
                    for item in items:
                        if isinstance(item, SequenceKeyframe):
                            if item != self and not item.isSelected() and item.track != self.track:
                                return item.x()
                        elif isinstance(item, SequenceTime):
                            return self.api.playback.time * PRECISION
        return time
