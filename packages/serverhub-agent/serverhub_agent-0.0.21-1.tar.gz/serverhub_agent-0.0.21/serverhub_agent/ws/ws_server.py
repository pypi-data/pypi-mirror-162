import logging
from asyncio import CancelledError, Queue, Task, create_task, wait_for
from json import JSONDecodeError

from aiohttp.http_websocket import WSMessage
from aiohttp.web import Application, Request, WebSocketResponse, WSMsgType
from aiohttp.web_runner import GracefulExit
from marshmallow import ValidationError

from serverhub_agent.types.exceptions import BadMessage, ClosedSocket
from serverhub_agent.types.files import File
from serverhub_agent.utils.filesystem import FileSystem
from serverhub_agent.ws.ws_broadcaster import WsBroadcaster
from serverhub_agent.ws.ws_messages import (Command, Error, ExecStatus,
                                            LogType, State, Types)
from serverhub_agent.ws.ws_runner import Runner
from serverhub_agent.ws.ws_utils import send_error_to_socket

logger = logging.getLogger(__name__)


class Closing(Exception):
    ...


class ContainerInitializer:
    """
    Реализация протокола инициализации контейнера:
    - при подключении к неинициализированному контейнеру клиенты получают STATE(new);
    - в ответ клиенты отправляют запрос INIT_REQ(uuid) на выполнение инициализации контейнера;
    - агент броадкастит первый пришедший запрос -- его отправитель будет производить инициализацию;
    - инициализация выполняется путем загрузки файлов в контейнер последовательными командами FILE_UPLOAD;
    - инициализация завершается после получения от инициализирующего клиента команды типа START;
    - по завершении инициализации агент отправляет всем клиентам команды STATE(initialized);
    - TODO: клиент отвалился до того, как завершил инциализацию
    """
    def __init__(self, ws_broadcaster: WsBroadcaster, file_system: FileSystem):
        self._queue: Queue = Queue()
        self._manager: Task = create_task(self._msg_dispatcher())
        self._ws_broadcaster: WsBroadcaster = ws_broadcaster
        self.initializing: bool = False  # todo: add inited state, send errors on FILE_UPLOAD after init
        self.file_system: FileSystem = file_system

    async def send_command(self, command: Command):  # общение с инициализатором только через этот метод (и stop())
        await self._queue.put(command)

    async def stop(self):  # останавливает выполнение команд, после отправки пришедших ранее, ждет 5 секунд и убивает
        await self._queue.put(None)
        try:
            await wait_for(self._manager, 2)
        except CancelledError:
            logger.error(f'failed to stop initializer properly')

    async def _msg_dispatcher(self):  # разгребает сообщения INIT_REQ/FILE_UPLOAD/START по одному
        while True:
            command: Command = await self._queue.get()
            if command is None:
                break

            if command.type is Types.INIT_REQUEST:
                if not self.initializing:
                    self.initializing = True
                    await self._ws_broadcaster.send_command(command)
            elif command.type is Types.FILE_UPLOAD:
                file: File = command.data
                self.file_system.create_file(file)  # todo: do it in a subprocess
            elif command.type is Types.START:
                inited_state = Command(Types.STATE, State(execution_status=ExecStatus.initialized, error_msg=None))
                await self._ws_broadcaster.send_command(inited_state)

        logger.info('initializer finished receiving commands')


class MsgDispatcher:
    """
    Диспатчер сообщений из одного конкретного сокета, направляет их синглтон раннеру/инициализатору контейнера
    """
    def __init__(
            self,
            ws: WebSocketResponse,
            runner: Runner,
            initializer: ContainerInitializer,
    ):
        self.ws: WebSocketResponse = ws
        self.runner: Runner = runner
        self.initializer: ContainerInitializer = initializer

    def load_command(self, msg: WSMessage) -> Command:
        if msg.type != WSMsgType.TEXT:
            logger.warning(f'ignoring unknown message type [{msg.type}]')
            raise BadMessage(f'bad message type [{msg.type}]')

        try:
            command = Command.Schema().loads(msg.data)
        except (JSONDecodeError, ValidationError) as e:
            logger.warning(f'failed to decode message with error [{e}]')
            raise BadMessage(f"bad message structure [{msg.data}]")

        return command

    async def run_until_closed(self):
        try:
            async for msg in self.ws:  # stops iteration on closed socket
                try:
                    command: Command = self.load_command(msg)
                except BadMessage as e:
                    await send_error_to_socket(Error(code='WS.BadCommand', message=str(e)), self.ws)
                    continue

                if command.type in [Types.INIT_REQUEST, Types.FILE_UPLOAD, Types.START]:
                    await self.initializer.send_command(command)
                elif (
                        command.type in [Types.CHECK, Types.RUN, Types.STOP]
                        or command.type is Types.LOG and command.data.level == LogType.stdin
                ):
                    await self.runner.send_command(command, self.ws)  # ws, cause we don't want sender to receive stdin
                elif command.type is Types.RESET:
                    logger.info('received a reset command, stopping agent')
                    raise Closing
                else:
                    await send_error_to_socket(
                        Error(code='WS.BadCommand', message=f'unexpected command of type [{command.type}]'),
                        self.ws,
                    )
        except ClosedSocket:
            ...

        logger.info(f'socket was closed')


class WsServer:
    def __init__(self, app: Application):
        self.ws_broadcaster: WsBroadcaster = WsBroadcaster(app['PROC_OUTPUT_LIMIT'])
        self.initializer: ContainerInitializer = ContainerInitializer(
            self.ws_broadcaster, app['filesystem'])
        self.runner: Runner = Runner(
            self.ws_broadcaster,
            app['filesystem'],
            app['PROC_MEM_LIMIT_MB'],
            app['PROC_OUTPUT_BUFFER_SIZE'],
            app['OUTPUT_PROCESSOR_CLS'],
        )

    async def connect(self, request: Request) -> WebSocketResponse:
        ws = WebSocketResponse()
        await ws.prepare(request)
        await self.ws_broadcaster.subscribe(ws)

        try:
            dispatcher = MsgDispatcher(ws, self.runner, self.initializer)
            await dispatcher.run_until_closed()
        except Closing:
            await self.stop()
        finally:
            await self.ws_broadcaster.unsubscribe(ws)

        return ws

    async def stop(self):
        await self.initializer.stop()
        await self.runner.stop()
        await self.ws_broadcaster.stop()
        raise GracefulExit
