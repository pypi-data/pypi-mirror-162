import os
import shutil
from base64 import b64decode
from pathlib import Path
from typing import List, Text

from serverhub_agent.types.files import File, TestFile


class FileSystem:
    def __init__(self, root_dir: Text):
        self.root_dir: Path = Path(root_dir).absolute()
        self.tmp_files: List[Path] = []

    def create_file(self, file: File, is_tmp=False):
        if file.isDir:
            return

        users_file = Path(self.root_dir, Path(file.name)).resolve()
        users_path = users_file.parent

        # Raises ValueError if files is created in tricky pass, something like: ../../../../foo
        users_path.relative_to(self.root_dir)

        users_path.mkdir(parents=True, exist_ok=True)
        mode = 'w'
        content = file.content
        if file.isBin:
            mode = 'wb'
            content = b64decode(content)

        with users_file.open(mode) as f:
            f.write(content)

        if is_tmp:
            self.tmp_files.append(users_file)

    def create_files(self, files: List[File], is_tmp=False):
        for file in files:
            self.create_file(file, is_tmp)

    def remove_tmp(self):
        for f_path in self.tmp_files:
            try:
                f_path.unlink()
            except FileNotFoundError:
                ...
        self.tmp_files = []


class TempFileManager:
    directory = None
    files = None

    def create_file(self, temp_file: TestFile):
        file_path = f"{self.directory}/{temp_file.name}"
        if isinstance(temp_file.content, bytes):
            mode = 'wb'
        else:
            mode = 'w'
        with open(file_path, mode) as f:
            f.write(temp_file.content)

    def __init__(self, *, files: List[TestFile], directory: str):
        self.files = files or []
        self.directory = directory

        if not os.path.exists(self.directory):
            os.makedirs(self.directory, exist_ok=True)

    def __enter__(self):
        for temp_file in self.files:
            self.create_file(temp_file)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        shutil.rmtree(self.directory)
        if exc_type is not None:
            return False
