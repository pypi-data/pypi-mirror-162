import typing
from starlette.datastructures import MutableHeaders, Secret
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from . import CookieBackend, SessionBackend
from .session import ImproperlyConfigured, Session


class SessionMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        session_cookie: str = "session",
        max_age: int = 14 * 24 * 60 * 60,  # 14 days, in seconds
        same_site: str = "lax",
        https_only: bool = False,
        autoload: bool = False,
        domain: str = None,
        path: str = None,
        secret_key: typing.Union[str, Secret] = None,
        backend: SessionBackend = None,
    ) -> None:
        self.app = app
        if backend is None:
            if secret_key is None:
                raise ImproperlyConfigured("CookieBackend requires secret_key argument.")
            backend = CookieBackend(secret_key, max_age)

        self.backend = backend
        self.session_cookie = session_cookie
        self.max_age = max_age
        self.autoload = autoload
        self.domain = domain
        self.path = path
        self.security_flags = "httponly; samesite=" + same_site
        if https_only:  # Secure flag can be used with HTTPS only
            self.security_flags += "; secure"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        session_id = connection.cookies.get(self.session_cookie, None)

        scope["session"] = Session(self.backend, session_id)
        if self.autoload:
            await scope["session"].load()

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                path = self.path or scope.get("root_path", "") or "/"
                if scope["session"].is_modified and not scope['session'].is_empty:
                    # We have session data to persist (data was changed, cleared, etc).
                    nonlocal session_id
                    session_id = await scope["session"].persist()

                    headers = MutableHeaders(scope=message)
                    header_parts = [
                        f'{self.session_cookie}={session_id}',
                        f'path={path}',
                    ]
                    if self.max_age:
                        header_parts.append(f'Max-Age={self.max_age}')
                    if self.domain:
                        header_parts.append(f'Domain={self.domain}')

                    header_parts.append(self.security_flags)
                    header_value = '; '.join(header_parts)
                    headers.append("Set-Cookie", header_value)
                elif scope["session"].is_loaded and scope["session"].is_empty:
                    if not self.path or self.path and scope['path'].startswith(self.path):
                        # no interactions to session were done
                        headers = MutableHeaders(scope=message)
                        header_value = "{}={}; {}".format(
                            self.session_cookie,
                            f"null; path={path}; expires=Thu, 01 Jan 1970 00:00:00 GMT;",
                            self.security_flags,
                        )
                        headers.append("Set-Cookie", header_value)
                        await self.backend.remove(scope['session'].session_id)
            await send(message)

        await self.app(scope, receive, send_wrapper)
