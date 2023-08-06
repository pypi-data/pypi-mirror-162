"""Test fn env file."""

from service import fn


def test_env_file_default(dot_env_default):  # noqa
    """Test env file default."""

    assert fn.env_file() == '.env'
    assert fn.debug()


def test_env_file_custom(dot_env_custom):  # noqa
    """Test env file custom."""

    assert fn.env_file() == '.custom.env'
    assert fn.debug()
