from typing import Callable, List, Text, Type

from aiohttp.web_exceptions import HTTPException
from aiohttp.web_response import Response
from marshmallow_dataclass import dataclass

from serverhub_agent.types.common import ObjectWithSchema


def get_all_subclasses(base_object: Type[HTTPException]) -> List[Type]:
    queue = base_object.__subclasses__()
    subclasses = []
    while len(queue):
        subclasses.append(queue.pop(0))
        for subclass in subclasses[-1].__subclasses__():
            queue.append(subclass)
    return subclasses


class HttpErrorFabric:

    base_exception: Type[HTTPException] = HTTPException

    def __init__(self):
        self.key_err_func = self._get_key_err_func()
        self.http_errors_map = self._build_err_map()

    def _get_key_err_func(self) -> Callable:
        return lambda err: getattr(err, 'status_code', -1) != -1

    def _build_err_map(self) -> dict:
        return {
            err.status_code: err
            for err in get_all_subclasses(self.base_exception)
            if self.key_err_func(err)
        }

    async def build(self, response: Response) -> HTTPException:

        err_class = self.class_by_status(response.status)
        return err_class(
            headers=response.headers,
            reason=response.reason,
            text=await response.text(),
        )

    def class_by_status(self, status: int):
        try:
            return self.http_errors_map[status]
        except KeyError:
            return self.base_exception


HttpErrorFabric = HttpErrorFabric()



@dataclass
class DRFError(ObjectWithSchema):
    code: Text
    message: Text


@dataclass
class DRFErrorResponse(ObjectWithSchema):
    errors: List[DRFError]


def build_err_string(code: Text, message: Text):
    response_data = DRFErrorResponse.Schema().dumps(
        DRFErrorResponse(
            errors=[DRFError(code=code, message=message)]),
    )
    return response_data


def build_drf_err(code: Text, message: Text, status: int = 400):
    return HttpErrorFabric.class_by_status(status)(
        content_type='application/json',
        text=build_err_string(code=code, message=message),
    )
