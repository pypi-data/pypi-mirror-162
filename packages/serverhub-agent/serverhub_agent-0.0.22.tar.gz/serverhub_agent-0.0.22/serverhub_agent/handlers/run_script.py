import logging

from aiohttp import web

from serverhub_agent.utils.runner import Runner

logger = logging.getLogger(__name__)


async def run_script(request: web.Request) -> web.Response:
    runner = Runner(
        working_dir=request.app["ENTRYPOINT_DIR"],
        script_path=request.app["ENTRYPOINT_PATH"],
        logs_path=request.app['ENTRYPOINT_LOGS_PATH'],
    )
    await runner.run_script()

    return web.json_response({"status": "ok"})
