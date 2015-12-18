from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.uix.label import Label

from hotkey import HotKeyBehavior


class HotKeyLabel(HotKeyBehavior, Label):
    text = "Hello world!"


if __name__ == "__main__":
    runTouchApp(HotKeyLabel())
