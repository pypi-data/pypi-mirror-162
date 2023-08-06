"""Common fixtures."""

import os
import json
import pytest

from typing import Dict

from service import fn
from starlette.config import Config


@pytest.fixture
def dot_env_default(mocker):
    """Fixture default env."""
    env_name = fn.env_file()
    mocker.patch(
        'service.fn.config',
        return_value=Config(env_file=env_name, environ=os.environ),
    )

    env_path = fn.app_dir() / env_name
    with open(env_path.as_posix(), 'w') as outfile:
        outfile.write('DEBUG=True')
    yield
    os.remove(env_path.as_posix())


@pytest.fixture
def dot_env_custom(mocker, monkeypatch):
    """Fixture default env."""
    env_alias = '.custom.env'
    monkeypatch.setenv('ENV_FILE', env_alias)

    env_name = fn.env_file()
    mocker.patch(
        'service.fn.config',
        return_value=Config(env_file=env_name, environ=os.environ),
    )

    env_path = fn.app_dir() / env_name
    with open(env_path.as_posix(), 'w') as outfile:
        outfile.write('DEBUG=True')
    yield
    os.remove(env_path.as_posix())


@pytest.fixture
def blank_pyproject_dict() -> Dict:
    """Blank pyproject dict."""
    return {
        'tool': {
            'poetry': {
                'name': 'any-name',
                'version': '0.1.0',
            },
        },
    }


@pytest.fixture
def log_config_custom(monkeypatch):
    """Fixture log config custom."""
    log_config_path = fn.app_dir() / fn.log_config_file_name()

    monkeypatch.setenv('LOG_LEVEL', 'error')
    monkeypatch.setenv('LOG_CONFIG', 'log.yaml')

    with open(log_config_path.as_posix(), 'w') as outfile:
        _config = dict(fn.log_config_blank)
        _config['version'] = 2
        outfile.write(json.dumps(_config))

    yield

    os.remove(log_config_path.as_posix())


@pytest.fixture
def env(monkeypatch):
    """Mock testing environment."""
    os_environment_testing = {
        'environment': 'develop',
        'app_temp_dir': fn.gettempdir(),
        'debug': True,
        'sentry_dsn': 'http://sentry.custom.url',
    }

    for env_name, env_value in os_environment_testing.items():
        monkeypatch.setenv(str(env_name).upper(), str(env_value))
    yield os_environment_testing


@pytest.fixture
def pyproject(mocker, blank_pyproject_dict, env) -> Dict:
    """Fixture pyproject."""

    _config = dict(blank_pyproject_dict)

    _config['project'] = {
        'entrypoint': 'main:app',
        # 'settings': 'main.Settings',
    }

    mocker.patch('service.fn.load_pyproject', return_value=_config)

    return _config


@pytest.fixture
async def app(pyproject) -> fn.Service:
    """App testing fixture."""
    yield fn.create()
