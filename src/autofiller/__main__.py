# coding:utf-8
from functools import partial
from random import randint
import sys
from time import sleep
from pynput.mouse import Controller as Mouse
from pynput.keyboard import Key, Listener, KeyCode, Controller as Keyboard

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

from qframelesswindow import FramelessWindow
import random_name
from ezregex import python as ez
import argparse
from pathlib import Path
import json

# Parse args
parser = argparse.ArgumentParser(
    prog='quick-assist',
    description='A small popup to input various random data for you',
)
parser.add_argument('-d', '--deamon', action='store_true')
parser.add_argument('-m', '--modifier', choices=('meta', 'alt', 'ctrl', 'none'), default='meta')
parser.add_argument('-k', '--key', default='f')
parser.add_argument('config', type=str, default='~/.config/quick-assist.json', nargs='?')

args = parser.parse_args()
keyboard = Keyboard()
mouse = Mouse()
config = Path(args.config).expanduser()

# Create config if it doesn't exist
if not config.exists():
    config.parent.mkdir(parents=True, exist_ok=True)
    # Copy default config file
    config.write_text((Path(__file__).parent / 'default_config.json').read_text())


# Load config
config = json.loads(config.read_text())

modifiers = {
    "meta": False,
    "ctrl": False,
    "alt":  False,
    "none": None,
}


class Window(FramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        w = QWidget(self)
        w.setMaximumSize(0, 0)
        self.setTitleBar(w)

        self.setWindowTitle("quick-assist")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setGeometry(*mouse.position, 100, 100)

        self.window().setLayout(QVBoxLayout())
        self.open_menu(config)

    def goaway(self):
        if args.deamon:
            self.hide()
        else:
            self.close()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.matches(QKeySequence.StandardKey.Cancel):
            self.goaway()
        else:
            for keys, func in self.keys.items():
                if event.text() in keys:
                    func()

        return super().keyPressEvent(event)

    def open_menu(self, menu_data):
        self.keys = {}
        # Clear layout
        while self.layout().count():
            child = self.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for type, data in menu_data.items():
            # type is the name. The first letter is the key
            # If data is a dict, it's a submenu
            if isinstance(data, dict):
                self.keys[type[0]] = partial(self.open_menu, data)
            # If data is a list, its a sequence of actions
            elif isinstance(data, list):
                self.keys[type[0]] = partial(self.activate_sequence, data)
            # If data is a string, type it
            elif isinstance(data, str):
                self.keys[type[0]] = self.parse_value(data)

            button = QPushButton(type)
            button.pressed.connect(self.keys[type[0]])
            self.layout().addWidget(button)

    def parse_value(self, value):
        """Parse a string from the config, and return a function to execute it"""
        if value.endswith('()'):
            return getattr(self, value[:-2])
        else:
            return partial(self.type, value)

    def type(self, text):
        """Type text and close the window"""
        self.goaway()
        sleep(.05)
        # If it looks like a keyboard sequence, use it
        # if ez.match_range(1, 2, ez.anyof('ctrl', 'alt', 'meta') + ez.ow) + ez.ow + '+' + ez.ow + ez.anyof(ez.word_char).match(text):
        #     keyboard.press(key)
        #     keyboard.release(key)
        # else:
        keyboard.type(text)

    def activate_sequence(self, sequence):
        """Activate a sequence of actions"""
        for action in sequence:
            # If it's a list, it's a mouse move
            if isinstance(action, list):
                mouse.position = action
            # If it's a string, type it, or call a custom method
            elif isinstance(action, str):
                self.parse_value(action)()

    # Custom methods
    def random_name(self):
        self.type(random_name.generate_name())

    def random_email(self):
        regex = ez.word + ez.opt('-' + ez.word) + '@' + ez.word + '.' + ez.anyof('com', 'net', 'org')
        self.type(regex.invert())

    def random_phone(self):
        self.type('123-456-7890')

    def random_address(self):
        self.type('123 Main St, Anytown, USA')

    def random_json(self):
        self.type('{ "TODO": "Random JSON" }')

    def random_text(self):
        regex = (ez.match_range(3, 5, ez.word_char) + ' ') * randint(2, 5)
        self.type(regex.invert()[:-1])



app = QApplication(sys.argv)
window = Window()

def on_press(key:KeyCode):
    global modifiers
    if key in (Key.cmd, Key.cmd_l, Key.cmd_r):
        modifiers['meta'] = True
    elif key in (Key.ctrl, Key.ctrl_l, Key.ctrl_r):
        modifiers['ctrl'] = True
    elif key in (Key.alt, Key.alt_l, Key.alt_r, Key.alt_gr):
        modifiers['alt'] = True

    elif (
        (modifiers[args.modifier] or args.modifier == 'none') and
        (
            (hasattr(Key, args.key) and key == getattr(Key, args.key)) or
            (hasattr(key, 'char') and key.char == args.key)
        )
    ):
        window.show()

def on_release(key):
    global modifiers
    if key in (Key.cmd, Key.cmd_l, Key.cmd_r):
        modifiers['meta'] = False
    elif key in (Key.ctrl, Key.ctrl_l, Key.ctrl_r):
        modifiers['ctrl'] = False
    elif key in (Key.alt, Key.alt_l, Key.alt_r, Key.alt_gr):
        modifiers['alt'] = False


if __name__ == "__main__":
    if args.deamon:
        with Listener(on_press=on_press, on_release=on_release) as listener:
            sys.exit(app.exec())
    else:
        window.show()
        sys.exit(app.exec())
