from enum import Enum
from typing import Any, List, Optional, Text

from marshmallow import ValidationError, post_load, pre_dump
from marshmallow_dataclass import dataclass

from serverhub_agent.types.common import ObjectWithSchema
from serverhub_agent.types.files import File


class TestMsgTypes(Enum):
    text = 'text'
    intl = 'intl'
    markdown = 'markdown'
    image = 'image'


class TestStatusTypes(Enum):
    ok = 'ok'
    failed = 'failed'
    failed_to_run_code = 'failed_to_run_code'
    error = 'error'
    timeout = 'timeout'
    pending = 'pending'
    null = 'null'


class ExecReturnCode(Enum):
    ok = 0
    failed = 1
    failed_to_run_code = 2


# represents the status of the running container
class ExecStatus(Enum):
    new = 'new'                                 # not initialized
    initialized = 'initialized'                 # initialization finished (signals that container started serving)
    null = 'null'                               # initialized and idle (signals that run terminated)
    check_in_progress = 'check_in_progress'     # initialized and running check
    run_in_progress = 'run_in_progress'         # initialized and running code


# types of command which can be used in WS
# communication protocol
class Types(Enum):
    RUN = 'RUN'                     # run (code)
    ERROR = 'ERROR'
    LOG = 'LOG'
    RESULT = 'RESULT'
    STATE = 'STATE'
    CHECK = 'CHECK'                 # run check
    FILE_UPLOAD = 'FILE_UPLOAD'
    INIT_REQUEST = 'INIT_REQUEST'   # request to start initialization
    START = 'START'                 # end of initialization, start serving
    RESET = 'RESET'                 # reset msg buffer and cancel running container
    STOP = 'STOP'                   # stop execution (run or check command)


class LogType(Enum):
    stdout = "stdout"
    stderr = "stderr"
    stdin = "stdin"


command_registry = {}


def register(klass_type):
    def wrapper(klass):
        if klass_type in command_registry:
            raise ValueError(
                f'class {klass_type} already registered with {command_registry[klass_type]}',
            )
        command_registry[klass_type] = klass
        return klass
    return wrapper


@dataclass
class Command(ObjectWithSchema):
    type: Types
    data: Optional[Any]

    @post_load()
    def parse_data(self, command, **kwargs):
        data = command['data']  # bug here
        data = {} if data is None else data
        try:
            payload_class = command_registry[command['type']]
        except KeyError as e:
            raise ValidationError(f'Not registered type {e}')
        data = payload_class.Schema().load(data)
        command['data'] = data
        return command

    @pre_dump()
    def dump_data(self, command, **kwargs):
        if command.data is not None and not isinstance(command.data, dict):
            data = command.data.Schema().dump(command.data)
            command.data = data
        return command


# Error type like Intl messages
@register(Types.ERROR)
@dataclass
class Error(ObjectWithSchema):
    message: str
    code: str

# Type for code execution state, for now
# wee are are intersted in execution_status and
# error_msg on ExecStatus.error status
@register(Types.STATE)
@dataclass
class State(ObjectWithSchema):
    execution_status: ExecStatus
    error_msg: Optional[Error]


# Logging command data, like from slow_ds trainer
@register(Types.LOG)
@dataclass
class Log(ObjectWithSchema):
    message_type: TestMsgTypes
    message: Any
    level: LogType


@register(Types.RESULT)
@dataclass
class Result(ObjectWithSchema):
    message_type: TestMsgTypes
    message: Any
    status: TestStatusTypes
    run_id: Optional[Text]


# разделение на Check/Run нужно пока мы кешируем логи в контейнере, т.к. фронт должен знать, что запускалось
@register(Types.CHECK)
@register(Types.RUN)
@dataclass
class Run(ObjectWithSchema):
    bash_command: Text
    files: Optional[List[File]]
    run_id: Optional[Text]
    timeout: Optional[int]


register(Types.FILE_UPLOAD)(File)


@register(Types.STOP)
@register(Types.RESET)
@register(Types.START)
@dataclass
class NoData(ObjectWithSchema):
    ...


@register(Types.INIT_REQUEST)
@dataclass
class InitRequest(ObjectWithSchema):
    request_id: Text
