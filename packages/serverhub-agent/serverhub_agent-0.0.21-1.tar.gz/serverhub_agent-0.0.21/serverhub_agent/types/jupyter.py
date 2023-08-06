from typing import Any, Union, List

from marshmallow_dataclass import dataclass

# При исполнении пользовательского кода используется nbformat.v4
# https://github.com/jupyter/nbformat/blob/master/nbformat/v4/nbformat.v4.schema.json
# Чтобы отличать вывод тетрадки от пользовательского, stdout валидируется относительно
# формата вывода ExecutePreprocessor


@dataclass
class JupyterOutputExecuteResult:
    # execute_result
    output_type: Any
    execution_count: Any
    data: Any
    metadata: Any


@dataclass
class JupyterOutputDisplayData:
    # display_data
    output_type: Any
    data: Any
    metadata: Any


@dataclass
class JupyterOutputStream:
    # stream
    output_type: Any
    name: Any
    text: Any


@dataclass
class JupyterOutputError:
    # error
    output_type: Any
    ename: Any
    evalue: Any
    traceback: Any


@dataclass
class JupyterOutputs:
    outputs: List[
        Union[
            JupyterOutputError,
            JupyterOutputStream,
            JupyterOutputExecuteResult,
            JupyterOutputDisplayData,
        ]
    ]
