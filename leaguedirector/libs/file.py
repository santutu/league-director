import os


class File:
    baseName: str
    path: str
    extension: str
    pathWithoutExtension: str
    name: str

    def __init__(self, filePath):
        self.path = filePath
        self.baseName = os.path.basename(filePath)
        self.pathWithoutExtension, self.extension = os.path.splitext(filePath)
        self.name, self.extension = os.path.splitext(self.baseName)
