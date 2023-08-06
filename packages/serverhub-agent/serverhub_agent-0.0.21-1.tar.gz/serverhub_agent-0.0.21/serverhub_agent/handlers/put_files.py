import logging
from json import JSONDecodeError
from typing import Any, List

from aiohttp import web
from marshmallow import ValidationError

from serverhub_agent.types.handlers.common import build_drf_err
from serverhub_agent.types.handlers.put_files import PutFilesRequest
from serverhub_agent.utils.filesystem import FileSystem
from serverhub_agent.utils.runner import Runner
from serverhub_agent.utils.waiter import (PortConfig, ServerWaiter,
                                          WaitingProtocol)

logger = logging.getLogger(__name__)


async def put_files(request: web.Request) -> web.Response:  # TODO: i think we should use some auth here later
    """ Puts files to the specified dir inside the container """
    try:
        validated = PutFilesRequest.Schema().load(await request.json())  # type: (PutFilesRequest, Any)
    except (JSONDecodeError, ValidationError) as e:
        logger.warning(f'failed to deserialize request with error [{e}]')
        raise build_drf_err(code='', message=f"failed to deserialize request")

    # check that server is running, before we will update files
    if request.app['WAIT_ON_PUT']:
        server_ports_to_wait: List[PortConfig] = [
            PortConfig(port, WaitingProtocol.port_up.name)
            for port in request.app['PORTS_TO_WAIT'] if port
        ]
        server_ports_to_wait += [
            PortConfig(port, WaitingProtocol.port_responding.name)
            for port in request.app['PORTS_TO_WAIT_RESPONDING'] if port
        ]
        logger.info(f'server ports [{server_ports_to_wait}] {request.app["PORTS_TO_WAIT"]}')

        server_is_up = await ServerWaiter(server_ports_to_wait, 3).wait_for_ports()
        logger.warning(f"server ports: {server_ports_to_wait} is {'ready' if server_is_up else 'down'}")

        utils_ports_to_wait: List[PortConfig] = [
            PortConfig(port, WaitingProtocol.port_up.name)
            for port in [3001, 3002, 3003]  # TODO set only needed ports
        ]
        logger.info(f'utils ports [{utils_ports_to_wait}]')
        utils_is_up = await ServerWaiter(utils_ports_to_wait, 3).wait_for_ports()
        logger.warning(f"utils ports: {utils_ports_to_wait} is {'ready' if utils_is_up else 'down'}")

    fs = FileSystem(root_dir=request.app['FS_EXPOSED_DIR'])
    try:
        fs.create_files(validated.files)
    except ValueError as e:
        logger.warning(f'failed to store files with error [{e}]')
        raise build_drf_err(code='', message=f"messy file structure")

    if request.app['WAIT_ON_PUT'] and utils_is_up and not server_is_up:
        script_path = f"{request.app['ENTRYPOINT_DIR']}run_user_server.sh"
        logger.warning(f"all environment is up, except user server. rerun [{script_path}]")
        runner = Runner(
            working_dir=request.app['ENTRYPOINT_DIR'],
            script_path=script_path,
            logs_path=request.app['ENTRYPOINT_LOGS_PATH'],
        )
        await runner.run_script()

    return web.json_response({"status": "ok"})
