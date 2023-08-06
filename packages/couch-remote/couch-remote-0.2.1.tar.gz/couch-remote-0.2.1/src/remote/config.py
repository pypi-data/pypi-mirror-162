"""TODO:
   - Link to pynput Key documentation
   - Transform into pydantic Settings object
"""

from pynput.keyboard import Key

from remote.models import Button


buttons = {
    'play_pause_media': Button(key=Key.media_play_pause, label='⏯️'),
    'esc': Button(key=Key.esc, label='Esc'),
    'caps': Button(key=Key.caps_lock, label='Caps Lock'),
    'space': Button(key=Key.space, label='Space'),
}

port = 4444
