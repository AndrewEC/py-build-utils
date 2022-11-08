from typing import List
from abc import ABC, abstractmethod

from pathlib import Path
import sys
import os
import shutil
import subprocess

from bs4 import BeautifulSoup


_TEMPLATE_PATH = '{PYTHON_VENV}'


def parse_python_command_string(command: str) -> str:
    """
    Replaces the python env template value in the command string with the appropriate value. This aims to identify
    if the current command is being executed within the context of a virtual environment, identify the environment
    and the path to the python binary, and replace the {PYTHON_ENV} placeholder in the command string with the
    absolute path to the python binary.
    """
    if sys.prefix == sys.base_prefix or _TEMPLATE_PATH not in command:
        return command
    executable_path = str(Path(sys.prefix).joinpath('Scripts').joinpath('python'))
    return command.replace(_TEMPLATE_PATH, executable_path)


class Command(ABC):

    """
    A high level abstract definition of a command.
    """

    def __init__(self, name: str):
        """
        Initializes the command.

        Args:
            name (str): The name of the command. The built-in commands typically use this for logging purposes.
        """
        self.name = name.lower().replace(' ', '_')

    @abstractmethod
    def execute(self) -> bool:
        pass


class StatusBasedProcessCommand(Command):

    """
    A command that executes a subprocess and verifies the status code of the process upon exit matches
    the successful status code provided.
    """

    def __init__(self, name: str, success_statuses: List[int], command: str):
        """
        Initializes the status based process command.

        Args:
            name (str): The name of the command.
            success_statuses (List[int]): The exit code that should be returned by the subprocess for this command to be
            considered successful.
            command (str): The command and associated arguments in a fully formed string that will be executed as a
            subprocess.
        """
        super().__init__(name)
        self._success_status = success_statuses
        self._command = command

    def execute(self) -> bool:
        status = self._execute_command()
        if not self._was_successful(status):
            print(f'[{self.name}] command exited with unexpected status [{status}]')
            return False
        return True

    def _was_successful(self, status: int) -> bool:
        return status in self._success_status

    def _execute_command(self) -> int:
        parsed_command = parse_python_command_string(self._command)
        print(f'Executing subprocess with command string [{parsed_command}]')
        process = subprocess.Popen(parsed_command)
        process.communicate()
        status = process.wait()
        return status


class ReportOpenCommand(Command):

    """
    Opens a file in the default associated program. Typically used to open reports such as code coverage and mutation
    coverage reports.
    """

    def __init__(self, name: str, file: str):
        """
        Initializes the report open command.

        Args:
            name (str): The name of the command.
            file (str): The relative or absolute path to the file to be opened.
        """

        super().__init__(name)
        self._file = file

    def execute(self) -> bool:
        if not os.path.isfile(self._file):
            print(f'Could not find report at: [{self._file}]')
            return False
        try:
            os.startfile(os.path.abspath(self._file))
        except Exception as e:
            print(f'Could not open report: [{self._file}], cause: [{e}]')
            return False
        return True


class ReportCheckCommand(Command):

    """
    An abstract command that provides a rough outline for creating a command with the purpose of opening
    a previously generated report, such as a code coverage report, and verifying the metrics defined within the
    report match the minimum thresholds required for the metric.
    """

    def __init__(self, name: str, file: str):
        super().__init__(name)
        self._file = file

    def execute(self) -> bool:
        if not os.path.isfile(self._file):
            print(f'Could not find report at [{self._file}]')
            return False
        with open(self._file, 'r') as file:
            report_contents = file.read().replace('\n', '')
        parsed = BeautifulSoup(report_contents, features='html.parser')
        return self._check_report(parsed)

    @abstractmethod
    def _check_report(self, html: BeautifulSoup) -> bool:
        pass


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
