from PySide2.QtCore import Signal, QEvent
from PySide2.QtWidgets import QWidget, QDoubleSpinBox, QHBoxLayout, QInputDialog

from leaguedirector.widgets import default


class FloatInput(QWidget):
    valueChanged = Signal(float)
    valueAdded = Signal(dict)

    def __init__(self, min_value=None, max_value=None):
        QWidget.__init__(self)
        self.range = None
        self.step = None
        self.spin = QDoubleSpinBox()
        self.spin.valueChanged.connect(self.handleValueChanged)
        self.layout = QHBoxLayout()
        self.layout.setMargin(0)
        self.layout.addWidget(self.spin)
        self.setLayout(self.layout)
        self.setRange(default(min_value, float('-inf')), default(max_value, float('inf')))

        self.spin.installEventFilter(self)

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

        dia = QInputDialog()
        [value, accept] = dia.getInt(self, "Add value", "Value", 0)
        if not accept:
            return
        self.valueAdded.emit(value)

    def handleValueChanged(self, value):
        self.applyRelativeRange()
        self.applyRelativeStep()
        self.valueChanged.emit(value)

    def update(self, value):
        if not self.spin.hasFocus():
            self.blockSignals(True)
            self.spin.setValue(value)
            self.applyRelativeRange()
            self.applyRelativeStep()
            self.blockSignals(False)

    def applyRelativeRange(self):
        if self.range is not None:
            delta = self.spin.value() * self.range
            self.spin.setRange(self.spin.value() - delta, self.spin.value() + delta)

    def applyRelativeStep(self):
        if self.step is not None:
            self.spin.setSingleStep(max(abs(self.spin.value()) * self.step, 1))

    def setRange(self, min_value, max_value):
        self.spin.setRange(min_value, max_value)
        self.range = None

    def setRelativeRange(self, value):
        self.range = value
        self.applyRelativeRange()

    def setSingleStep(self, step):
        self.spin.setSingleStep(step)
        self.step = None

    def setRelativeStep(self, value):
        self.step = value
        self.applyRelativeStep()

    def setSpecialValueText(self, text):
        self.spin.setSpecialValueText(text)

    def setValue(self, value):
        self.spin.setValue(value)

    def value(self):
        return self.spin.value()
