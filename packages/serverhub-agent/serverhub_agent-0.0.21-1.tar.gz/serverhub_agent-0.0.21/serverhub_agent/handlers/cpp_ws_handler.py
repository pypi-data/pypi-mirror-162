import logging

from aiohttp.web import Request, WebSocketResponse

from serverhub_agent.ws.ws_server import WsServer

logger = logging.getLogger(__name__)


async def ws_handler(request: Request) -> WebSocketResponse:
    ws_server: WsServer = request.app['ws_server']
    return await ws_server.connect(request)  # runs until socket is closed by the client
