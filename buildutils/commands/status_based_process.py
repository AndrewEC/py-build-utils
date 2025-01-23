from typing import List
import subprocess

from .base import Command, parse_python_command_string


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
        print(f'Executing subprocess [{parsed_command}]')
        process = subprocess.Popen(parsed_command)
        process.communicate()
        status = process.wait()
        return status
