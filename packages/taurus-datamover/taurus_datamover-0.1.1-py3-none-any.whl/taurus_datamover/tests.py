import unittest
import subprocess
from pathlib import Path
import os
import shutil

my_path = Path(__file__)
testdir = my_path.parent.parent / 'tests'


class MockCluster:
    def __init__(self, mock_path: Path = testdir / 'mock_cluster',
                 commands: list = ['dtls', 'dtcp', 'dtmv'], exe: str = 'dtwrapper') -> None:
        self.mock_path = mock_path
        self.commands = commands
        self.src = self.mock_path / exe

    def __enter__(self):
        shutil.copytree(str(self.mock_path) + '_files', self.mock_path)
        src = self.mock_path / 'dtwrapper'
        for command in self.commands:
            os.symlink(src, self.mock_path / command)
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        shutil.rmtree(self.mock_path, ignore_errors=True)
