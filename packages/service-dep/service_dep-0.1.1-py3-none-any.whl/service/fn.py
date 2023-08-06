"""Func tools module."""

import os
import sys
import yarl
import yaml
import toml

from typing import Any, Dict, Optional, List, Tuple, Union, Type
from dotenv import load_dotenv
from tempfile import gettempdir
from pathlib import Path
from pydantic import BaseSettings

from starlette.config import Config
from starlette.routing import Router

from ._uses import load_class
from .logging import new_log  # noqa

from ._setup import (
    setup_instance,
    setup_sentry,
    setup_middleware,
    setup_static_translates,
)

from ._define import (
    Service,
    ServiceApp,
    ServiceApi,
    Spec,
    Socket,
    Environment,
    Paths,
    Policy,
    I18n,
    Logging,
    log_config_blank,
    lang_locales,
    UserSettings,  # noqa
    project_file,
)


def env_file() -> str:
    """Env file."""
    return os.environ.get('ENV_FILE', '.env')


config = Config(env_file=env_file(), environ=os.environ)


def _test_module_loaded() -> bool:
    """Test modules loads."""
    loaded_modules = sys.modules.keys()
    modules = (
        '_pytest' in loaded_modules,
        'unittest' in loaded_modules,
    )
    return any(modules)


def app_dir() -> Path:
    """App dir path."""
    return Path(os.getcwd()).resolve()


def load_dot_env_file() -> None:
    """Load dot env file."""
    dot_file_path = Path(app_dir() / env_file()).resolve()
    if dot_file_path.exists():
        load_dotenv(dotenv_path=dot_file_path.as_posix())


load_dot_env_file()


def environment() -> Environment:
    """Get execution environment."""
    return Environment(config('ENVIRONMENT', cast=str, default='unknown'))


def running_on_k8s() -> bool:
    """Is running on k8s."""
    return any([
        True if str(_opt).upper().startswith('KUBERNETES') else False
        for _opt in dict(os.environ).keys()
    ])


def debug() -> bool:
    """Is debug."""
    return config('DEBUG', cast=bool, default=False)


def testing() -> bool:
    """Is testing now."""
    _env = config('ENVIRONMENT', cast=str, default='unknown')
    testing_conditions = (
        _test_module_loaded(),
        str(_env).lower() == 'testing',
    )
    return any(testing_conditions)


def create(
    routers: List[Union[Router, Any]] = None,
    options: Dict = None,
    api: bool = True,
    skip_builtin_middleware: bool = False,
) -> Service:
    """Create service.

    :ara api - use fast-api backend by default or starlette app if not.
    """

    kwargs = options if options else {}

    spec = load_spec()

    app = ServiceApi(**kwargs) if api else ServiceApp(**kwargs)

    setup_instance(app, spec, load_user_settings())

    if routers:
        for router in routers:
            app.include_router(router)

    if not skip_builtin_middleware:
        setup_middleware(app, spec)

    setup_sentry(app, spec)
    setup_static_translates(app, spec)

    return app


def socket() -> Socket:
    """Get socket url."""

    scheme = 'https' if running_on_k8s() else 'http'

    # if needs something special, who knows =\
    scheme = config('SERVICE_SOCKET_SCHEME', cast=str, default=scheme)

    host = config('SERVICE_HOST', cast=str, default='0.0.0.0')
    port = config('SERVICE_PORT', cast=int, default=9990)

    return Socket(
        host=host,
        port=port,
        url=yarl.URL.build(host=host, port=port, scheme=scheme),
    )


def paths() -> Paths:
    """Service paths."""
    tmp_path = Path(config('SERVICE_TMP', cast=str, default=gettempdir()))
    app_path = Path(app_dir()).resolve()
    assets_path = Path(app_path) / 'assets'
    i18n_path = Path(assets_path) / 'i18n'

    return Paths(
        app=app_dir(),
        tmp=tmp_path.resolve(),
        assets=assets_path.resolve(),
        i18n=i18n_path.resolve(),
    )


def sentry_url() -> Optional[str]:
    """Sentry url if assigned for k8s only."""
    if running_on_k8s():
        return config('SENTRY_URL', cast=str, default=None)


def load_pyproject() -> Dict:
    """Load pyproject from file."""
    alias = 'Project file'
    config_path: Path = Path(app_dir() / project_file).resolve()

    try:
        with open(config_path.as_posix()) as config_file:
            return toml.loads(config_file.read())
    except Exception as _load_exc:
        raise RuntimeError(
            f'{alias} load {config_path.as_posix()} with {_load_exc}',
        )


def load_log_config(log_config_path: Path) -> Dict:
    """Load log config."""
    if log_config_path.exists():
        with open(log_config_path.as_posix()) as _file:
            try:
                return yaml.safe_load(_file)
            except Exception as _log_config_exc:
                print(f'Failed load log config: {_log_config_exc}')
                return log_config_blank
    return log_config_blank


def log_config_file_name() -> str:
    """Log config file name."""
    return config(
        'LOG_CONFIG',
        cast=str,
        default='log.yaml',
    )


def logging() -> Logging:
    """Logging."""
    log_config_name = log_config_file_name()
    if not Path(app_dir() / log_config_name).exists():
        log_config_name = None

    return Logging(
        config_file=log_config_name,
        level=config('LOG_LEVEL', cast=str, default='debug'),
    )


def load_spec() -> Spec:
    """Load spec."""
    pyproject = load_pyproject()
    poetry = pyproject.get('tool', {}).get('poetry')

    if not poetry:
        raise RuntimeError(f'Spec: tool.poetry section empty')

    name = poetry.get('name')
    if not name:
        raise RuntimeError(f'Spec: poetry.name empty')

    version = poetry.get('version')
    if not version:
        raise RuntimeError(f'Spec: poetry.version empty')

    description = poetry.get('description', '')

    return Spec(
        name=name,
        version=version,
        description=description,
        debug=debug(),
        environment=environment(),
        pyproject=pyproject,
        i18n=I18n.from_pyproject(pyproject),
        policy=Policy.from_pyproject(pyproject),
        paths=paths(),
        socket=socket(),
        logging=logging(),
        sentry_url=sentry_url(),
    )


def settings_class() -> Optional[str]:
    """User settings class."""
    pyproject = load_pyproject()
    return pyproject.get('project', {}).get('settings')


def load_user_settings() -> Optional[Union[UserSettings, Any]]:
    """Load settings from `module.UserSettingsClassName`."""
    settings, user_class = None, settings_class()
    if not user_class:
        return None

    try:
        settings = load_class(user_class)
    except Exception as _load_user_settings:
        print('Error load settings', _load_user_settings)
        settings = None
    finally:
        return settings() if settings else None


def load_locales() -> Tuple:
    """Load locales like tuple str ('en_US', 'fr_FR', ...)."""

    pyproject = load_pyproject()
    locales = pyproject.get('i18n', {}).get('locales', lang_locales)
    return locales


def languages() -> Tuple[str]:
    """Get languages."""
    _spec = load_spec()
    return tuple(_spec.i18n.languages)
