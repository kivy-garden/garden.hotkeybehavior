import atexit
import ctypes
import logging
import sys

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

# keyboard control code definitions for registering hotkey through RegisterHotKey
MOD = {"alt": 1, "ctrl": 2, "shift": 4, "win": 8}
KEY = {"space": 0x20, "return": 0x0D, "esc": 0x1B}
KEY.update({chr(i): i for i in range(48, 58)})
KEY.update({chr(i).lower(): i for i in range(65, 91)})


class HotKeyBehavior(object):
    """This mixin class provides HotKey behavior to the app:
    1. the app starts hidden
    2. once the user presses some hotkey, the app is shown
    3. once the user closes the app, the app is hidden, listening again for the hotkey
    (the user can exit the app if it is shown by pressing another keyboard shortcut

    The class should be inherited by the root widget of the kivy app.

    The class provides two string properties:
    - key_show : the keyboard shortcut (hotkey) to show the app (default to 'alt+space')
    - key_exit : the keyboard shortcut to exit the app once visible (default to 'ctrl+c')
    Both shortcuts are of the form : modifier1+modifier2+...+letter.

    The class provides also 4 events:
    - on_show : triggered after the key_show hotkey is pressed and before showing the app
    - on_hide : triggered before hiding the app
    - on_init : triggered at the end of the initialisation of the mixin behavior
    - on_exit : triggered when the user presses the key_exit shortcut

    TODO:
    - implement a "on focus lost" ==> hide the app (but no focus property on the Window)
    - implement other platforms (linux+osx)
    """
    _hwnd = None
    _is_first_lost_skipped = False
    key_show = StringProperty(None)
    key_exit = StringProperty(None)

    def __init__(self, **kwargs):
        # register two new events triggered when the HotKeyBehavior is shown and hidden
        self.register_event_type('on_show')
        self.register_event_type('on_hide')

        # register two new events triggered when the HotKeyBehavior is initialised and stopped
        self.register_event_type('on_init')
        self.register_event_type('on_exit')

        # bind keyboard event to detect key_exit
        Window.request_keyboard(lambda: None, self).bind(on_key_down=self._on_keyboard)

        super(HotKeyBehavior, self).__init__(**kwargs)

    def on_request_close(self, *args, **kwargs):
        # whenever we try to close the app, we hide it instead
        self.hide()

        return True  # avoid really closing the app

    def on_key_exit(self, instance, value):
        self._key_exit = set(value.lower().split("+"))

    def on_show(self, *args, **kwargs):
        pass

    def on_hide(self, *args, **kwargs):
        pass

    def on_init(self, *args, **kwargs):
        pass

    def on_exit(self, *args, **kwargs):
        pass

    def _on_keyboard(self, keyboard, keycode, text, modifiers):
        # check combination of modifiers and text matches exit key
        if {text}.union(modifiers) == self._key_exit:
            self.dispatch("on_exit")
            sys.exit()

        return False

    def on_parent(self, instance, parent):
        # call when the root widget inheriting the mixin behavior
        # is added to App window (parent property changed)

        # only win32 currently supported
        assert sys.platform == 'win32', \
            "Hotkey functionality does not work for your platform '{}'".format(sys.platform)

        # behavior must be inherited by root widget (that has parent Window)
        assert isinstance(parent, type(Window))

        # set window as the foreground window
        if sys.platform == 'win32':
            ctypes.windll.user32.SetForegroundWindow(self._hwnd)

        # set up callbacks once the parent Window is ready
        parent.bind(on_request_close=self.on_request_close)

        # set default values to key if not yet defined
        if self.key_exit is None:
            logging.info("key_exit not defined, default to ctrl+c")
            self.key_exit = "ctrl+c"
        if self.key_show is None:
            logging.info("key_show not defined, default to alt+space")
            self.key_show = "alt+space"

        if sys.platform == 'win32':
            # retrieve hwnd of kivy app
            self._hwnd = ctypes.windll.user32.GetActiveWindow()

            # unregister hotkey
            logging.info("register atexit callback to unregister hotkey")
            atexit.register(ctypes.windll.user32.UnregisterHotKey, None, 1)

        # dispatch event
        self.dispatch("on_init")


        # start hidden
        self.hide()


    def show(self):
        # dispatch the event before showing the window
        # if one has to catch active window
        self.dispatch("on_show")

        # show the main window
        self.parent.show()

    def hide(self):
        # dispatch the event
        self.dispatch("on_hide")

        # hide the app
        self.parent.hide()

        # start listening for hotkey
        Clock.schedule_once(self._listen_hotkey_win32)

    def _listen_hotkey_win32(self, dt):
        msg = ctypes.wintypes.MSG()

        _ = self.key_show.lower().split("+")
        modifier = sum(MOD[k] for k in _[:-1])
        key = KEY[_[-1]]

        # register hotkey
        logging.info("registering hotkey '{}'".format(self.key_show))
        if ctypes.windll.user32.RegisterHotKey(None,  # self.hwnd,
                                               1,  # id of hotkey
                                               modifier,  # 1 = alt
                                               key,  # 32 = vk_space
                                               ) != 1:
            logging.error("could not register hotkey '{}', exiting...".format(self.key_show))
            sys.exit()

        # wait for the HOTKEY message in infinite loop
        while ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0):
            if msg.message == 786:  # 786 = WM_HOTKEY
                if msg.wParam == 1:
                    self.show()
                break

            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

        # unregister hotkey
        logging.info("unregistering current hotkey")
        if ctypes.windll.user32.UnregisterHotKey(None, 1) == 0:
            # unregister did not work meaning HOTKEY was never registered
            # as it is the first time, add the atexit callback
            logging.info("hotkey could not be unregistered")
