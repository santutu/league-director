from PySide2.QtCore import Signal, QEvent
from PySide2.QtWidgets import QWidget, QDoubleSpinBox, QHBoxLayout, QInputDialog


class VectorInput(QWidget):
    valueChanged = Signal(dict)
    valueAdded = Signal(dict)

    def __init__(self, min_value=None, max_value=None):
        QWidget.__init__(self)
        self.step = None
        self.range = None
        self.x = QDoubleSpinBox()
        self.y = QDoubleSpinBox()
        self.z = QDoubleSpinBox()
        self.x.valueChanged.connect(self.handleValueChanged)
        self.y.valueChanged.connect(self.handleValueChanged)
        self.z.valueChanged.connect(self.handleValueChanged)
        self.layout = QHBoxLayout()
        self.layout.setMargin(0)
        self.layout.addWidget(self.x)
        self.layout.addWidget(self.y)
        self.layout.addWidget(self.z)
        self.setLayout(self.layout)
        min_value = min_value or [float('-inf'), float('-inf'), float('-inf')]
        max_value = max_value or [float('inf'), float('inf'), float('inf')]
        self.setRange(min_value, max_value)

        self.x.installEventFilter(self)
        self.y.installEventFilter(self)
        self.z.installEventFilter(self)

    def eventFilter(self, widget, event):
        if (event.type() == QEvent.ContextMenu and
                isinstance(widget, QDoubleSpinBox)):
            menu = widget.lineEdit().createStandardContextMenu()
            menu.addSeparator()
            menu.addAction('Add Value',
                           self.handleValueAdded)
            menu.exec_(event.globalPos())
            menu.deleteLater()
            return True
        return QWidget.eventFilter(self, widget, event)

    def handleValueAdded(self):

        focus = {
            'x': self.x.hasFocus(),
            'y': self.y.hasFocus(),
            'z': self.z.hasFocus()
        }

        dia = QInputDialog()
        [value, accept] = dia.getInt(self, "Add value", "Value", 0)
        if not accept:
            return

        dictValue = {}

        for k in focus:
            dictValue[k] = value if focus[k] else 0

        self.valueAdded.emit(dictValue)

    def handleValueChanged(self, value):
        self.applyRelativeRange()
        self.applyRelativeStep()
        self.valueChanged.emit(self.value())

    def update(self, value):
        if not self.x.hasFocus() and not self.y.hasFocus() and not self.z.hasFocus():
            self.blockSignals(True)
            self.x.setValue(value['x'])
            self.y.setValue(value['y'])
            self.z.setValue(value['z'])
            self.applyRelativeRange()
            self.applyRelativeStep()
            self.blockSignals(False)

    def applyRelativeRange(self):
        if self.range is not None:
            delta = self.x.value() * self.range
            self.x.setRange(self.x.value() - delta, self.x.value() + delta)
            delta = self.y.value() * self.range
            self.y.setRange(self.y.value() - delta, self.y.value() + delta)
            delta = self.z.value() * self.range
            self.z.setRange(self.z.value() - delta, self.z.value() + delta)

    def applyRelativeStep(self):
        if self.step is not None:
            self.x.setSingleStep(max(abs(self.x.value()) * self.step, 1))
            self.y.setSingleStep(max(abs(self.y.value()) * self.step, 1))
            self.z.setSingleStep(max(abs(self.z.value()) * self.step, 1))

    def setRange(self, min_value, max_value):
        self.x.setRange(min_value[0], max_value[0])
        self.y.setRange(min_value[1], max_value[1])
        self.z.setRange(min_value[2], max_value[2])
        self.range = None

    def setSingleStep(self, step):
        self.x.setSingleStep(step)
        self.y.setSingleStep(step)
        self.z.setSingleStep(step)

    def setRelativeRange(self, value):
        self.range = value
        self.applyRelativeRange()

    def setRelativeStep(self, value):
        self.step = value
        self.applyRelativeStep()

    def setValue(self, value):
        self.x.setValue(value['x'])
        self.y.setValue(value['y'])
        self.z.setValue(value['z'])
        self.applyRelativeRange()
        self.applyRelativeStep()

    def value(self):
        return {
            'x': self.x.value(),
            'y': self.y.value(),
            'z': self.z.value()
        }