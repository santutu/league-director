import keyboard


def aa():
    print('aa')

# keyboard.add_hotkey('ctrl+shift+a', print, args=('triggered', 'hotkey'))
keyboard.add_hotkey("ctrl+a", aa)
keyboard.remove_hotkey("ctrl+a")
