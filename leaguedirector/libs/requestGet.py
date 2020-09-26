import os

from leaguedirector.libs.emptyClass import EmptyClass
from leaguedirector.libs.request import Request
import requests


class RequestGet(Request):
    def __init__(self, endpoint, certPath, parent=None):
        Request.__init__(self, endpoint, certPath, parent)

    def run(self):
        try:
            res = requests.get(self.endpoint, verify=self.certPath)
            res.error = False
        except:
            res = EmptyClass()
            res.error = True

        self.finished.emit(res)
