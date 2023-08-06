import logging
import pathlib

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pynput.keyboard import Key, Controller

from remote import config
from remote.models import KeyPress

__version__ = '0.2.1'

# global_config_path = '~/.config/couch-remote'

log = logging.getLogger(__name__)


class RemoteBackend:
    """
    TODO: Enable adding other backends easily.

    Since I'm aiming at a single config which is independent of the backend, I will probably
    need to map the keys onto something independent like strings instead of the current way of just
    listing pynput.keyboard.Button instances
    """

    def tap(self, key) -> None:
        """Implement this."""
        raise NotImplementedError("This is an abstract backend")


class PynputBackend(RemoteBackend):
    def __init__(self):
        self.keyboard = Controller()
        # handle special keys easily
        # such as  media_play_pause

    def tap(self, key: str) -> None:
        self.keyboard.tap(key)


class UnknownKeyError(Exception):
    pass


class Server:
    """W serverze robi się exposy, więc robi się na klasie dekorator"""
    # @expose(in_model=InModel, out_model=OutModel)
    # def method(self, request: InModel) -> OutModel:
    #     return OutModel()

    def __init__(self, _config):
        self._config = _config
        self._backend = PynputBackend()

    async def tap(self, key_sym: str) -> None:
        key = await self._find_key(key_sym)
        self._backend.tap(key)
        log.info(f'Pressed once: {key}')
        print(f'Pressed once: {key}')

    # TODO: test it?
    async def _find_key(self, key_sym: str) -> Key:
        # Validate
        if key_sym not in self._config.buttons:
            raise UnknownKeyError(key_sym)

        return self._config.buttons[key_sym].key

    async def get_buttons(self):
        return [
            {'label': btn.label, 'value': val}
            for val, btn in self._config.buttons.items()
        ]


# TODO: how to pack this up so that it can be instantiated in __main__?
app = FastAPI()
# Mount static files from remote/statics
app.mount('/static', StaticFiles(packages=['remote']), name='static')
# Add templates from remote/templates
base_dir = pathlib.Path(__file__).parent
template_path = base_dir / 'templates'
templates = Jinja2Templates(directory=template_path)

server = Server(config)


@app.post('/', response_model=KeyPress)
async def tap(kp: KeyPress):
    """On a successful attempt, responds with pressed key."""
    try:
        await server.tap(kp.key)
    except UnknownKeyError:
        raise HTTPException(status_code=404, detail='Unknown key')

    return kp


@app.get('/')
async def index(request: Request):
    """Index page with buttons corresponding to keys."""
    ctx = {
        'request': request,
        'buttons': await server.get_buttons(),
    }
    return templates.TemplateResponse('index.html', context=ctx)
