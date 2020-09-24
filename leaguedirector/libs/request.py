from leaguedirector.libs.runnableWithSignals import RunnableWithSignals
from PySide2.QtCore import Signal
import os


class Request(RunnableWithSignals):
    finished = Signal(object)

    def __init__(self, endpoint, certPath, parent=None):
        self.endpoint = endpoint
        self.certPath = certPath
        RunnableWithSignals.__init__(self, parent)
