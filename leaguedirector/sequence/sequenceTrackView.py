import copy
import statistics
from operator import attrgetter

from PySide2.QtCore import Signal, Qt, QEvent
from PySide2.QtGui import QPen, QMouseEvent
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QAbstractScrollArea, QApplication, QGraphicsItem

from leaguedirector.libs.memoryCache import MemoryCache
from leaguedirector.sequence.constant import PRECISION, ADJACENT
from leaguedirector.sequence.sequenceKeyframe import SequenceKeyframe
from leaguedirector.sequence.sequenceTime import SequenceTime
from leaguedirector.sequence.sequenceTrack import SequenceTrack
from leaguedirector.widgets import schedule


class SequenceTrackView(QGraphicsView):
    selectionChanged = Signal()

    def __init__(self, api, headers):
        self.api = api
        self.scene = QGraphicsScene()
        QGraphicsView.__init__(self, self.scene)
        self.tracks = {}
        self.timer = schedule(10, self.animate)
        self.scale(1.0 / PRECISION, 1.0)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        for index, name in enumerate(self.api.sequence.keys()):
            track = SequenceTrack(self.api, name, index)
            self.scene.addItem(track)
            self.tracks[name] = track
        self.time = SequenceTime(0, 1, 0, self.scene.height() - 2)
        self.time.setPen(QPen(QApplication.palette().highlight(), 1))
        self.time.setFlags(QGraphicsItem.ItemIgnoresTransformations)
        self.scene.addItem(self.time)
        self.api.playback.updated.connect(self.update)
        self.api.sequence.updated.connect(self.update)
        self.api.sequence.dataLoaded.connect(self.reload)
        headers.addKeyframe.connect(self.addKeyframe)
        headers.verticalScrollBar().valueChanged.connect(lambda value: self.verticalScrollBar().setValue(value))
        self.verticalScrollBar().valueChanged.connect(lambda value: headers.verticalScrollBar().setValue(value))
        self.scene.selectionChanged.connect(self.selectionChanged.emit)

        self.clipboard = MemoryCache()
        self.clipboard.set('copied_key_frames', [])

    def copyKeyframes(self):
        self.clipboard.set('copied_key_frames',
                           [(keyframe.track.name, copy.deepcopy(keyframe.item)) for keyframe in
                            self.selectedKeyframes()])
        return self

    def pasteKeyframes(self):
        keyframes = self.clipboard.get('copied_key_frames')
        for keyframe in keyframes:
            [name, item] = keyframe
            item = copy.deepcopy(item)
            self.api.sequence.appendKeyframe(name, item)
            SequenceKeyframe(self.api, item, self.tracks[name])

    def reload(self):
        for track in self.tracks.values():
            track.reload()

    def selectedKeyframes(self):
        return [key for key in self.scene.selectedItems() if isinstance(key, SequenceKeyframe)]

    def allKeyframes(self):
        return [key for key in self.scene.items() if isinstance(key, SequenceKeyframe)]

    def addKeyframe(self, name):
        self.tracks[name].addKeyframe()

    def clearKeyframes(self):
        for track in self.tracks.values():
            track.clearKeyframes()

    def deleteSelectedKeyframes(self):
        for selected in self.selectedKeyframes():
            selected.delete()

    def selectAllKeyframes(self):
        for child in self.allKeyframes():
            child.setSelected(True)

    def selectAdjacentKeyframes(self):
        for selected in self.selectedKeyframes():
            for child in self.allKeyframes():
                if abs(child.time - selected.time) < ADJACENT:
                    child.setSelected(True)

    def selectNextKeyframe(self):
        selectionSorted = sorted(self.selectedKeyframes(), key=attrgetter('time'))
        trackSelection = {key.track: key for key in selectionSorted}
        for track, selected in trackSelection.items():
            for child in sorted(track.childItems(), key=attrgetter('time')):
                if child.time > selected.time:
                    trackSelection[track] = child
                    break
        self.scene.clearSelection()
        for item in trackSelection.values():
            item.setSelected(True)

    def selectPrevKeyframe(self):
        selectionSorted = sorted(self.selectedKeyframes(), key=attrgetter('time'), reverse=True)
        trackSelection = {key.track: key for key in selectionSorted}
        for track, selected in trackSelection.items():
            for child in sorted(track.childItems(), key=attrgetter('time'), reverse=True):
                if child.time < selected.time:
                    trackSelection[track] = child
                    break
        self.scene.clearSelection()
        for item in trackSelection.values():
            item.setSelected(True)

    def seekSelectedKeyframe(self):
        selected = [key.time for key in self.selectedKeyframes()]
        if selected:
            self.api.playback.pause(statistics.mean(selected))

    def update(self):
        for track in self.tracks.values():
            track.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            QGraphicsView.mousePressEvent(self, QMouseEvent(
                QEvent.GraphicsSceneMousePress,
                event.pos(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier
            ))
        elif event.button() == Qt.LeftButton:
            if event.modifiers() == Qt.ShiftModifier:
                self.setDragMode(QGraphicsView.RubberBandDrag)
                QGraphicsView.mousePressEvent(self, event)
        QGraphicsView.mousePressEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        QGraphicsView.mouseDoubleClickEvent(self, event)
        if not self.scene.selectedItems() and not event.isAccepted():
            self.api.playback.pause(self.mapToScene(event.pos()).x() / PRECISION)

    def mouseReleaseEvent(self, event):
        QGraphicsView.mouseReleaseEvent(self, event)
        self.setDragMode(QGraphicsView.NoDrag)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.scale(1.1, 1.0)
        else:
            self.scale(0.9, 1.0)

    def animate(self):
        self.time.setPos(self.api.playback.currentTime * PRECISION, 0)
