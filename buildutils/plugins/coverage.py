from configparser import ConfigParser

from bs4 import BeautifulSoup

from buildutils.base import Plugin, StatusBasedProcessCommand, ReportCheckCommand, ReportOpenCommand, FileCleanupCommand
from .config import PluginConfigHelper


class CoveragePlugin(Plugin):

    """Plugin used to execute unit tests and generate coverage reports.

    This plugin looks for configuration values under the COVERAGE section of the configuration file. From that section
    it pulls the values for 'command', 'enable_coverage_check', 'coverage_requirement', and 'open_coverage_report'.

    command: Specifies the coverage command to execute. For example:
    coverage run --omit=./consumer/tests/* --source=<source_module> --branch --module <test_module>

    enable_coverage_check: If true the plugin will check the code coverage measured after unit test execution and
    flag the build as a failure if the coverage is below the threshold specified by the coverage_requirement value.

    coverage_requirement: Specifies the required code coverage percentage that must be met for the build to pass.
    This value should be a number between 0 and 100. This value will only be read if enable_coverage_check is true.

    open_coverage_report: If true the plugin will open the coverage report after execution of the unit tests has
    completed assuming that the coverage requirement has either been met or skipped.
    """

    REPORT_PATH = './htmlcov/index.html'

    def __init__(self):
        super().__init__('coverage-test', 'Run unit tests and measure code coverage using the Python Coverage package.')

    def load_config(self, config: ConfigParser):
        helper = PluginConfigHelper(self, config, 'COVERAGE')

        command = helper.prop('command')
        self._use_command(StatusBasedProcessCommand('coverage', [0], command))  # Run the coverage package
        self._use_command(_CoverageReportCommand())  # Generate the coverage HTML report

        if helper.bool_prop('enable_coverage_check', 'False'):
            coverage_requirement = helper.int_prop('coverage_requirement')
            self._use_command(_CoverageCheckCommand(coverage_requirement))  # Check if code coverage thresholds are met

        if helper.bool_prop('open_coverage_report', 'False'):
            self._use_command(ReportOpenCommand('open-coverage-report', CoveragePlugin.REPORT_PATH))  # Open coverate HTML report

        self._use_command_for_cleanup(FileCleanupCommand('coverage-cleanup', ['.coverage']))


class _CoverageReportCommand(StatusBasedProcessCommand):

    def __init__(self):
        super().__init__('coverage-report', [0], 'coverage html')

    def execute(self):
        if not super().execute():
            return False
        print(f'Coverage report has been generated. It can be found at [{CoveragePlugin.REPORT_PATH}].')
        return True


class _CoverageCheckCommand(ReportCheckCommand):

    def __init__(self, coverage_requirement: int):
        super().__init__('coverage-check', CoveragePlugin.REPORT_PATH)
        self._coverage_requirement = coverage_requirement

    def _check_report(self, html: BeautifulSoup) -> bool:
        total_coverage_row = html.findAll('tr', {'class': 'total'})[0]
        total_coverage_cell = total_coverage_row.findAll('td', {'class': 'right'})[0]
        total_coverage_percent = int(total_coverage_cell.text.replace('%', ''))
        if total_coverage_percent < self._coverage_requirement:
            print(f'Coverage check failed. Expected [{self._coverage_requirement}]% coverage instead was [{total_coverage_percent}]%')
            return False
        else:
            print(f'Coverage check passed with coverage at [{total_coverage_percent}]%')
        return True
