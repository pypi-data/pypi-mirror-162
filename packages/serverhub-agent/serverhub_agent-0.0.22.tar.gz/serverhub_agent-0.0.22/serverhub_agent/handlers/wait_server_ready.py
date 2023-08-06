import logging
from typing import List

from aiohttp import web

from serverhub_agent.utils.waiter import (PortConfig, ServerWaiter,
                                          WaitingProtocol)

logger = logging.getLogger(__name__)


async def wait_server_ready(request: web.Request) -> web.Response:
    ports_to_wait: List[PortConfig] = [
        PortConfig(port, WaitingProtocol.port_up.name)
        for port in request.app["PORTS_TO_WAIT"] if port
    ]
    ports_to_wait += [
        PortConfig(port, WaitingProtocol.port_responding.name)
        for port in request.app["PORTS_TO_WAIT_RESPONDING"] if port
    ]
    all_up = await ServerWaiter(ports_to_wait, request.app["STARTUP_TIMEOUT"]).wait_for_ports()
    if all_up:
        return web.json_response({"status": "ok"})
    else:
        raise web.HTTPGatewayTimeout()
