# HotKeyBehavior
A mixin to make an app appear only after pressing some global HotKey and hide it when closed.

This mixin class can be a good start to build applications 
that appear on demand through hotkey and stay in the background otherwise as:
 - a quick launcher like the Unity launcher or wox (https://github.com/Wox-launcher/Wox)
 - a widget that pops up with information (weather, system ressources, ...)

Its use is very simple:
 1. make your root widget inherit from HotKeyBehavior (should come first in the inheritance order):
 
    ```python
    class HotKeyLabel(HotKeyBehavior, Label):
        text = "Hello world!"

    runTouchApp(HotKeyLabel())
    ```
    
 2. run the code
 3. hit "alt+space" to make the label appear
 4. close the app (it will just hide)
 5. hit again "alt+space" to make the label reappear
 6. close the app (yes, it will still just hide)
 7. hit once more "alt+space" to make the label reappear again
 8. ... (continue having fun)
 
