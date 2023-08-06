import logging
from asyncio import CancelledError

from aiohttp.web import WebSocketResponse

from serverhub_agent.types.exceptions import ClosedSocket
from serverhub_agent.ws.ws_messages import Command, Error, Types

logger = logging.getLogger(__name__)


async def send_command_to_socket(command: Command, socket: WebSocketResponse):
    try:
        await socket.send_json(Command.Schema().dump(command))
    except Exception as e:
        logger.info(f'on write to socket error {e}')
        raise ClosedSocket()


async def send_error_to_socket(error: Error, socket: WebSocketResponse):
    cmd = Command(type=Types.ERROR, data=error)
    await send_command_to_socket(cmd, socket)


def no_except(fun):
    async def wrapper(*args, **kwargs):
        try:
            return await fun(*args, **kwargs)
        except CancelledError as e:
            raise e
        except Exception as e:
            logger.error(f'fun [{fun.__name__}] caught an unexpected exception of type [{type(e)}] data [{str(e)}]')
            return None

    return wrapper
