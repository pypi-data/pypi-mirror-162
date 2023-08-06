import asyncio
import logging
from pathlib import Path
from typing import Text

logger = logging.getLogger(__name__)


class Runner:
    """ Runs entrypoint scripts for now, later it may run user's code and proxy logs etc. """
    def __init__(self, working_dir: Text, script_path: Text, logs_path: Text):
        self.working_dir = Path(working_dir)
        self.script_path = Path(script_path)
        self.logs_path = Path(logs_path)

    async def run_script(self):
        redirect = ''
        if self.logs_path:
            redirect = f'> {self.logs_path} 2>&1'

        proc = await asyncio.create_subprocess_shell(
            f'cd {self.working_dir} && /bin/bash {self.script_path} {redirect}',
        )
        logger.info(f'spawned entrypoint process with pid [{proc.pid}]')
        return
