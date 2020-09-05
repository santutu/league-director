from PySide2.QtWidgets import QComboBox


class SequenceCombo(QComboBox):
    def __init__(self, api):
        QComboBox.__init__(self)
        self.api = api
        self.update()
        self.api.sequence.namesLoaded.connect(self.update)
        self.activated.connect(self.onActivated)

    def onActivated(self, index):
        self.api.sequence.load(self.itemText(index))

    def showPopup(self):
        self.api.sequence.reloadNames()
        QComboBox.showPopup(self)

    def update(self):
        self.clear()
        for name in self.api.sequence.names:
            self.addItem(name)
        self.setCurrentIndex(self.api.sequence.index)