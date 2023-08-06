from aiohttp import web

from serverhub_agent.handlers.cpp_ws_handler import ws_handler
from serverhub_agent.handlers.ping import ping
from serverhub_agent.handlers.put_files import put_files
from serverhub_agent.handlers.run_ast_test import run_ast_test
from serverhub_agent.handlers.run_code import run_code
from serverhub_agent.handlers.run_script import run_script
from serverhub_agent.handlers.run_test import run_test
from serverhub_agent.handlers.wait_server_ready import wait_server_ready


def setup_routes(app: web.Application) -> None:
    app.router.add_post(f'/put_files/', put_files)
    app.router.add_post(f'/run_script/', run_script)
    app.router.add_get(f'/ping/', ping)
    app.router.add_get(f'/wait_server_ready/', wait_server_ready)
    app.router.add_get('/ws/', ws_handler)
    app.router.add_post('/run_code/', run_code)
    app.router.add_post('/run_test/', run_test)
    app.router.add_post('/run_ast_test/', run_ast_test)
