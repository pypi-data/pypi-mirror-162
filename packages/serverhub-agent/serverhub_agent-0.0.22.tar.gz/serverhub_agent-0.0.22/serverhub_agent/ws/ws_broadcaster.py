import logging
from asyncio import CancelledError, wait_for
from asyncio.queues import Queue
from asyncio.tasks import Task, create_task
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional, Union

from aiohttp.web_ws import WebSocketResponse

from serverhub_agent.types.exceptions import ClosedSocket
from serverhub_agent.ws.ws_messages import (Command, Error, ExecStatus, Log,
                                            Result, State, Types)
from serverhub_agent.ws.ws_utils import no_except, send_command_to_socket

logger = logging.getLogger(__name__)


class BcMsgType(IntEnum):
    subscribe = 1
    unsubscribe = 2
    send = 3


@dataclass
class SendParams:
    cmd: Command
    exclude: Optional[WebSocketResponse]


@dataclass
class BcMsg:
    """
    Сообщения для взаимодействия с WsBroadcaster
    """
    type: BcMsgType
    data: Union[None, SendParams, WebSocketResponse]


class WsBroadcaster:
    """
    Класс буферизующий и рассылающий сообщения на время работы одного запуска кода (неидеальная альтернатива редису).

    При старте агента создается один инстанс для всех обработчиков. Новый запуск перетирает сообщения предыдущего.

    Каждый запуск начинается сообщением State(execution_status='.._in_progress') и заканчивается сообщением
    State(execution_status='null'). Их разделяет произвольное кол-во сообщений типов Log, Error, Result (последнее может
    быть только одно и присутствует только у запуска тестов).

    При установлении коннекта по новому сокету в него посылаются все накопленные сообщения (в буфере всегда есть, как
    минимум, одно сообщение State(execution_status='null'), которое заносится туда при старте).

    Для отправки любых сообщений в сокет, кроме ошибок десериализации сообщений, должен использоваться объект этого
    класса. Это верно и для сообщений типа Log(stdin). Мы их отправляем обратно в сокет т.к. хотим, чтобы
    пользователь видел свой ввод при реконекте. В случае с Log(stdin) важно отправлять сообщения в сокет до отправки их
    в stdin процесса, чтобы гарантировать, что stdout порожденный этим stdin'ом был получен клиентом после отправленного
    stdin. (Однако, мы не можем гарантировать, что stdout, порождаемый процессом без влияния полученного stdin будет
    отображен в верном порядке относительно него).

    Log(stdin) транслируется всем, в т.ч. отправителю, чтобы зафиксировать порядок сообщения Log(stdin) относительно
    сообщений типа State, в котором оно было обработано. Мы гарантируем, что ввод, пришедший после
    первого State(in_progress) был направлен первому запуску, а после второго State(in_progress) -- второму.

    Таким образом после получения State(in_progress) можно смело очищать консоль -- весь ввод, доставленый в новый
    запуск (и возможно произведенный в параллельной сессии), будет доставлен в сокет после полученного стейта.
    """
    states_clearing_buffer = [ExecStatus.initialized, ExecStatus.run_in_progress, ExecStatus.check_in_progress]
    preinit_state = Command(Types.STATE, State(execution_status=ExecStatus.new, error_msg=None))

    def __init__(self, output_limit: int):
        self._all_ws: List[WebSocketResponse] = []
        self._queue: Queue = Queue()  # очередь еще не отосланых в сокеты сообщений И запросов на подключение/отключение
        self._buffer: List[Command] = [self.preinit_state]  # буфер сообщений для отсылки подключившимся позже
        self._manager: Task = create_task(self._msg_dispatcher())
        self.output_size = 0
        self.output_limit: int = output_limit  # todo: drop after exceed

    # запрос на отправку команды во все подписанные сокеты
    async def send_command(self, command: Command, exclude: Optional[WebSocketResponse] = None):
        await self._queue.put(BcMsg(BcMsgType.send, SendParams(command, exclude)))

    async def subscribe(self, ws: WebSocketResponse):  # запрос на подписку на рассылку команд
        await self._queue.put(BcMsg(BcMsgType.subscribe, ws))

    async def unsubscribe(self, ws: WebSocketResponse):  # запрос на отписку от рассылки
        await self._queue.put(BcMsg(BcMsgType.unsubscribe, ws))

    async def stop(self):  # останавливает рассылку сообщений, после отправки пришедших ранее, ждет 5 секунд и убивает
        await self._queue.put(None)
        try:
            await wait_for(self._manager, 2)
        except CancelledError:
            logger.error(f'failed to stop broadcaster properly')

    async def send_state(self, state: State):
        cmd = Command(type=Types.STATE, data=state)
        await self.send_command(cmd)

    async def send_error(self, error: Error):
        cmd = Command(type=Types.ERROR, data=error)
        await self.send_command(cmd)

    async def send_log(self, log: Log):
        cmd = Command(type=Types.LOG, data=log)
        await self.send_command(cmd)

    async def send_result(self, result: Result):
        cmd = Command(type=Types.RESULT, data=result)
        await self.send_command(cmd)

    def _update_buffer(self, cmd: Command):
        """
        Добавляет пришедшую команду в буфер. Команды STATE(initialized),STATE(check_in_progress),STATE(run_in_progress)
        требуют очистки предыдущих сообщений в буфере,
        т.к. данная команды отсылаются при новом запуске и после завершения инициализации контейнера.
        """
        if cmd.type is Types.STATE and cmd.data.execution_status in self.states_clearing_buffer:
            self.output_size = 0
            self._buffer = []

        if cmd.type is Types.LOG:
            self.output_size += len(cmd.data.message)
        if cmd.type is Types.LOG and self.output_size > self.output_limit:
            return

        self._buffer.append(cmd)

    async def _msg_dispatcher(self):
        """
        Разгребает очередь. В ней сообщения трех типов -- запрос на подписку/отписку сокета, запрос на отправку
        команды во все подписанные сокеты.
        """
        while True:
            msg: BcMsg = await self._queue.get()
            if msg is None:
                break

            if msg.type is BcMsgType.subscribe and isinstance(msg.data, WebSocketResponse):
                await self._subscribe(msg)
            elif msg.type is BcMsgType.unsubscribe and isinstance(msg.data, WebSocketResponse):
                await self._unsubscribe(msg)
            elif msg.type is BcMsgType.send and isinstance(msg.data, SendParams):
                await self._send(msg)
            else:
                logger.error(f'broadcaster: bad msg [{msg}]')

        logger.info('broadcaster finished receiving commands')

    @no_except
    async def _subscribe(self, msg: BcMsg):
        ws: WebSocketResponse = msg.data
        try:
            for command in self._buffer:
                await send_command_to_socket(command, ws)
        except ClosedSocket:
            logger.error('socket was closed just after subscription')
        else:
            self._all_ws.append(ws)

    @no_except
    async def _unsubscribe(self, msg: BcMsg):
        ws: WebSocketResponse = msg.data
        try:
            self._all_ws.remove(ws)
        except ValueError:
            logger.warning('socket has been unsubscribed already')

    @no_except
    async def _send(self, msg: BcMsg):
        cmd: Command = msg.data.cmd
        self._update_buffer(cmd)
        await self._send_to_all(msg.data.cmd, msg.data.exclude)

    async def _send_to_all(self, command: Command, exclude: Optional[WebSocketResponse] = None):
        for ws in self._all_ws:
            if ws is exclude:
                logger.debug(f"skipped source on stdin send")
                continue

            try:
                await send_command_to_socket(command, ws)
            except ClosedSocket:
                logger.error(f'socket closed on broadcasting, unsubscribing it')
                self._all_ws.remove(ws)
