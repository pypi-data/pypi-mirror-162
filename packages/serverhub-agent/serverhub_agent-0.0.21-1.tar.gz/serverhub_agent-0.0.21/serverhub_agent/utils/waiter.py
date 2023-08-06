import logging
from asyncio import TimeoutError, ensure_future, sleep, subprocess, wait
from dataclasses import dataclass
from enum import Enum
from typing import List, Text

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError

logger = logging.getLogger(__name__)


class WaitingProtocol(Enum):
    port_up = 1
    port_responding = 2


@dataclass
class PortConfig:
    port: int
    protocol: Text = WaitingProtocol.port_up.name


class ServerWaiter(object):
    """ Waits for ports on localhost with specified protocol """
    def __init__(self, ports_to_wait: List[PortConfig], overall_timeout: int):
        self.ports_to_wait: List[PortConfig] = ports_to_wait
        self.overall_timeout: int = overall_timeout

    @staticmethod
    def get_waiter(protocol: WaitingProtocol):
        waiters = {
            WaitingProtocol.port_up: ServerWaiter._is_port_listening,
            WaitingProtocol.port_responding: ServerWaiter._is_port_responding,
        }

        try:
            waiter = waiters[protocol]
        except KeyError:
            raise NotImplementedError(f'waiter for protocol [{protocol.name}] is not implemented')

        return waiter

    @staticmethod
    async def _is_port_listening(port: int) -> bool:
        cmd = f"netstat -tulpn 2>/dev/null | grep LISTEN | grep :{port}"
        proc = await subprocess.create_subprocess_shell(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()

        return stdout != b''

    @staticmethod
    async def _is_port_responding(port: int) -> bool:
        timeout = ClientTimeout(total=1, connect=0.5)
        url = f'http://localhost:{port}/'
        try:
            async with ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    logger.info(f'port {port} is ready, resp status [{resp.status}]')
                    return True  # we're okay with any response at all
        except (ClientError, TimeoutError) as e:
            logger.info(f'port [{port}] is still not responding, error [{e}] of type [{type(e)}]')
            return False

    async def waiting_loop(self, port_conf: PortConfig) -> None:
        is_port_ready = self.get_waiter(WaitingProtocol[port_conf.protocol])
        while not await is_port_ready(port_conf.port):
            logger.info(f'{port_conf.port} is still not responding, waiting 0.25s')
            await sleep(0.25)

        return

    async def wait_for_ports(self) -> bool:
        if not len(self.ports_to_wait):
            return True

        waiting_tasks = [ensure_future(self.waiting_loop(port_conf)) for port_conf in self.ports_to_wait]
        try:
            _, pending = await wait(waiting_tasks, timeout=self.overall_timeout)
        finally:
            for coro in waiting_tasks:
                if coro.done():
                    logger.info(coro.result())
                coro.cancel()

        return len(pending) == 0
