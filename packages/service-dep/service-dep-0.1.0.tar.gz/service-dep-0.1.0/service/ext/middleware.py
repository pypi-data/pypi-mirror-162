"""Middleware."""

from typing import Tuple

from starlette.requests import Request
from starlette.datastructures import Headers
from starlette.middleware.base import BaseHTTPMiddleware



class HeadersI81n:
    """Check accept-language header and re-pass fault if needed."""

    def __init__(
        self,
        app,
        fallback: str = 'en',
        allowed: Tuple[str] = ('en', ),
    ):
        """Init."""
        self.app = app
        self.fallback = fallback
        self.allowed = allowed

    async def __call__(self, scope, receive, send):
        """Call."""
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        headers = scope.get('headers')
        if not headers:
            scope['headers'] = [(b'accept-language', self.fallback.encode())]
            await self.app(scope, receive, send)
            return

        new_headers = []
        for (header_name, header_value) in headers:
            if header_name == b'accept-language':
                _lang = header_value.decode()
                if len(_lang) != 2 or _lang not in self.allowed:
                    new_headers.append((header_name, self.fallback.encode()))
                else:
                    new_headers.append((header_name, header_value))

        scope['headers'] = new_headers
        await self.app(scope, receive, send)
