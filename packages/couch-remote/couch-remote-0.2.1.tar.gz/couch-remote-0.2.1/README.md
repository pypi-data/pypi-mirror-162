# Couch Remote

A utility, available at [pypi](#). Download it on a computer and serve yourself a remote keyboard to control it.

> Current state of things:
> - run `remote` to serve, commands are not supported yet.

## Usage

1. **To install:** `pip install couch-remote` (in a venv or globally)
2. Now, your `remote` should be available.
3. **Optionally,** `remote scaffold-config`, creates a basic settings file, then `remote global settings.py` copies it to a [global configuration directory](#install-a-global-settings-file-pilot-global-settingspy).
4.  **Finally,** `remote control` serves an instance at [localhost:4444](http://localhost:4444). This is the **only** command, you're going to need from now on.

## Settings

And how to set them.

```python
from pynput.keyboard import Key
from remote.models import Button

buttons = {
    'play_pause_media': Button(key=Key.media_play_pause, label='⏯️'),
    'esc': Button(key=Key.esc, label='Esc'),
    'caps': Button(key=Key.caps_lock, label='Caps Lock'),
    'space': Button(key=Key.space, label='Space'),
}

port = 4444
```

Q: Do jakiego formatu zapisują się i wczytują configi w settingsach?


### Install a global settings file `remote global settings.py `

When ran, stores settings at a default path: `~/.config/couch-remote/settings.py`

Pilot will default to this path when not specified.
