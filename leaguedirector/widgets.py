import os
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *


def schedule(interval, callback):
    timer = QTimer()
    timer.timeout.connect(callback)
    timer.start(interval)
    return timer


def respath(*args):
    directory = os.path.abspath(os.path.join(os.curdir, 'resources'))
    return os.path.join(directory, *args)


def userpath(*args):
    base = os.path.expanduser('~/Documents/LeagueDirector')
    path = os.path.abspath(os.path.join(base, *args))
    if '.' in os.path.basename(path):
        directory = os.path.dirname(path)
    else:
        directory = path
    if not os.path.exists(directory):
        os.makedirs(directory)
    return path


def default(value1, value2):
    return value1 if value1 is not None else value2


class Separator(QFrame):
    def __init__(self):
        QFrame.__init__(self)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class HBoxWidget(QWidget):
    def __init__(self, *widgets):
        QWidget.__init__(self)
        self.layout = QHBoxLayout()
        self.layout.setMargin(0)
        self.setLayout(self.layout)
        for widget in widgets:
            self.addWidget(widget)

    def addWidget(self, widget):
        self.layout.addWidget(widget)


class VBoxWidget(QWidget):
    def __init__(self, *widgets):
        QWidget.__init__(self)
        self.layout = QVBoxLayout()
        self.layout.setMargin(0)
        self.setLayout(self.layout)
        for widget in widgets:
            self.addWidget(widget)

    def addWidget(self, widget):
        self.layout.addWidget(widget)


class FloatSlider(QWidget):
    valueChanged = Signal(float)

    def __init__(self, label, precision=5):
        QWidget.__init__(self)

        self.updating = False
        self.precision = 10 ** precision
        self.label = QLabel(label)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTracking(True)
        self.input = QDoubleSpinBox()

        self.slider.valueChanged.connect(self.sliderValueChanged)
        self.input.valueChanged.connect(self.inputValueChanged)

        self.layout = QHBoxLayout()
        self.layout.setMargin(0)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.input)
        self.setLayout(self.layout)

    def sliderValueChanged(self):
        value = float(self.slider.value()) / self.precision
        self.input.blockSignals(True)
        self.input.setValue(value)
        self.input.blockSignals(False)
        self.valueChanged.emit(value)

    def inputValueChanged(self):
        value = self.input.value()
        self.slider.blockSignals(True)
        self.slider.setValue(value * self.precision)
        self.slider.blockSignals(False)
        self.valueChanged.emit(value)

    def setRange(self, min_value, max_value):
        self.slider.setRange(min_value * self.precision, max_value * self.precision)
        self.input.setRange(min_value, max_value)

    def setSingleStep(self, step):
        self.input.setSingleStep(step)

    def setValue(self, value):
        self.slider.setValue(value)
        self.input.setValue(value)

    def value(self):
        return self.input.value()

    def update(self, value):
        if not self.slider.isSliderDown() and not self.input.hasFocus():
            self.blockSignals(True)
            self.setValue(value)
            self.blockSignals(False)


class BooleanInput(QWidget):
    valueChanged = Signal(bool)

    def __init__(self, text=''):
        QWidget.__init__(self)
        self.checkbox = QCheckBox(text)
        self.checkbox.stateChanged.connect(self.handleValueChanged)
        self.label = QLabel('')
        self.layout = QHBoxLayout()
        self.layout.setMargin(0)
        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def handleValueChanged(self, state):
        self.valueChanged.emit(bool(state == Qt.Checked))

    def update(self, value):
        self.blockSignals(True)
        self.checkbox.setCheckState(Qt.Checked if value else Qt.Unchecked)
        self.blockSignals(False)

    def setValue(self, value):
        self.checkbox.setCheckState(Qt.Checked if value else Qt.Unchecked)

    def value(self):
        return bool(self.checkbox.checkState() == Qt.Checked)

    def toggle(self):
        self.setValue(not self.value())

    def setText(self, text):
        self.label.setText(text)

    def setCheckboxText(self, text):
        self.checkbox.setText(text)


class ColorInput(QWidget):
    valueChanged = Signal(dict)

    def __init__(self):
        QWidget.__init__(self)
        self.r = QSpinBox()
        self.g = QSpinBox()
        self.b = QSpinBox()
        self.a = QSpinBox()
        self.dialog = QColorDialog()
        self.dialog.setModal(True)
        self.dialog.setOption(QColorDialog.ShowAlphaChannel)
        self.dialog.setOption(QColorDialog.NoButtons)
        self.dialog.setOption(QColorDialog.DontUseNativeDialog)
        self.palette = QPalette()
        self.button = QPushButton()
        self.button.setFlat(True)
        self.button.setAutoFillBackground(True)
        self.button.setFixedSize(QSize(18, 18))
        self.r.setRange(0, 255)
        self.g.setRange(0, 255)
        self.b.setRange(0, 255)
        self.a.setRange(0, 255)
        self.r.valueChanged.connect(self.handleValueChanged)
        self.g.valueChanged.connect(self.handleValueChanged)
        self.b.valueChanged.connect(self.handleValueChanged)
        self.a.valueChanged.connect(self.handleValueChanged)
        self.dialog.currentColorChanged.connect(self.handleColorPicked)
        self.button.clicked.connect(self.dialog.show)
        self.layout = QHBoxLayout()
        self.layout.setMargin(0)
        self.layout.addWidget(self.r)
        self.layout.addWidget(self.g)
        self.layout.addWidget(self.b)
        self.layout.addWidget(self.a)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    def handleValueChanged(self, value):
        self.palette.setColor(QPalette.Button, self.color())
        self.button.setPalette(self.palette)
        self.valueChanged.emit(self.value())

    def handleColorPicked(self):
        self.blockSignals(True)
        color = self.dialog.currentColor()
        self.r.setValue(color.red())
        self.g.setValue(color.green())
        self.b.setValue(color.blue())
        self.a.setValue(color.alpha())
        self.blockSignals(False)
        self.valueChanged.emit(self.value())

    def update(self, value):
        if not self.r.hasFocus() and not self.g.hasFocus() and not self.b.hasFocus() and not self.a.hasFocus():
            self.blockSignals(True)
            self.r.setValue(value['r'] * 255)
            self.g.setValue(value['g'] * 255)
            self.b.setValue(value['b'] * 255)
            self.a.setValue(value['a'] * 255)
            self.blockSignals(False)

    def setValue(self, value):
        self.r.setValue(value['r'] * 255)
        self.g.setValue(value['g'] * 255)
        self.b.setValue(value['b'] * 255)
        self.a.setValue(value['a'] * 255)

    def value(self):
        return {
            'r': float(self.r.value()) / 255,
            'g': float(self.g.value()) / 255,
            'b': float(self.b.value()) / 255,
            'a': float(self.a.value()) / 255
        }

    def color(self):
        return QColor(self.r.value(), self.g.value(), self.b.value(), self.a.value())
