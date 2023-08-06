from typing import TYPE_CHECKING

from starlette.endpoints import HTTPEndpoint
from starlette.responses import PlainTextResponse
from starlette.routing import Mount, Route

if TYPE_CHECKING:
    from starlette.requests import Request


class MainPage(HTTPEndpoint):
    async def get(self, request: 'Request') -> PlainTextResponse:
        return PlainTextResponse('volosti-server-starlette')


main = Mount('/', routes=[
    Route('/', MainPage),
])
