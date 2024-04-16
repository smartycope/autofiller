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
from ezregex import python as er
import argparse


parser = argparse.ArgumentParser(
    prog='autofiller',
    description='A small popup to input various random data for you',
)
parser.add_argument('-d', '--deamon', action='store_true')
parser.add_argument('-m', '--modifier', choices=('meta', 'alt', 'ctrl', 'none'), default='meta')
parser.add_argument('-k', '--key', default='f')

args = parser.parse_args()
keyboard = Keyboard()
mouse = Mouse()

modifiers = {
    "meta": False,
    "ctrl": False,
    "alt": False,
    "none": None,
}


class Window(FramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        w = QWidget(self)
        w.setMaximumSize(0, 0)
        self.setTitleBar(w)

        self.setWindowTitle("autofiller")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setGeometry(*mouse.position, 100, 100)

        self.body()

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

    def body(self):
        layout = QVBoxLayout()

        self.keys = {}

        # To add buttons just add to this, then add to add_random()
        buttons = [
            QPushButton("Add Random Text"),
            QPushButton("Add Random Name"),
            QPushButton("Add Random JSON"),
            QPushButton("Add Random Email"),
        ]

        for cnt, button in enumerate(buttons):
            button.setText(f'{cnt + 1}: ' + button.text())
            type = button.text().split()[-1].lower()
            func = partial(self.add_random, type=type)
            self.keys[(str(cnt+1), type[0])] = func

            button.pressed.connect(func)
            layout.addWidget(button)

        self.window().setLayout(layout)

    def give(self, text):
        self.goaway()
        sleep(.05)
        keyboard.type(text)

    def add_random(self, type):
        match type:
            case 'text':
                regex = (er.match_range(3, 5, er.word_char) + ' ') * randint(1, 5)
                self.give(regex.invert())
            case 'name':
                self.give(random_name.generate_name())
            case 'json':
                self.give('{ "TODO": "Random JSON" }')
            case 'email':
                self.give(er.email.invert())

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
