from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.uix.button import Button
from hotkey import HotKeyBehavior


class HotKeyButton(HotKeyBehavior, Button):
    # make a simple Button that appears with the hotkey "ctrl+alt+space"
    def __init__(self, **kwargs):
        super(HotKeyButton, self).__init__(**kwargs)
        self.key_show="ctrl+alt+space"



kv = """
#: import datetime datetime.datetime

<HotKeyButton>:
    now_show: None
    now_hide: None
    halign: 'center'
    text:
        '''I have been shown on {}
        and
        was hidden for {}'''.format(self.now_show, self.now_show-self.now_hide if self.now_hide and self.now_show else "")
    on_press: self.text = "You can hide the window by closing it (or pressing escape)"
    on_show: self.now_show = datetime.now()
    on_hide: self.now_hide = datetime.now()

"""
Builder.load_string(kv)

if __name__ == "__main__":
    runTouchApp(HotKeyButton())
