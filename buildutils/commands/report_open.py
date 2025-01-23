import os

from .base import Command


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
