from typing import ItemsView, Dict

import keyboard

sad: Dict[str, int] = {
    "123": 1

}


def aa():
    print('aa')


keyboard.add_hotkey("Ctrl+v ", aa)
