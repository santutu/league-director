from leaguedirector.libs.emptyClass import EmptyClass
from leaguedirector.libs.request import Request
import requests


class RequestPost(Request):

    def __init__(self, endpoint, data, certPath, parent=None):
        self.data = data
        Request.__init__(self, endpoint, certPath, parent)

    def run(self):
        try:
            res = requests.post(self.endpoint, data=self.data, verify=self.certPath)
            # res = requests.post(self.endpoint, data=self.data, verify=False)
            res.error = False
        except:
            res = EmptyClass()
            res.error = True

        self.finished.emit(res)
