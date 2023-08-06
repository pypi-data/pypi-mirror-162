"""Service core init."""

import sys
import logging

from .logging import JSONFormatter, ServiceFormatter
from ._define import CoreMixin, Service, ServiceApp, ServiceApi
from ._define import Environment


def exception_hook(exc_type, exc_value, exc_traceback):  # noqa
    """Logging exceptions."""
    logging.exception('Uncaught exception')


sys.excepthook = exception_hook  # noqa

__version__ = '0.1.0'


__all__ = (
    'CoreMixin',
    'Service',
    'ServiceApp',
    'ServiceApi',
    'Environment',
    'JSONFormatter',
    'ServiceFormatter',
)
