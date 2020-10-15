import functools
from ctypes import c_ulong, windll, byref
from typing import Dict, List
from PySide2.QtCore import QObject, Signal
from PySide2.QtGui import QKeySequence

from leaguedirector.bindings.keyboardHook import KeyboardHook
from leaguedirector.bindings.shortcut import Shortcut


class Bindings(QObject):
    triggered = Signal(str)
    allowPids: List[int]

    shortcuts: Dict[str, Shortcut]

    def __init__(self, window, bindings, options):
        QObject.__init__(self)
        self.labels = {name: label for name, label, _ in options}
        self.shortcuts = {}
        self.defaults = {}
        self.allowPids = []
        for name, _, default in options:
            if name in bindings:
                hotkey = bindings[name]
            else:
                hotkey = default
            shortcut = Shortcut(hotkey, functools.partial(self.activated, name))

            self.shortcuts[name] = shortcut
            self.defaults[name] = default
        self.hook = KeyboardHook(window)
        self.hook.start()

    def activated(self, name):

        pid = c_ulong()
        windll.user32.GetWindowThreadProcessId(windll.user32.GetForegroundWindow(), byref(pid))

        if pid.value not in self.allowPids:
            return

        if name in self.shortcuts:
            self.triggered.emit(name)

    def getBindings(self):
        return {name: shortcut.hotkey for name, shortcut in self.shortcuts.items()}

    def getOptions(self):
        return [(name, label, self.shortcuts[name].hotkey) for name, label, default in self.options]

    def setBinding(self, name, sequence: QKeySequence):
        self.shortcuts[name].setHotkey(sequence.toString())

    def getLabel(self, name):
        return self.labels[name]

    def setGamePid(self, pids: List[int]):
        self.allowPids = pids
