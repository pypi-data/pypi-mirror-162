"""Test fn testing."""

from service import fn


def test_if_no_testing(mocker):
    """Test fn no."""
    mocker.patch(
        'service.fn._test_module_loaded',
        return_value=False,
    )
    assert not fn.testing()


def test_fn_testing():
    """Test fn default by modules."""
    assert fn.testing()


def test_fn_testing_env(monkeypatch):
    """Test fn testing by env."""
    monkeypatch.setenv('ENVIRONMENT', 'testing')
    assert fn.environment() == 'testing'
    assert fn.testing()
