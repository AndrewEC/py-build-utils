from typing import List
import os

from configparser import ConfigParser
from pathlib import Path
import shutil

from bs4 import BeautifulSoup

from buildutils.base import StatusBasedProcessCommand, ReportCheckCommand, ReportOpenCommand, Plugin, FileCleanupCommand, Command


_source_directory = Path(os.getcwd())
_testbed_directory = _source_directory.joinpath('_mutmutbed')


class MutationPlugin(Plugin):

    """Plugin to run mutation tests against the python project using mutmut.

    This plugin looks for values under the MUTATION section of the configuration file. From that section it pulls
    the values for the properties 'command', 'enable_killcount_check', 'killcount_requirement',
    and 'open_mutation_report'.

    In addition to the aforementioned properties the mutmut command will load configuration properties from
    the default setup.cfg file. To learn more about what properties are available look through the mutmut
    documentation: https://mutmut.readthedocs.io/en/latest/index.html

    command: specifies the command to run the mutation tests. Example: mutmut run

    enable_killcount_check: If true this plugin will parse the mutation test results to determine the number
    of mutants that were killed off and kill off the remainder of the build if the kill count percentage is lower
    than the specified threshold.

    killcount_requirement: The number of mutants that must be killed as a percentage of the total number of
    mutants that have been executed. This value will only be read if enable_killcount_check has been set to true.

    open_mutation_report: Specifies whether an HTML report should be opened in the default browser
    upon successful completion of the mutation test execution

    test_bed_exclude: A comma delimited list of the files and directories to not copy over when creating the test bed.
    """

    def __init__(self):
        super().__init__('mutation-test', 'Run mutation tests and measure kill count rates.')

    def load_config(self, config: ConfigParser):
        mutation_section = config['MUTATION']

        command = mutation_section['command']
        exclude = mutation_section['test_bed_exclude'].split(',')
        self._use_command(_CreateTestbedCommand(exclude))
        self._use_command(_MutationTestCommand(command))
        self._use_command(_MutationTestReportCommand())
        self._use_command(_MutationTestReportCopyCommand())

        if mutation_section['enable_killcount_check'].lower() == 'true':
            killcount_requirement = int(mutation_section['killcount_requirement'])
            self._use_command(_MutationTestCoverageCheckCommand(killcount_requirement))

        if mutation_section['open_mutation_report'].lower() == 'true':
            self._use_command(_OpenMutationTestReportCommand())

        self._use_command_for_cleanup(_MutationTestCleanupCommand())


class _ChangeDirectory:

    def __init__(self, previous_directory: Path, target_directory: Path):
        self._previous_directory = previous_directory
        self._target_directory = target_directory

    def __enter__(self):
        os.chdir(self._target_directory)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self._previous_directory)


class _CreateTestbedCommand(Command):

    def __init__(self, exclude: List[str]):
        super().__init__('mutation-create-test-bed')
        self._exclude = exclude

    def execute(self) -> bool:
        print(f'Creating testbed directory in: [{_testbed_directory}]')
        if _testbed_directory.is_dir():
            shutil.rmtree(_testbed_directory)
        os.mkdir(_testbed_directory)
        for file in self._list_files(_source_directory):
            if file.name in self._exclude:
                print(f'Not copying file since it has been marked as excluded from test bed: [{file.name}]')
                continue
            print(f'Copying: [{file.name}]')
            target_dir = _testbed_directory.joinpath(file.name)
            if file.is_dir():
                shutil.copytree(file, target_dir)
            else:
                shutil.copy(file, target_dir)
        return True

    def _list_files(self, root: Path) -> List[Path]:
        files = list(map(root.joinpath, os.listdir(root)))
        return [file for file in files if file.name != '.git' and file.name != '_mutmutbed']


class _MutationTestCommand(StatusBasedProcessCommand):

    def __init__(self, command: str):
        super().__init__('mutation-test', [-1], command)

    def execute(self) -> bool:
        with _ChangeDirectory(_source_directory, _testbed_directory):
            return super().execute()

    def _was_successful(self, status: int):
        return status != self._success_status


class _MutationTestReportCommand(StatusBasedProcessCommand):

    TESTBED_REPORT_PATH = './_mutmutbed/html/index.html'

    def __init__(self):
        super().__init__('mutation-test-report', [0], 'mutmut html')

    def execute(self):
        with _ChangeDirectory(_source_directory, _testbed_directory):
            if not super().execute():
                return False
            print(f'Temp mutation report at [{_MutationTestReportCommand.TESTBED_REPORT_PATH}]')
            return True


class _MutationTestReportCopyCommand(Command):

    def __init__(self):
        super().__init__('mutation-copy-test-report')

    def execute(self) -> bool:
        temp_report_directory = _testbed_directory.joinpath('html')
        perm_report_directory = _source_directory.joinpath('html')
        if perm_report_directory.is_dir():
            shutil.rmtree(perm_report_directory)
        shutil.copytree(temp_report_directory, perm_report_directory)
        print('Generated mutation test report can be found at: ./html/index.html')
        return True


class _MutationTestCoverageCheckCommand(ReportCheckCommand):

    _EXECUTED_MUTANT_CELL_INDEX = 1
    _SURVIVED_MUTANT_CELL_INDEX = 4
    _SOURCE_REPORT_PATH = './html/index.html'

    def __init__(self, killcount_requirement: int):
        super().__init__('mutation-test-check', _MutationTestCoverageCheckCommand._SOURCE_REPORT_PATH)
        self._killcount_requirement = killcount_requirement

    def _check_report(self, html: BeautifulSoup) -> bool:
        coverage_table_rows = html.findAll('tr')[1:]
        mutants_executed = self._calculate_total_mutants_run(coverage_table_rows)
        mutants_survived = self._calculate_total_mutants_survived(coverage_table_rows)
        mutant_kill_rate = 100 - (mutants_survived / mutants_executed * 100.0)
        if mutant_kill_rate < self._killcount_requirement:
            print(f'Mutation kill rate check failed. Expected [{self._killcount_requirement}]% kill rate but instead was [{int(mutant_kill_rate)}]%')
            return False
        else:
            print(f'Mutation kill rate check passed with [{mutant_kill_rate}]% of mutants killed')
        return True

    def _calculate_total_mutants_run(self, coverage_table_rows: List):
        return self._sum_all_cells(coverage_table_rows, _MutationTestCoverageCheckCommand._EXECUTED_MUTANT_CELL_INDEX)

    def _calculate_total_mutants_survived(self, coverage_table_rows: List):
        return self._sum_all_cells(coverage_table_rows, _MutationTestCoverageCheckCommand._SURVIVED_MUTANT_CELL_INDEX)

    def _sum_all_cells(self, coverage_table_rows: List, cell_index: int):
        cells_to_sum = [row.findAll('td')[cell_index] for row in coverage_table_rows]
        return sum([int(cell.text) for cell in cells_to_sum])


class _OpenMutationTestReportCommand(ReportOpenCommand):

    def __init__(self):
        super().__init__('open-mutation-test-report', _MutationTestReportCommand.TESTBED_REPORT_PATH)


class _MutationTestCleanupCommand(FileCleanupCommand):

    def __init__(self):
        super().__init__('mutation-test-cleanup', ['.mutmut-cache', '_mutmutbed'])
