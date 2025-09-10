from .lyrics import LYRICS_PLATFORMS
from .placeholders import Placeholders
from .settings import Settings
from .equalizer import (
    get_presets,
    get_preset,
    save_preset,
    delete_preset,
)

__all__ = (
    "LYRICS_PLATFORMS",
    "Placeholders",
    "Settings",
    "get_presets",
    "get_preset",
    "save_preset",
    "delete_preset",
)
