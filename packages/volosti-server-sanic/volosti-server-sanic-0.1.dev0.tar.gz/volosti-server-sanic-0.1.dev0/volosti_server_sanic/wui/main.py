from typing import TYPE_CHECKING

from sanic import Blueprint
from sanic.response import text
from sanic.views import HTTPMethodView

if TYPE_CHECKING:
    from sanic.request import Request
    from sanic.response import HTTPResponse


class MainPage(HTTPMethodView):
    async def get(self, request: 'Request') -> 'HTTPResponse':
        return text('volosti-server-sanic')


main = Blueprint('main')
main.add_route(MainPage.as_view(), '/')
