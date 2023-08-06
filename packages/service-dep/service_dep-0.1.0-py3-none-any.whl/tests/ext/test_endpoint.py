"""Tests for endpoint ext helper."""

import httpx

from logging import getLogger
from pytest import fixture
from pytest_httpx import HTTPXMock

from service.ext.endpoint import Request, Response, bind_endpoint
from service.ext.testing import any_sentence, any_word

APP_LANGUAGE = 'ru'
SUPPORT_LANGUAGES = ('en', 'de', 'fr')
I18N_FIELDS = ('name', 'info')
I18N_MASK_URL = '/{id}/translation/{lang}'

ENTITY_URL = 'http://service.pbilet.com/api/entity'
SERVICE_TOKEN = 'SecretServiceToken'
SERVICE_AUTH_HEADER = {'Authorization': f'Bearer {SERVICE_TOKEN}'}


@fixture
async def endpoint_mock(httpx_mock: HTTPXMock):
    """Mock entity fixture."""

    # store all mocked urls for release response
    registered_urls = []

    # mock pages with limit per page
    pages, limit = 3, 3

    # fill docs like: {'lang_code': {'pk': 'doc'}, ...}
    docs = {_l: dict() for _l in SUPPORT_LANGUAGES}
    docs[APP_LANGUAGE] = dict()

    for page in range(1, pages + 1):

        start_from = 1 if page == 1 else page * limit - limit + 1
        end_to = limit + 1 if page == 1 else page * limit + 1

        page_results = []

        for doc_id in range(start_from, end_to):
            slug = f'slug_{doc_id}'
            doc = {
                'id': doc_id,
                'slug': slug,
                'name': any_word(),
                'info': any_sentence(),
            }

            page_results.append(doc)
            docs[APP_LANGUAGE][doc_id] = doc

            # mock detail by id
            _url_detail_id = f'{ENTITY_URL}/{doc_id}'
            httpx_mock.add_response(
                method='GET',
                url=_url_detail_id,
                json=doc,
                match_headers=SERVICE_AUTH_HEADER,
            )
            registered_urls.append(_url_detail_id)

            # mock detail by slug
            _url_detail_slug = f'{ENTITY_URL}/{slug}'
            httpx_mock.add_response(
                method='GET',
                url=_url_detail_slug,
                json=doc,
                match_headers=SERVICE_AUTH_HEADER,
            )
            registered_urls.append(_url_detail_slug)

            for support_lang in SUPPORT_LANGUAGES:
                i18n_doc = dict(doc)
                i18n_doc['item_id'] = i18n_doc.pop('id', None)  # noqa
                for _field in I18N_FIELDS:
                    i18n_doc[_field] = f'[{support_lang}] {doc[_field]}'

                docs[support_lang][doc_id] = i18n_doc

                # mock i18n header with detail slug response
                auth_lang_headers = dict(SERVICE_AUTH_HEADER)
                auth_lang_headers.update({'Accept-Language': support_lang})
                httpx_mock.add_response(
                    method='GET',
                    url=_url_detail_slug,
                    json=i18n_doc,
                    match_headers=auth_lang_headers,
                )
                registered_urls.append(_url_detail_slug)

                # mock i18n header with detail pk response
                auth_lang_headers = dict(SERVICE_AUTH_HEADER)
                auth_lang_headers.update({'Accept-Language': support_lang})
                httpx_mock.add_response(
                    method='GET',
                    url=_url_detail_id,
                    json=i18n_doc,
                    match_headers=auth_lang_headers,
                )
                registered_urls.append(_url_detail_id)

                # mock i18n pk with lang param
                _url_i18n_pk_param = f'{_url_detail_id}?lang={support_lang}'
                httpx_mock.add_response(
                    method='GET',
                    url=_url_i18n_pk_param,
                    json=i18n_doc,
                    match_headers=SERVICE_AUTH_HEADER,
                )
                registered_urls.append(_url_i18n_pk_param)

                # mock i18n slug with lang param
                _url_i18n_slug_param = f'{_url_detail_slug}?lang={support_lang}'
                httpx_mock.add_response(
                    method='GET',
                    url=_url_i18n_slug_param,
                    json=i18n_doc,
                    match_headers=SERVICE_AUTH_HEADER,
                )
                registered_urls.append(_url_i18n_slug_param)

                _url_custom = I18N_MASK_URL.format(id=doc_id, lang=support_lang)
                _url_custom = f'{ENTITY_URL}{_url_custom}'
                httpx_mock.add_response(
                    method='GET',
                    url=_url_custom,
                    json=i18n_doc,
                    match_headers={},
                )
                registered_urls.append(_url_custom)

        if page == 1:
            # first page without page param
            httpx_mock.add_response(
                method='GET',
                url=ENTITY_URL,
                json={
                    'data': {
                        'page': page,
                        'last_page': pages,
                        'results': page_results,
                    },
                },
                match_headers=SERVICE_AUTH_HEADER,
            )
            registered_urls.append(ENTITY_URL)

        # register all pages py num
        page_url = f'{ENTITY_URL}?page={page}'
        registered_urls.append(page_url)

        # mock page data
        httpx_mock.add_response(
            method='GET',
            url=page_url,
            json={
                'data': {
                    'page': page,
                    'last_page': pages,
                    'results': page_results,
                },
            },
            match_headers=SERVICE_AUTH_HEADER,
        )

    yield

    # release mocked responses
    async with httpx.AsyncClient(headers=SERVICE_AUTH_HEADER) as client:
        for reg_url in registered_urls:
            await client.get(reg_url)
            for support_lang in SUPPORT_LANGUAGES:
                await client.get(
                    reg_url,
                    headers={'Accept-Language': support_lang},
                )


def test_request_params():
    """Test request params."""
    mock_params = {'new_only': True}
    request = Request(url=ENTITY_URL, action='Test', params=mock_params)
    assert request.params == mock_params


def test_request_headers():
    """Test request headers."""
    mock_headers = {'Accepted-Language': 'ru'}
    request = Request(url=ENTITY_URL, action='Test', headers=mock_headers)
    assert request.headers == mock_headers


def test_request_payload():
    """Test request payload."""
    _url = f'{ENTITY_URL}/same/'
    _payload = {'foo': 'bar'}
    request = Request(url=_url, action='Test', payload=_payload)
    assert request.payload == _payload


async def test_request_get_success(httpx_mock: HTTPXMock):
    """Test request get success."""
    params = {
        'url': 'http://example.com',
        'json': {'payload': 'data'},
        'status_code': 200,
    }

    httpx_mock.add_response(method='GET', **params)

    request = Request(url=params['url'], action='Test request')
    response: Response = await request.get()
    assert response.data == params['json']
    assert response.status == params['status_code']
    assert not response.error


async def test_request_get_fail(httpx_mock: HTTPXMock):
    """Test request get success."""
    ext_logger = getLogger('service.ext.endpoint')

    params = {'url': f'{ENTITY_URL}/bad/', 'status_code': 401}
    httpx_mock.add_response(method="GET", **params)

    request = Request(url=params['url'], action='Test bad request')

    # skip log errors
    ext_logger.disabled = True
    response: Response = await request.get()
    ext_logger.disabled = False

    assert response.data is None
    assert response.status == params['status_code']
    assert 'not success' in response.error


async def test_endpoint_smoke():
    """Test endpoint smoke."""
    header_name = 'X-HEADER-CUSTOM'
    header_value = f'{header_name}-VALUE'

    endpoint = bind_endpoint(
        url=ENTITY_URL,
        token=SERVICE_TOKEN,
        headers={header_name: header_value},
    )

    assert endpoint.headers['Authorization'] == f'Bearer {SERVICE_TOKEN}'
    assert endpoint.url == ENTITY_URL
    assert endpoint.headers[header_name] == header_value

    with_param = bind_endpoint(
        url=ENTITY_URL,
        token=SERVICE_TOKEN,
        i18n={
            'lang': APP_LANGUAGE,
            'i18n_url': None,
            'i18n_support': SUPPORT_LANGUAGES,
            'fields': I18N_FIELDS,
            'use_url': False,
            'use_param': True,
            'use_headers': False,
        },
    )

    with_header = bind_endpoint(
        url=ENTITY_URL,
        token=SERVICE_TOKEN,
        i18n={
            'lang': APP_LANGUAGE,
            'i18n_url': None,
            'i18n_support': SUPPORT_LANGUAGES,
            'fields': I18N_FIELDS,
            'use_url': False,
            'use_param': False,
            'use_headers': True,
        },
    )

    with_url = bind_endpoint(
        url=ENTITY_URL,
        token=SERVICE_TOKEN,
        i18n={
            'lang': APP_LANGUAGE,
            'i18n_url': I18N_MASK_URL,
            'i18n_support': SUPPORT_LANGUAGES,
            'fields': I18N_FIELDS,
            'use_url': True,
            'use_param': False,
            'use_headers': False,
        },
    )

    assert with_param.i18n.fields == I18N_FIELDS
    assert with_param.i18n.lang == APP_LANGUAGE
    assert with_param.i18n.i18n_support == SUPPORT_LANGUAGES
    assert with_param.i18n.use_param
    assert not with_param.i18n.i18n_url
    assert not with_param.i18n.use_headers
    assert not with_param.i18n.use_url

    assert with_header.i18n.fields == I18N_FIELDS
    assert with_header.i18n.lang == APP_LANGUAGE
    assert with_header.i18n.i18n_support == SUPPORT_LANGUAGES
    assert with_header.i18n.use_headers
    assert not with_header.i18n.use_param
    assert not with_header.i18n.i18n_url
    assert not with_header.i18n.use_url

    assert with_url.i18n.fields == I18N_FIELDS
    assert with_url.i18n.lang == APP_LANGUAGE
    assert with_url.i18n.i18n_support == SUPPORT_LANGUAGES
    assert with_url.i18n.use_url
    assert with_url.i18n.i18n_url
    assert not with_url.i18n.use_headers
    assert not with_url.i18n.use_param


async def test_endpoint_lookup_pk_default(endpoint_mock):  # noqa
    """Test endpoint lookup by id."""
    endpoint = bind_endpoint(url=ENTITY_URL, token=SERVICE_TOKEN)

    list_pk = await endpoint.list_pk()
    docs = [await endpoint.doc(pk) for pk in list_pk]
    for doc in docs:
        assert str(doc['id']) in list_pk


async def test_endpoint_lookup_pk_overload(endpoint_mock):  # noqa
    """Test endpoint lookup pk alias."""
    pk_alias = 'slug'
    endpoint = bind_endpoint(url=ENTITY_URL, token=SERVICE_TOKEN)
    list_pk = await endpoint.list_pk(pk=pk_alias)
    docs = [await endpoint.doc(pk) for pk in list_pk]
    for doc in docs:
        assert str(doc[pk_alias]) in list_pk


async def test_endpoint_lookup_translate_by_param(endpoint_mock):  # noqa
    """Test endpoint lookup with translates by param."""
    endpoint = bind_endpoint(
        url=ENTITY_URL,
        token=SERVICE_TOKEN,
        i18n={
            'lang': APP_LANGUAGE,
            'fields': I18N_FIELDS,
            'i18n_support': SUPPORT_LANGUAGES,
            'i18n_url': None,
            'use_param': True,
            'use_url': False,
            'use_headers': False,
        },
    )

    list_pk = await endpoint.list_pk()
    docs = [await endpoint.doc(pk) for pk in list_pk]

    for _ in docs:
        for lang in SUPPORT_LANGUAGES:
            i18n = await endpoint.translate(pk=_['id'], lang=lang, cached=_)
            for field in I18N_FIELDS:
                assert lang in i18n[field]


async def test_endpoint_lookup_translate_by_header(endpoint_mock):  # noqa
    """Test endpoint lookup with translates by header."""
    endpoint = bind_endpoint(
        url=ENTITY_URL,
        token=SERVICE_TOKEN,
        i18n={
            'lang': APP_LANGUAGE,
            'fields': I18N_FIELDS,
            'i18n_support': SUPPORT_LANGUAGES,
            'i18n_url': None,
            'use_param': False,
            'use_url': False,
            'use_headers': True,
        },
    )

    list_pk = await endpoint.list_pk()
    docs = [await endpoint.doc(pk) for pk in list_pk]

    for _ in docs:
        for lang in SUPPORT_LANGUAGES:
            i18n = await endpoint.translate(pk=_['id'], lang=lang, cached=_)
            for field in I18N_FIELDS:
                assert lang in i18n[field]


async def test_endpoint_lookup_translate_by_url(endpoint_mock):  # noqa
    """Test endpoint lookup with translates by url."""
    endpoint = bind_endpoint(
        url=ENTITY_URL,
        token=SERVICE_TOKEN,
        i18n={
            'lang': APP_LANGUAGE,
            'fields': I18N_FIELDS,
            'i18n_support': SUPPORT_LANGUAGES,
            'i18n_url': I18N_MASK_URL,
            'use_param': False,
            'use_url': True,
            'use_headers': False,
        },
    )

    list_pk = await endpoint.list_pk()
    docs = [await endpoint.doc(pk) for pk in list_pk]

    for _ in docs:
        for lang in SUPPORT_LANGUAGES:
            i18n = await endpoint.translate(pk=_['id'], lang=lang, cached=_)
            for field in I18N_FIELDS:
                assert lang in i18n[field]
