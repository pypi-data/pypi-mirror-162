"""Test fn debug."""

from service import fn


def test_fn_debug(monkeypatch):
    """Test fn debug."""

    assert not fn.debug()
    monkeypatch.setenv('DEBUG', 'True')
    assert fn.debug()
