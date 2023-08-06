import json
import logging
from typing import Any, List, Tuple

from serverhub_agent.types.jupyter import JupyterOutputs
from serverhub_agent.ws.ws_messages import TestMsgTypes

logger = logging.getLogger(__name__)


class BaseOutputProcessor(object):
    async def get_log(self, line: bytes) -> List[Tuple[TestMsgTypes, Any]]:
        if type(line) == bytes:
            line = line.decode()

        return [(TestMsgTypes.text, line)]


class JupyterOutputProcessor(BaseOutputProcessor):
    def __init__(self):
        # TODO: нет парсеров для output_type: error и execute_result
        self.jupyter_type_parsers: dict = {
            "stream": self.parse_stream,
            "display_data": self.parse_display,
        }

        self.jupyter_outputs_schema = JupyterOutputs.Schema()

    def parse_stream(self, output: dict) -> (TestMsgTypes, Any):
        return TestMsgTypes.text, output.get('text', '')

    def parse_display(self, output: dict) -> (TestMsgTypes, Any):
        key = None
        data = output.get('data', {})
        for key in data:
            if key.startswith('image'):
                break
            else:
                key = None

        if not key:
            return None, None

        encoded_image = data.get(key, None)
        return TestMsgTypes.image, f'data:{key};base64, {encoded_image}'

    async def get_log(self, line: bytes) -> List[Tuple[TestMsgTypes, Any]]:
        if type(line) == bytes:
            line = line.decode()

        try:
            cell_outputs = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            logger.debug(f"Output is not a json [{line}]")
            return [(TestMsgTypes.text, line)]

        errors = self.jupyter_outputs_schema.validate({"outputs": cell_outputs})
        if errors:
            logger.debug(f"Output is not cell_outputs [{line}]")
            return [(TestMsgTypes.text, line)]

        result = []
        for cell_output in cell_outputs:
            if type(cell_output) is not dict:
                result.append((TestMsgTypes.text, cell_output))
                continue

            parser = self.jupyter_type_parsers.get(cell_output.get('output_type', None), None)
            if parser is None:
                continue

            o_type, o_data = parser(cell_output)
            if not o_data:
                continue

            result.append((o_type, o_data))

        return result
