from typing import Optional

from PySide2.QtWidgets import QComboBox

from leaguedirector.libs.file import File
from leaguedirector.utils import getAttributes
from leaguedirector.visible.visible import Visible
from leaguedirector.visible.visibleDataContainer import VisibleDataContainer


class VisibleCombo(QComboBox):
    def __init__(self, visibleDataContainer: VisibleDataContainer, api):
        QComboBox.__init__(self)
        self.api = api
        self.visibleDataContainer = visibleDataContainer
        self.update()
        self.updateUI(self.visibleDataContainer.getFileByName(self.visibleDataContainer.defaultFileName))
        self.visibleDataContainer.changedFiles.connect(self.updateUI)
        self.activated.connect(self.onActivated)
        self.onActivated(self.currentIndex())

    def onActivated(self, index):
        visible = self.visibleDataContainer.getVisibleByName(self.itemText(index))
        for attribute in getAttributes(Visible):
            self.api.render.set(attribute, getattr(visible, attribute))

    def updateUI(self, file: Optional[File]):
        if not file:
            index = 0
        else:
            index = self.visibleDataContainer.getIndexByName(file.name)

        self.clear()
        for file in self.visibleDataContainer.files:
            self.addItem(file.name)
        self.setCurrentIndex(index)

    def currentItemText(self):
        return self.itemText(self.currentIndex())

    def saveCurrentItem(self):
        self.visibleDataContainer.saveFileByNameFromApiVisible(self.currentItemText())

    def newVisible(self, name: str):
        if name.strip() != "":
            self.visibleDataContainer.saveFileByName(name)
        self.onActivated(self.currentIndex())

    def removeCurrentItem(self):
        currentText = self.currentItemText()
        if len(self.visibleDataContainer.files) > 1:
            self.visibleDataContainer.removeByName(currentText)
        self.onActivated(self.currentIndex())
