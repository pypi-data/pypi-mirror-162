import json
import logging
import os
import resource
from asyncio import CancelledError, Queue, Task, TimeoutError, create_task
from asyncio import subprocess as sp
from asyncio import wait_for
from dataclasses import dataclass
from typing import List, Optional, Text

import psutil
from aiohttp.web import WebSocketResponse

from serverhub_agent.utils.filesystem import FileSystem
from serverhub_agent.ws.output_processor import BaseOutputProcessor
from serverhub_agent.ws.ws_broadcaster import WsBroadcaster
from serverhub_agent.ws.ws_messages import (Command, Error, ExecReturnCode,
                                            ExecStatus, Log, LogType, Result,
                                            State, TestMsgTypes,
                                            TestStatusTypes, Types)
from serverhub_agent.ws.ws_utils import no_except

logger = logging.getLogger(__name__)


@dataclass
class RunnerMsg:
    """
    Сообщения для взаимодействия с WsBroadcaster
    """
    cmd: Command
    source: WebSocketResponse


class Runner:
    """
    Класс представляющий запущенный процесс. При старте агента создается один инстанс для всех обработчиков.

    Диспатчеры сокетов направляют stdin/run/check сообщения в этот инстанс. Сообщения обрабатывается по очереди,
    гарантируя одну последовательность State/Stdin видимую клиентам.

    Все сообщения в сокеты так же отправляются из этого класса.
    """
    reset_state = State(execution_status=ExecStatus.initialized, error_msg=None)

    def __init__(
            self,
            ws_broadcaster: WsBroadcaster,
            file_system: FileSystem,
            mem_limit_mb: int,
            output_limit: int,
            output_processor_cls: BaseOutputProcessor,
    ):
        self._queue: Queue = Queue()
        self.manager: Task = create_task(self._msg_dispatcher())
        self.ws_broadcaster: WsBroadcaster = ws_broadcaster
        self.file_system: FileSystem = file_system
        self.process: Optional[sp.Process] = None
        self.process_handlers: List[Task] = []
        self.loaded_files: List[Text] = []
        self.run_id: Optional[Text] = None
        self.mem_limit_mb: int = mem_limit_mb
        self.output_limit: int = output_limit
        self.output_processor: BaseOutputProcessor = output_processor_cls()

    # общение с раннером только через этот метод (и close())
    async def send_command(self, command: Command, src: WebSocketResponse):
        await self._queue.put(RunnerMsg(command, src))

    async def stop(self):  # завершает работу раннера после обработки предыдущих сообщений, ждет 5 сек и убивает
        await self._queue.put(RunnerMsg(None, None))
        try:
            await wait_for(self.manager, 2)
        except CancelledError:
            logger.error(f'failed to stop runner properly')

    async def _msg_dispatcher(self):  # разгребает сообщения stdin/run/check по одному
        while True:
            msg: RunnerMsg = await self._queue.get()
            command = msg.cmd
            if command is None:
                break

            if command.type in [Types.CHECK,  Types.RUN]:
                await self._start_run(command)
            elif command.type is Types.LOG and command.data.level == LogType.stdin:
                await self._send_stdin(command, msg.source)
            elif command.type is Types.STOP:
                await self._reset()
            else:
                logger.error(f"runner received command of unexpected type f{command.type}")

        logger.info('runner finished receiving commands')

    @property
    def _is_running(self):
        return self.process and self.process.returncode is None

    @no_except
    async def _reset(self):
        await self._kill_running_process()
        await self.ws_broadcaster.send_state(self.reset_state)

    @no_except
    async def _start_run(self, run_cmd: Command):
        await self._kill_running_process()
        try:
            await self._put_files(run_cmd)
        except Exception as e:
            print(e)
        await self._start_sub_process(run_cmd)

    @no_except
    async def _send_stdin(self, log_cmd: Command, source: WebSocketResponse):
        if not self._is_running:
            await self.ws_broadcaster.send_error(Error(code='WS.NoProcess', message='wait for State(in progress)'))
            return

        await self.ws_broadcaster.send_command(log_cmd, exclude=source)
        self.process.stdin.write(log_cmd.data.message.encode())
        await self.process.stdin.drain()

    async def _kill_running_process(self):
        if self._is_running:
            logger.info('killing already running process')
            process = psutil.Process(self.process.pid)
            for proc in process.children(recursive=True) + [process]:
                proc.kill()
                logger.info(f'killed [{proc.pid}]')

            for handler in self.process_handlers:
                try:
                    await wait_for(handler, 0.1)
                    logger.info('one handler finished')
                except TimeoutError:
                    logger.warning('failed to wait for process handler')

    async def _put_files(self, run_cmd: Command):
        # delete old user's files
        self.file_system.remove_tmp()

        # put new files
        try:
            self.file_system.create_files(run_cmd.data.files, is_tmp=True)
        except ValueError as e:
            logger.error(f'trying to put files outside the sandbox: error [{e}]')
            await self.ws_broadcaster.send_error(Error(code='WS.BadFiles', message='bad file structure'))
            return

    def _get_preexec_fun(self):
        max_bytes = self.mem_limit_mb * 2**20

        def set_limits():
            resource.setrlimit(resource.RLIMIT_DATA, (max_bytes, max_bytes))

        return set_limits

    async def _start_sub_process(self, run_cmd: Command):
        self.run_id = run_cmd.data.run_id
        opened_fds = len(set(os.listdir(f'/proc/{os.getpid()}/fd/')))
        logger.info(f"got [{opened_fds}] opened file descriptors")

        read_pipe_number, write_pipe_number = os.pipe()
        os.set_inheritable(write_pipe_number, True)

        if run_cmd.type is Types.RUN:
            running_state = State(execution_status=ExecStatus.run_in_progress, error_msg=None)
        else:
            running_state = State(execution_status=ExecStatus.check_in_progress, error_msg=None)
        await self.ws_broadcaster.send_state(running_state)

        # start new process (with new handlers)
        env = os.environ.copy()
        env["TEST_OUTPUT_FD"] = str(write_pipe_number)
        logger.debug(f'running [{run_cmd.data.bash_command}]')
        self.process = await sp.create_subprocess_shell(
            run_cmd.data.bash_command,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            stdin=sp.PIPE,
            preexec_fn=self._get_preexec_fun(),
            pass_fds=(write_pipe_number,),
            env=env,
            limit=self.output_limit,
        )
        os.close(write_pipe_number)  # to avoid deadlock

        self.process_handlers = [
            create_task(self._proxy_stream(LogType.stdout)),
            create_task(self._proxy_stream(LogType.stderr)),
            create_task(self._process_waiter(
                send_result=run_cmd.type is Types.CHECK,
                test_pipe_fd=read_pipe_number,
                timeout=run_cmd.data.timeout,
            )),
        ]
        logger.info(f'spawned process with pid [{self.process.pid}]')

    @staticmethod
    def _get_test_status_by_ret_code(ret_code):
        test_statuses = {
            ExecReturnCode.ok.value: TestStatusTypes.ok,
            ExecReturnCode.failed.value: TestStatusTypes.failed,
            ExecReturnCode.failed_to_run_code.value: TestStatusTypes.failed_to_run_code,
        }
        return test_statuses.get(ret_code, TestStatusTypes.failed)

    async def _send_result(self, ret_code, test_output):
        result = Result(
            message_type=TestMsgTypes.intl if test_output else TestMsgTypes.text,
            message=test_output or "",
            status=self._get_test_status_by_ret_code(ret_code=ret_code),
            run_id=self.run_id,
        )
        await self.ws_broadcaster.send_result(result)

    async def _send_timeout_result(self):
        result = Result(
            message_type=TestMsgTypes.intl,
            message={"id": "TrainerError.Timeout"},
            status=TestStatusTypes.timeout,
            run_id=self.run_id,
        )
        await self.ws_broadcaster.send_result(result)

    async def _send_end_state(self):
        # send state null
        run_end_state = State(execution_status=ExecStatus.null, error_msg=None)
        await self.ws_broadcaster.send_state(run_end_state)

    async def _process_waiter(self, send_result: bool, test_pipe_fd: int, timeout: Optional[int]):
        try:
            ret_code = await wait_for(self.process.wait(), timeout=timeout)  # Если timeout is None, ждём завершения
        except TimeoutError:
            logger.info(f'killing process [{self.process.pid}] by timeout')
            await self._send_timeout_result()
            await self._kill_running_process()
        else:
            logger.info(f'process terminated with exit code [{ret_code}]')

            # send result only in check
            if not send_result:
                return

            with os.fdopen(test_pipe_fd) as pipe:
                test_output = pipe.read()
                try:
                    test_output = json.loads(test_output)
                except (json.JSONDecodeError, ValueError):
                    logger.error(f'failed to parse [{test_output}] as json')
                await self._send_result(ret_code=ret_code, test_output=test_output)
        finally:  # this waiter is canceled on process killing, we want state to be delivered anyway
            # os.close(test_pipe_fd)
            await self._send_end_state()

    async def _proxy_stream(self, stream_type: LogType):
        stream = self.process.stdout if stream_type is LogType.stdout else self.process.stderr

        at_eof = False
        while not at_eof:
            logger.debug(f"Subprocess {stream_type.name}: waiting read")
            try:
                line = await stream.readline()
            except CancelledError:
                logger.warning(f'Subprocess {stream_type.name}: canceled on read')
                return

            at_eof = stream.at_eof()

            if not line:
                continue
            messages = await self.output_processor.get_log(line)
            try:
                for message_type, message in messages:
                    await self.ws_broadcaster.send_log(Log(
                        message_type=message_type,
                        message=message,
                        level=stream_type,
                    ))
            except CancelledError:
                logger.warning(f'Subprocess {stream_type.name}: canceled on send')
                return

        logger.debug(f"Subprocess {stream_type.name}: eof/terminated")
