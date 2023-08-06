"""Test fn app dir."""

import os
from pathlib import Path
from tempfile import gettempdir
from service import fn


def test_fn_app_dir():
    """Test app dir."""

    assert fn.app_dir() == Path(os.getcwd()).resolve()


def test_paths():
    """Test service paths."""

    paths = fn.paths()

    assert paths.app == fn.app_dir()
    assert paths.tmp == Path(gettempdir()).resolve()
    assert paths.assets == Path(paths.app) / 'assets'
    assert paths.i18n == Path(paths.assets) / 'i18n'
