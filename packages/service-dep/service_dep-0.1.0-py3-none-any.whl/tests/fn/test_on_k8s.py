"""Test fn on k8s."""

from service import fn


def test_fn_running_on_k8s(monkeypatch):
    """Test fn running on k8s."""

    assert not fn.running_on_k8s()

    monkeypatch.setenv('KUBERNETES', 'any_value')
    assert fn.running_on_k8s()

    monkeypatch.setenv('KUBERNETES_ANY_POST_FIX', 'any_value')
    assert fn.running_on_k8s()
