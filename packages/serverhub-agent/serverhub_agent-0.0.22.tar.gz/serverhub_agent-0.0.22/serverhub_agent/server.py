import logging

from aiohttp import web

from serverhub_agent.routes import setup_routes
from serverhub_agent.settings import _env_variables, init_settings_from_env
from serverhub_agent.utils.filesystem import FileSystem
from serverhub_agent.ws.output_processor import BaseOutputProcessor
from serverhub_agent.ws.ws_server import WsServer

AGENT_PORT = 3030


async def _init_ws_server(app):
    app['ws_server'] = WsServer(app)


async def _stop_ws_server(app):
    await app['ws_server'].stop()


def run_server(
        env_settings=True,                          # get all settings from env variables
        ws_server=True,                             # start websocket server
        fs_exposed_dir='/app/',                     # root dir of all files put through handler /put_files/
        entrypoint_dir='/.utils/',                  # cwd of the script running after /run_script/
        request_max_body_size_mb=30,                # max body size of any request to agent
        startup_timeout=50,                         # /wait_server_started/ returns after waiting max seconds specified
        ports_to_wait=None,                         # ports to wait become *up* (default [3000])
        ports_to_wait_responding=None,              # ports to wait become *responding* (default [])
        proc_mem_limit_mb=512,                      # memory limit of process spawned through websocket
        wait_on_put=True,                           # wait server, before updating files with /put_files/
        interpreter_name='python',                  # interpreter used in /run_code/
        script_name='__test.py',                    # script name used in /run_code/
        entrypoint_path='/.utils/entrypoint.sh',    # script name to run on call /run_script/
        entypoint_logs_path='/.utils/logs',         # path to the file where entrypoint's logs will be stored
        proc_output_limit=2 ** 20,                  # max number of bytes in output
        proc_output_buffer_size=2 ** 16,            # max number of bytes in output per line
        output_processor_cls=BaseOutputProcessor,   # used to decode process's output into messages
        template_path=None,                         # path to get template to wrap code in (required)
        testlib_default_version='0.0.1',            # testlib default version used in python based trainers
        import_snippet_path='/.utils/testlib_import_snippet.py',    # path to get import snippet for py based trainers
):
    if ports_to_wait is None:
        ports_to_wait = [3000]
    if ports_to_wait_responding is None:
        ports_to_wait_responding = []

    logging.basicConfig(level=logging.DEBUG)

    REQUEST_MAX_BODY_SIZE_MB = _env_variables.REQUEST_MAX_BODY_SIZE_MB if env_settings else request_max_body_size_mb
    app = web.Application(client_max_size=REQUEST_MAX_BODY_SIZE_MB * 2 ** 20)

    if env_settings:
        init_settings_from_env(app)
    else:
        app['FS_EXPOSED_DIR'] = fs_exposed_dir
        app['ENTRYPOINT_DIR'] = entrypoint_dir
        app['REQUEST_MAX_BODY_SIZE_MB'] = request_max_body_size_mb
        app['STARTUP_TIMEOUT'] = startup_timeout
        app['PORTS_TO_WAIT'] = ports_to_wait
        app['PORTS_TO_WAIT_RESPONDING'] = ports_to_wait_responding
        app['PROC_MEM_LIMIT_MB'] = proc_mem_limit_mb
        app['WAIT_ON_PUT'] = wait_on_put
        app['INTERPRETER_NAME'] = interpreter_name
        app['SCRIPT_NAME'] = script_name
        app['ENTRYPOINT_PATH'] = entrypoint_path
        app['ENTRYPOINT_LOGS_PATH'] = entypoint_logs_path
        app['PROC_OUTPUT_LIMIT'] = proc_output_limit
        app['PROC_OUTPUT_BUFFER_SIZE'] = proc_output_buffer_size
        app['OUTPUT_PROCESSOR_CLS'] = output_processor_cls
        app['TEMPLATE_PATH'] = template_path
        app['TESTLIB_DEFAULT_VERSION'] = testlib_default_version
        app['IMPORT_SNIPPET_PATH'] = import_snippet_path

    app['filesystem'] = FileSystem(root_dir=app['FS_EXPOSED_DIR'])

    if ws_server:
        app.on_startup.append(_init_ws_server)
        app.on_shutdown.append(_stop_ws_server)

    setup_routes(app)

    web.run_app(
        app,
        host='0.0.0.0',
        port=AGENT_PORT,
    )
