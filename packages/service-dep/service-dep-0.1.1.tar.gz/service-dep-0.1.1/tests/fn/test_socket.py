"""Test fn socket."""

from service import fn
from yarl import URL


def test_fn_socket(monkeypatch):
    """Test fn socket."""
    def_host = '0.0.0.0'
    def_port = 9990

    default_socket = fn.socket()
    assert default_socket.host == def_host
    assert default_socket.port == def_port
    assert default_socket.url == URL.build(
        scheme='http',
        port=def_port,
        host=def_host,
    )

    # Check k8s https schema
    monkeypatch.setenv('KUBERNETES', 'any')
    any_socket = fn.socket()
    assert any_socket.host == def_host
    assert any_socket.port == def_port
    assert any_socket.url == URL.build(
        scheme='https',
        port=def_port,
        host=def_host,
    )
