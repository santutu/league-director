from typing import List, Optional
import json

from PySide2 import QtCore
from PySide2.QtCore import Signal

from leaguedirector.libs.file import File
from leaguedirector.utils import getFilePaths, getFiles, getAttributes
from leaguedirector.visible.visible import Visible
from leaguedirector.visible.visibleScheme import VisibleScheme
from leaguedirector.widgets import userpath
import os


class VisibleDataContainer(QtCore.QObject):
    dirPath = None
    files: List[File] = []

    _visibleScheme = VisibleScheme()

    changedFiles = Signal(File)

    defaultFileName = 'default'

    def __init__(self, dirPath: str, api):
        super().__init__()
        self.dirPath = dirPath
        self.api = api
        self.loadFiles()
        if len(self.files) == 0:
            self.saveFileByName(self.defaultFileName, Visible())

        if not os.path.exists(self.dirPath):
            os.mkdir(self.dirPath)

    def getIndexByName(self, name: str):
        i = -1
        for file in self.files:
            i += 1
            if file.name == name:
                return i
        return 0

    def loadFiles(self):
        self.files =  getFiles(self.dirPath)
        return self.files

    def getVisibleByName(self, name: str) -> Visible:
        filePath = self.getFilePathByName(name)

        return self._visibleScheme.loadFromJsonFile(filePath)

    def getFilePathByName(self, name: str):
        return os.path.join(self.dirPath, name + ".json")

    def getFileByName(self, name: str):
        for file in self.files:
            if file.name == name:
                return file

        return None

    def saveFileByName(self, name: str, visible: Optional[Visible] = None):
        filePath = self.getFilePathByName(name)

        if visible is None:
            visible = Visible()
        self._visibleScheme.saveToJson(filePath, visible)
        self.loadFilesAndEmitChangedFiles(name)

    def saveFileByNameFromApiVisible(self, name: str):
        visible = Visible()
        for attribute in getAttributes(Visible):
            setattr(visible, attribute, self.api.render.get(attribute))

        self.saveFileByName(name, visible)

    def removeByName(self, name: str):
        os.remove(self.getFilePathByName(name))
        self.loadFilesAndEmitChangedFiles(name)

    def loadFilesAndEmitChangedFiles(self, name: str):
        self.loadFiles()
        self.changedFiles.emit(self.getFileByName(name))
