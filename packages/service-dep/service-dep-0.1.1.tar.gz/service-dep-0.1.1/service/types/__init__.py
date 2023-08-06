"""Common types."""

from typing import Literal

from . import api
from . import app
from ..fn import Environment, UserSettings, Spec, languages  # noqa


Lang = Literal[languages()]  # noqa


__all__ = ('Environment', 'UserSettings', 'Spec', 'Lang', 'api', 'app')
