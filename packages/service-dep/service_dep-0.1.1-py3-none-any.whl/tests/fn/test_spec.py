"""Test fn spec."""

import toml

from copy import deepcopy
from tempfile import gettempdir
from pathlib import Path
from service import fn


def test_fn_load_spec():
    """Test fn load spec."""

    spec = fn.load_spec()
    spec_file = fn.app_dir() / fn.project_file

    with open(spec_file.resolve()) as toml_file:

        pyproject = toml.loads(toml_file.read())

        assert pyproject['tool']['poetry']['name'] == spec.name
        assert pyproject['tool']['poetry']['version'] == spec.version
        assert pyproject['tool']['poetry']['description'] == spec.description

        assert spec.socket == fn.socket()

        # Check logging
        assert spec.logging.level == 'debug'
        assert not spec.logging.config_file
        # assert spec.logging.config['version'] == 1
        # assert not spec.logging.config['disable_existing_loggers']

        # check paths
        assert spec.paths.app == fn.app_dir()
        assert spec.paths.assets == Path(fn.app_dir()) / 'assets'
        assert spec.paths.i18n == Path(spec.paths.assets) / 'i18n'
        assert spec.paths.tmp == Path(gettempdir()).resolve()

        # i18n check default not set
        assert spec.i18n.default == 'en'
        assert spec.i18n.support == list()
        assert spec.i18n.locales == ['en_US']
        assert spec.i18n.languages == ['en']

        # policy check default not set
        assert spec.policy.workers == 1
        assert spec.policy.request_retry == 3
        assert spec.policy.request_timeout == 60


def test_fn_spec_i18n(mocker, blank_pyproject_dict):
    """Test fn spec with i18n extra."""
    blank = deepcopy(blank_pyproject_dict)

    blank['i18n'] = {
        'default': 'de',
        'support': ['en', 'fr'],
        'locales': ['en_US', 'de_DE', 'fr_FR'],
    }

    mocker.patch('service.fn.load_pyproject', return_value=blank)

    spec = fn.load_spec()

    assert spec.i18n.default == blank['i18n']['default']
    assert spec.i18n.support == blank['i18n']['support']
    assert spec.i18n.locales == blank['i18n']['locales']
    languages = [blank['i18n']['default']]
    languages += blank['i18n']['support']
    assert spec.i18n.languages == languages


def test_fn_spec_policy(mocker, blank_pyproject_dict):
    """Test fn spec with Policy extra."""
    blank = deepcopy(blank_pyproject_dict)

    blank['policy'] = {
        'workers': 3,
        'request_retry': 1,
        'request_timeout': 30,
    }

    mocker.patch('service.fn.load_pyproject', return_value=blank)

    spec = fn.load_spec()

    assert spec.policy.workers == 3
    assert spec.policy.request_retry == 1
    assert spec.policy.request_timeout == 30


def test_fn_spec_logging(log_config_custom):  # noqa
    """Test fn spec with Logging extra."""

    spec = fn.load_spec()

    assert spec.logging.level == 'error'
    assert spec.logging.config_file
