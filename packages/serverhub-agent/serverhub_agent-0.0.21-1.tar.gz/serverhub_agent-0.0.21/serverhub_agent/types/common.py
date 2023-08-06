import dataclasses
from typing import ClassVar, Text, Type

from marshmallow import EXCLUDE, Schema


class ObjectWithSchema:
    Schema: ClassVar[Type[Schema]]  # For the type checker

    def to_dict(self) -> dict:
        # TODO check errors
        return dataclasses.asdict(self)

    def to_json(self) -> Text:
        schema = self.Schema(unknown=EXCLUDE)
        return schema.dumps(self).data
