"""Test fn load user settings."""

from service import fn


class Settings(fn.UserSettings):
    """User settings third party."""

    setting: str = 'value'


def test_settings_no_set():
    """Test fn test settings when not set."""
    assert not fn.load_user_settings()


def test_fn_user_settings(mocker):
    """Test fn load user settings."""
    mocker.patch(
        'service.fn.settings_class',
        return_value='tests.fn.test_user_settings.Settings',
    )

    assert fn.load_user_settings() == Settings()
