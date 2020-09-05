from PySide2.QtCore import Signal, Qt
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene

from leaguedirector.sequence.sequenceHeader import SequenceHeader


class SequenceHeaderView(QGraphicsView):
    addKeyframe = Signal(str)

    def __init__(self, api):
        self.api = api
        self.scene = QGraphicsScene()
        QGraphicsView.__init__(self, self.scene)
        self.setFixedWidth(162)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        for index, name in enumerate(self.api.sequence.keys()):
            self.scene.addItem(SequenceHeader(self.api, name, index, self.addKeyframe.emit))