"""Test fn sentry url."""

from service import fn


def test_fn_sentry_url(monkeypatch):
    """Test fn sentry url - skip for none k8s."""
    url = 'http://custom.sentry.url'

    monkeypatch.setenv('SENTRY_URL', url)
    assert not fn.sentry_url()

    monkeypatch.setenv('KUBERNETES', 'any_value')
    assert fn.running_on_k8s()
    assert fn.sentry_url() == url
