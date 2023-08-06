import asyncio
import os

from aiohttp import web


def read_template(template_filename: str) -> str:
    try:
        with open(template_filename) as template_file:
            return template_file.read()
    except IOError:
        raise FileNotFoundError(f'Can\'t find template {template_filename} in docker image')


async def run_code(request: web.Request) -> web.Response:
    body = await request.json()
    code = body['code']
    lib_version = body['lib_version']

    template_path = request.app['TEMPLATE_PATH']

    if template_path is None:
        raise FileNotFoundError(
            'Web_server lesson type requires code template file inside docker container',
        )

    is_py_trainer = template_path.endswith('.py')

    # оборачиваем код в шаблон; кодируем, если шаблон на питоне
    wrapped_code = read_template(template_path).format(
        test_code=code.encode() if is_py_trainer else code,
    )

    # импортируем тестовую либу, если шаблон на питоне
    testlib_import_code = read_template(request.app['IMPORT_SNIPPET_PATH']).format(
        testlib_version=lib_version,
        testlib_default_version=request.app['TESTLIB_DEFAULT_VERSION'],
    ) if is_py_trainer else ''

    wrapped_code = '\n'.join((testlib_import_code, wrapped_code))

    script_path = f'/app/{request.app["SCRIPT_NAME"]}'

    with open(script_path, 'w') as f:
        f.writelines(wrapped_code)

    envs = []
    with open('/etc/environment', 'r') as env:
        for line in env.readlines():
            envs.append(line.strip())

    # перед выполнением проверющего скрипта нужно перейти в entrypoint_dir,
    # так как именно туда ставятся библиотеки
    # (в частности, node_modules)
    proc = await asyncio.create_subprocess_shell(
        f'cd {request.app["ENTRYPOINT_DIR"]} && \
        {" ".join(envs)} /bin/bash -c "{request.app["INTERPRETER_NAME"]} {script_path}"',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()

    os.remove(script_path)

    return web.json_response({
        "exit_code": proc.returncode,
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
    })
