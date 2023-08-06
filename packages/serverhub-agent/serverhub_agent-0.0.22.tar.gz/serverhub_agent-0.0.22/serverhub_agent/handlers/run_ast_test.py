import asyncio
from json import JSONDecodeError

from aiohttp import web
from marshmallow import ValidationError

from serverhub_agent.types.files import AstTests
from serverhub_agent.utils.filesystem import TempFileManager

TESTS_PATH = '/tests'


async def run_ast_test(request: web.Request) -> web.Response:
    body = await request.text()
    try:
        test_data = AstTests.Schema().loads(body)
    except (JSONDecodeError, ValidationError) as e:
        return web.json_response(data=f"Failed to parse ast test data: {e}", status=400)

    files_to_create = [test_data.answer, test_data.user, test_data.precode, test_data.test]

    with TempFileManager(directory=TESTS_PATH, files=files_to_create) as manager:
        ast_command = (
            f"python3 /testlibs/{test_data.testlib_version}.py "
            f"-u {test_data.user.name} "
            f"-a {test_data.answer.name} "
            f"-t {test_data.test.name} "
            f"-pre {test_data.precode.name}"
        )

        proc = await asyncio.create_subprocess_shell(
            f'cd {manager.directory} && exec {ast_command}',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

    return web.json_response({
        "exit_code": proc.returncode,
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
    })
