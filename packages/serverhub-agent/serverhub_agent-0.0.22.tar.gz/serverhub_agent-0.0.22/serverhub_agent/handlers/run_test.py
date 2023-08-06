import asyncio
import os
import shutil

from aiohttp import web


async def run_test(request: web.Request) -> web.Response:
    body = await request.json()
    """
        body = {
            "files":[
                {
                    content: Text,
                    name: Text,
                }
            ]
        }
    """
    files = body['files']
    tests_path = f'/tests'

    for test_file in files:
        test_file_content = test_file['content']
        test_file_path =f"{tests_path}/{test_file['name']}"
        test_file_dirname = os.path.dirname(test_file_path)
        if not os.path.exists(test_file_dirname):
            os.makedirs(test_file_dirname, exist_ok=True)
        with open(test_file_path, 'w') as f:
            f.writelines(test_file_content)

    envs = []
    with open('/etc/environment', 'r') as env:
        for line in env.readlines():
            envs.append(line.strip())

    proc = await asyncio.create_subprocess_shell(
        f'cd {tests_path} && {" ".join(envs)} /bin/bash {tests_path}/run.sh',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()
    shutil.rmtree(tests_path)

    return web.json_response({
        "exit_code": proc.returncode,
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
    })
