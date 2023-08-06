"""Test fn create service."""

from typing import Union

from service import fn


assert Union[fn.ServiceApi, fn.ServiceApp] == fn.Service


def test_fn_create_backend():
    """Test create backend."""

    api = fn.create()
    app = fn.create(api=False)

    assert isinstance(app, fn.ServiceApp)
    assert not isinstance(app, fn.ServiceApi)
    assert isinstance(api, fn.ServiceApi)

    assert isinstance(api.spec, fn.Spec)
    assert isinstance(app.spec, fn.Spec)


def test_fn_create_kwargs():
    """Test create kwargs."""

    _kwargs = {'debug': True}
    api = fn.create(options=_kwargs)
    assert api.debug == _kwargs['debug']
    app = fn.create(options=_kwargs, api=False)
    assert app.debug == _kwargs['debug']
