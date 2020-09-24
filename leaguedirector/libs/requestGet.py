import os
from leaguedirector.libs.request import Request
from PySide2.QtCore import *
import requests


class RequestGet(Request):
    def __init__(self, endpoint, certPath, parent=None):
        Request.__init__(self, endpoint, certPath, parent)

    def run(self):
        res = requests.get(self.endpoint, verify=self.certPath)
        self.finished.emit(res)
