"""Test fn languages."""

from service import fn


def test_fn_languages(mocker, blank_pyproject_dict):
    """Test fn languages."""
    assert fn.languages() == ('en', )

    blank_pyproject_dict['i18n'] = {
        'default': 'en',
        'support': ['ru'],
        'locales': ['en_US', 'ru_RU'],
    }

    mocker.patch(
        'service.fn.load_pyproject',
        return_value=blank_pyproject_dict,
    )

    assert fn.languages() == ('en', 'ru')
