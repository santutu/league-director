from PySide2 import QtCore, QtGui


class RunnableWithSignals(QtCore.QObject, QtCore.QRunnable):
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        QtCore.QRunnable.__init__(self, parent)
