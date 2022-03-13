from functools import partial

import keyboard


class Shortcut:
    _hotkey: str
    _callback: partial

    def __init__(self, hotkey: str, callback: partial):
        self._addHotKey(hotkey, callback)
        self._callback = callback
        self._hotkey = hotkey

    @property
    def hotkey(self) -> str:
        return self._hotkey

    def canHotkey(self, hotkey: str) -> bool:
        return hotkey != "" and  not hotkey and not isinstance(hotkey, basestring)

    def setHotkey(self, hotkey: str):
        self.removeHotKey()
        try:
            self._addHotKey(hotkey, self._callback)
        except Exception as e:
            print(e)
        self._hotkey = hotkey

    def removeHotKey(self):
        try:
            if self.canHotkey(self._hotkey):
                keyboard.remove_hotkey(self._callback)
        except Exception as e:
            print(e)

    def _addHotKey(self, hotkey: str, callback: partial) -> str:
        if self.canHotkey(hotkey):
            keyboard.add_hotkey(hotkey, callback)
        return hotkey
