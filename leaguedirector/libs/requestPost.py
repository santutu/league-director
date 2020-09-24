from leaguedirector.libs.request import Request
from leaguedirector.libs.runnableWithSignals import RunnableWithSignals
from PySide2.QtCore import *
import requests


class RequestPost(Request):

    def __init__(self, endpoint, data, certPath, parent=None):
        self.data = data
        Request.__init__(self, endpoint, certPath, parent)

    def run(self):
        res = requests.post(self.endpoint, data=self.data, verify=self.certPath)
        self.finished.emit(res)
