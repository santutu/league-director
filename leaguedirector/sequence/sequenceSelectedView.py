import threading
import webbrowser

from PySide2.QtWidgets import QWidget, QFormLayout, QLabel, QComboBox, QPushButton, QStyle

from leaguedirector.widget.vectorInput import VectorInput
from leaguedirector.widgets import HBoxWidget, BooleanInput, ColorInput
from leaguedirector.widget.floatInput import FloatInput


class SequenceSelectedView(QWidget):
    def __init__(self, api, tracks):
        QWidget.__init__(self)
        self.api = api
        self.api.playback.updated.connect(self.update)
        self.api.sequence.updated.connect(self.update)
        self.tracks = tracks
        self.tracks.selectionChanged.connect(self.update)
        self.form = QFormLayout(self)
        self.setLayout(self.form)
        self.layout()
        self.update()

    def layout(self):
        self.label = QLabel()
        self.time = FloatInput()
        self.blend = QComboBox()
        self.value = HBoxWidget()
        self.valueLabel = QLabel('Multiple Selected')
        self.valueFloat = FloatInput()
        self.valueBool = BooleanInput()
        self.valueVector = VectorInput()
        self.valueColor = ColorInput()
        self.value.addWidget(self.valueLabel)
        self.value.addWidget(self.valueFloat)
        self.value.addWidget(self.valueBool)
        self.value.addWidget(self.valueVector)
        self.value.addWidget(self.valueColor)
        self.blend.activated.connect(self.updateBlend)
        for option in self.api.sequence.blendOptions:
            self.blend.addItem(option)

        self.blendHelp = QPushButton()
        self.blendHelp.setFixedWidth(20)
        self.blendHelp.setIcon(self.style().standardIcon(QStyle.SP_TitleBarContextHelpButton))
        self.blendHelp.clicked.connect(self.openBlendHelp)

        self.form.addRow('', self.label)
        self.form.addRow('Time', self.time)
        self.form.addRow('Blend', HBoxWidget(self.blend, self.blendHelp))
        self.form.addRow('Value', self.value)

        self.time.valueChanged.connect(self.updateTime)
        self.valueFloat.valueChanged.connect(self.updateValue)
        self.valueBool.valueChanged.connect(self.updateValue)
        self.valueVector.valueChanged.connect(self.updateValue)
        self.valueColor.valueChanged.connect(self.updateValue)
        self.blend.activated.connect(self.updateBlend)

        self.valueVector.valueAdded.connect(self.addValueVector)
        self.valueFloat.valueAdded.connect(self.addValueFloat)

    def openBlendHelp(self):
        threading.Thread(target=lambda: webbrowser.open_new('https://easings.net')).start()

    def update(self):
        selected = self.tracks.selectedKeyframes()
        self.setVisible(len(selected))
        self.time.setRange(0, self.api.playback.length)

        blending = list(set([key.blend for key in selected]))
        self.label.setText("{} keyframes selected".format(len(selected)))
        if len(blending) == 1:
            self.blend.setCurrentText(blending[0])
        else:
            self.blend.setCurrentIndex(-1)

        times = list(set([key.time for key in selected]))
        if len(times):
            self.time.update(times[0])

        if len(set([key.valueType for key in selected])) == 1:
            valueType = selected[0].valueType
            if valueType == 'float':
                self.valueFloat.update(selected[0].value)
                self.valueLabel.setVisible(False)
                self.valueFloat.setVisible(True)
                self.valueBool.setVisible(False)
                self.valueVector.setVisible(False)
                self.valueColor.setVisible(False)
            elif valueType == 'bool':
                self.valueBool.update(selected[0].value)
                self.valueLabel.setVisible(False)
                self.valueFloat.setVisible(False)
                self.valueBool.setVisible(True)
                self.valueVector.setVisible(False)
                self.valueColor.setVisible(False)
            elif valueType == 'vector':
                self.valueVector.update(selected[0].value)
                self.valueLabel.setVisible(False)
                self.valueFloat.setVisible(False)
                self.valueBool.setVisible(False)
                self.valueVector.setVisible(True)
                self.valueColor.setVisible(False)
            elif valueType == 'color':
                self.valueColor.update(selected[0].value)
                self.valueLabel.setVisible(False)
                self.valueFloat.setVisible(False)
                self.valueBool.setVisible(False)
                self.valueVector.setVisible(False)
                self.valueColor.setVisible(True)
        else:
            self.valueLabel.setVisible(True)
            self.valueFloat.setVisible(False)
            self.valueBool.setVisible(False)
            self.valueVector.setVisible(False)
            self.valueColor.setVisible(False)

    def updateTime(self):
        for item in self.tracks.selectedKeyframes():
            item.time = self.time.value()

    def updateValue(self, value):
        for item in self.tracks.selectedKeyframes():
            item.value = value

    def addValueVector(self, value):
        for item in self.tracks.selectedKeyframes():
            item.value = {
                'x': item.value['x'] + value['x'],
                'y': item.value['y'] + value['y'],
                'z': item.value['z'] + value['z'],
            }

    def addValueFloat(self, value):
        for item in self.tracks.selectedKeyframes():
            item.value += value

    def updateBlend(self, index):
        for item in self.tracks.selectedKeyframes():
            item.blend = self.blend.itemText(index)
