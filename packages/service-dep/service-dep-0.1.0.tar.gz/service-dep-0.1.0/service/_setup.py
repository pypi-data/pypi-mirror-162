import i18n

from typing import Dict

from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.logging import LoggingIntegration

from service._define import Spec, Service

from .ext.middleware import HeadersI81n


def setup_instance(app: Service, spec: Spec, user_settings: Dict = None) -> None:
    """Setup app instance."""

    app.spec = spec
    app.settings = user_settings
    app.title = app.spec.name
    app.version = app.spec.version


def setup_static_translates(app: Service, spec: Spec) -> None:
    """Setup static translates."""

    if spec.paths.i18n.exists():
        i18n.set('filename_format', '{locale}.{format}')
        i18n.set('file_format', 'json')
        i18n.set('enable_memoization', True)

        available_locales = [spec.i18n.default]
        available_locales += spec.i18n.support

        i18n.set('skip_locale_root_data', True)

        i18n.set('locale', spec.i18n.default)
        i18n.set('fallback', spec.i18n.default)
        i18n.set('available_locales', spec.i18n.languages)

        i18n.load_path.append(spec.paths.i18n.as_posix())

        app._ = i18n.t


def setup_sentry(app: Service, spec: Spec) -> None:
    """Setup sentry."""

    if spec.sentry_url:
        try:
            sentry_init(
                dsn=spec.sentry_url,
                server_name=spec.name,
                release=spec.version,
                environment=spec.environment,
                attach_stacktrace=True,
                integrations=[LoggingIntegration()],
                request_bodies='always',
                with_locals=spec.debug,
            )
        except Exception as sentry_exc:
            print(f'Setup sentry: {sentry_exc}')


def setup_middleware(app: Service, spec: Spec) -> None:
    """Setup middleware."""

    app.add_middleware(
        HeadersI81n,
        fallback=spec.i18n.default,
        allowed=tuple(spec.i18n.languages),
    )
