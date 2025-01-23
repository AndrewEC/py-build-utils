from abc import abstractmethod
import os

from bs4 import BeautifulSoup

from .base import Command


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
