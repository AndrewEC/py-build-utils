from typing import List
import os
import shutil

from .base import Command


class FileCleanupCommand(Command):

    """
    A generic high level command that is responsible for attempting to delete a select list of files and/or folders.
    """

    def __init__(self, name: str, paths: List[str]):
        """
        Initializes the file cleanup command.

        Args:
              name (str): The name of the command.
              paths (List[str]): The relative or absolute list of paths to a set of files or folders to be deleted.
        """

        super().__init__(name)
        self._paths = paths

    def execute(self) -> bool:
        for path in self._paths:
            if os.path.isfile(path):
                print(f'Cleaning up file [{path}]')
                os.remove(path)
            elif os.path.isdir(path):
                print(f'Cleaning up directory [{path}]')
                shutil.rmtree(path)
        return True
