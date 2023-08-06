from typing import List, Optional, Text, Union

from marshmallow_dataclass import dataclass

from .common import ObjectWithSchema


@dataclass
class File(ObjectWithSchema):
    """
    Represents code in a file:

    {
      "language": "html",
      "content": "<h1>Hello World</h1>",
      "name": "index.html",
      "isDir": False,
      "isBin": False,
    }
    """
    content: Text
    language: Text
    name: Text
    isDir: Optional[bool]
    isBin: Optional[bool] = False


@dataclass
class Files(ObjectWithSchema):
    files: List[File]


@dataclass
class TestFile(ObjectWithSchema):
    content: Union[str, bytes]
    name: str


@dataclass
class AstTests(ObjectWithSchema):
    testlib_version: str
    precode: Optional[TestFile]
    user: TestFile
    answer: TestFile
    test: TestFile
