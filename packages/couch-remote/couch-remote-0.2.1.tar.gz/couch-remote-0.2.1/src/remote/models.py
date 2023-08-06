from pydantic import BaseModel
from pynput.keyboard import Key


class Button(BaseModel):
    """Config entry for key."""
    key: Key
    label: str


class KeyPress(BaseModel):
    """Request/response model for a single key press."""
    key: str
