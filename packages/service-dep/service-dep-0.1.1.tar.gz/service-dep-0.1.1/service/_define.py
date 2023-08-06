"""Service definitions."""

from __future__ import annotations

import os
from typing import Callable, Dict, List, Union, Type, Optional

from enum import Enum
from yarl import URL
from pydantic import BaseSettings as UserSettings
from pathlib import Path
from dataclasses import dataclass
from fastapi import FastAPI as Api
from starlette.applications import Starlette as App


project_file = 'pyproject.toml'

log_config_blank = {
    'version': 1,
    'disable_existing_loggers': False,
}

lang_default = 'en'
lang_support = list()
lang_locales = ['en_US', ]


@dataclass
class I18n:
    """Service I18n options."""

    default: str
    support: List[str]
    locales: List[str]

    languages: List[str]

    @staticmethod
    def from_pyproject(pyproject: Dict) -> I18n:
        """I18n from pyproject."""
        i18n = pyproject.get('i18n', dict())

        _default = i18n.get('default', lang_default)
        _support = i18n.get('support', lang_support)
        _locales = i18n.get('locales', lang_locales)

        _languages = [_default]
        _languages += _support

        return I18n(
            default=_default,
            support=_support,
            locales=_locales,
            languages=_languages,
        )


@dataclass
class Policy:
    """Service policy."""

    workers: int

    request_retry: int
    request_timeout: int

    @staticmethod
    def from_pyproject(config: Dict) -> Policy:
        """Policy from pyproject."""
        policy = config.get('policy', {})
        workers = os.environ.get('WEB_CONCURRENCY')
        if not workers:
            workers = policy.get('workers', 1)

        request_retry = int(policy.get('request_retry', 3))
        request_timeout = int(policy.get('request_timeout', 60))
        return Policy(
            request_retry=request_retry,
            request_timeout=request_timeout,
            workers=int(workers),
        )


class Environment(str, Enum):
    """Environment."""

    unknown = 'unknown'

    testing = 'testing'
    develop = 'develop'

    stage = 'stage'
    pre_stage = 'pre-stage'

    production = 'production'
    pre_production = 'pre-production'


@dataclass
class Socket:
    """Socket."""

    host: str
    port: int
    url: URL


@dataclass
class Paths:
    """App paths."""

    app: Path
    tmp: Path
    assets: Path
    i18n: Path


@dataclass
class Logging:
    """App logging."""

    level: str
    config_file: Optional[str]


@dataclass
class Spec:
    """Service spec."""

    name: str
    version: str
    description: str

    socket: Socket

    i18n: I18n
    policy: Policy
    paths: Paths
    logging: Logging

    pyproject: Dict
    environment: Environment

    debug: bool = False
    sentry_url: str = None


class CoreMixin:
    """Service core mixin."""

    spec: Spec
    settings: Type[UserSettings]
    _: Callable = None


class ServiceApp(CoreMixin, App):
    """Service app mixin."""

    pass


class ServiceApi(CoreMixin, Api):
    """Service api mixin."""

    pass


Service = Union[ServiceApi, ServiceApp]


__all__ = (
    'Api',
    'App',
    'CoreMixin',
    'Service',
    'ServiceApp',
    'ServiceApi',
    'Socket',
    'Spec',
    'Paths',
    'Policy',
    'Logging',
    'log_config_blank',
    'I18n',
    'Environment',
    'UserSettings',
    'project_file',
    'lang_locales',
)
