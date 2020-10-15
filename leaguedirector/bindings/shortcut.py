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
        return hotkey != ""

    def setHotkey(self, hotkey: str):
        if self.canHotkey(hotkey):
            keyboard.remove_hotkey(self._hotkey)
            self._addHotKey(hotkey, self._callback)
            self._hotkey = hotkey

    def _addHotKey(self, hotkey: str, callback: partial) -> str:
        if self.canHotkey(hotkey):
            keyboard.add_hotkey(hotkey, callback)
        return hotkey
