"""Request-response and endpoint bindings."""

from copy import deepcopy
from dataclasses import dataclass

from typing import Dict, Optional, List, Sequence, Type, Tuple
from logging import getLogger

from httpx import AsyncClient, AsyncHTTPTransport, codes

from service import fn

spec = fn.load_spec()
log = getLogger(__name__)

SUCCESS_CODES = (
    codes.OK,
    codes.CREATED,
    codes.ACCEPTED,
    codes.NON_AUTHORITATIVE_INFORMATION,
    codes.NO_CONTENT,
    codes.RESET_CONTENT,
    codes.PARTIAL_CONTENT,
    codes.MULTI_STATUS,
    codes.ALREADY_REPORTED,
    codes.IM_USED,
)


@dataclass(frozen=True)
class Response:
    """Response binding."""

    status: int
    data: Optional[Dict]
    error: Optional[str]


@dataclass(frozen=True)
class Request:
    """Request binding."""

    url: str

    action: str = 'Request'

    headers: Dict = None
    params: Dict = None
    payload: Dict = None

    def request_dict(self) -> Dict:
        """Request options as dict."""
        _options = {}
        if self.headers and isinstance(self.headers, dict):
            _options['headers'] = self.headers
        if self.params and isinstance(self.params, dict):
            _options['params'] = self.params
        if self.payload and isinstance(self.payload, dict):
            _options['data'] = self.payload
        return _options

    @classmethod
    def get_transport(cls, retries: int) -> AsyncHTTPTransport:
        """Get http transport."""
        return AsyncHTTPTransport(retries=retries)

    async def get(
        self,
        retries: int = 3,
        success_codes: Tuple[int] = SUCCESS_CODES,
    ) -> Response:
        """Get method."""
        _json, _error, _status = None, None, 500

        options = self.request_dict()
        transport = self.get_transport(retries=retries)
        log_info = {
            'request_url': self.url,
            'request_options': options,
        }

        try:
            async with AsyncClient(transport=transport) as client:
                _response = await client.get(self.url, **options)
                _status = _response.status_code

                log_info['response_status'] = _status

                if _response.status_code in success_codes:
                    _json = _response.json()
                    if spec.debug:
                        log_info['response_json'] = _json
                else:
                    _error = f'Response status is not success: {_status}'

        except Exception as _err_request:
            log_info['exception'] = _err_request
            _json, _error, _status = None, str(_err_request), 500
        finally:
            if _error:
                log.error(f'{self.action}: {_error}', extra=log_info)
            else:
                log.debug(self.action, extra=log_info)

            return Response(data=_json, error=_error, status=_status)


@dataclass
class Param18n:
    """i18n params."""

    fields: Sequence[str]

    lang: str = 'ru'

    i18n_support: Sequence[str] = ('en', )
    i18n_url: str = None

    use_headers: bool = True
    use_param: bool = False
    use_url: bool = False


@dataclass
class Endpoint:
    """Endpoint binding."""

    url: str

    pk: str = 'id'

    headers: Dict = None
    i18n: Type[Param18n] = None

    async def paginate(
        self,
        page: int,
        pk: str = None,
    ) -> Tuple[int, List[str]]:
        """Check if response is paginated.
        Returns last_page count and list pk from first page.
        """
        params = {'page': page}
        options = {'url': self.url, 'headers': self.headers, 'params': params}

        request = Request(**options)
        response: Response = await request.get()

        last_page, results = 0, []
        if not response.error and response.data:
            page_data = response.data.get('data', {})
            last_page = page_data.get('last_page', 0)
            results = page_data.get('results', [])

        fail_conditions = (
            bool(response.error),
            len(results) == 0,
            last_page == 0,
        )

        if any(fail_conditions):
            return 0, []

        if pk:
            list_pk = [str(doc.get(pk)) for doc in results]
        else:
            list_pk = [str(doc.get(self.pk)) for doc in results]

        return last_page, list_pk

    async def list_pk(self, pk: str = None) -> List[str]:
        """List entity pk."""
        last_page, list_pk = await self.paginate(page=1, pk=pk)

        if last_page == len(list_pk) == 0:
            return []

        for page in range(2, last_page + 1):
            _, page_pks = await self.paginate(page=page, pk=pk)
            if page_pks and len(page_pks) > 0:
                list_pk += page_pks

        return list(set(list_pk))

    async def doc(self, pk: str) -> Optional[Dict]:
        """Doc by pk."""
        url = f'{self.url}/{pk}'
        options = {
            'action': f'Request doc {self.pk}={pk}',
            'url': url,
            'headers': self.headers,
        }
        request = Request(**options)
        response: Response = await request.get()
        if response.data and not response.error:
            return response.data

    async def translate(
        self,
        pk: str,
        lang: str,
        cached: Dict = None,
    ) -> Optional[Dict]:
        """Translate by pk."""
        assert self.i18n

        # use cached original response or retrieve new
        origin = deepcopy(cached) if cached else await self.doc(pk)
        if not origin:
            return

        i18n_url = f'{self.url}/{pk}'
        if self.i18n.use_url:
            _part = {self.pk: pk, 'lang': lang}
            i18n_rel = self.i18n.i18n_url.format(**_part)
            i18n_url = f'{self.url}{i18n_rel}'

        action = f'Request {lang} i18n {self.pk}={pk}, cached={bool(cached)}'

        options = {
            'action': action,
            'url': i18n_url,
            'headers': self.headers or dict(),
            'params': dict(),
        }

        if self.i18n.use_headers:
            options['headers']['Accept-Language'] = lang

        if self.i18n.use_param:
            options['params']['lang'] = lang

        request = Request(**options)
        response: Response = await request.get()
        if response.error or not response.data:
            return origin

        for i18n_field in self.i18n.fields:
            if i18n_field in response.data:
                origin[i18n_field] = response.data[i18n_field]

        return origin


def bind_endpoint(
    url: str,
    pk: str = 'id',
    token: str = None,
    i18n: Dict = None,
    headers: Dict = None,
    **kwargs,  # noqa
) -> Endpoint:
    """Bind endpoint lookup."""
    _options = {'url': url, 'pk': pk}
    _headers = dict(headers) if headers else dict()

    if token:
        _headers.update({'Authorization': f'Bearer {token}'})

    _options['headers'] = _headers
    _options['i18n'] = None

    if i18n:
        i18n_url = i18n.get('i18n_url', '/{id}/translation/{lang}')
        assert 'fields' in i18n
        _options['i18n'] = Param18n(
            i18n_url=i18n_url,
            fields=i18n['fields'],
            lang=i18n.get('lang', spec.i18n.default),
            i18n_support=i18n.get('i18n_support', spec.i18n.support),
            use_headers=i18n.get('use_headers', True),
            use_param=i18n.get('use_param', False),
            use_url=i18n.get('use_url', False),
        )

    return Endpoint(**_options)
