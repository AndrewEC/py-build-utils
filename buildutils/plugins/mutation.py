from typing import List
import os

from configparser import ConfigParser
from pathlib import Path
import shutil

from bs4 import BeautifulSoup

from buildutils.base import StatusBasedProcessCommand, ReportCheckCommand, ReportOpenCommand, Plugin, FileCleanupCommand, Command
from .config import PluginConfigHelper


_source_directory = Path(os.getcwd())
_testbed_directory = _source_directory.joinpath('_testbed')


class MutationPlugin(Plugin):

    """Plugin to run mutation tests against the python project using cosmic-ray.

    This plugin looks for values under the MUTATION section of the configuration file. From that section it pulls
    the values for the properties 'config_file', 'enable_killcount_check', 'killcount_requirement',
    and 'open_mutation_report'.

    config_file: specifies the toml file the configuration will be loaded from. Ex: mutation-config.toml

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
        helper = PluginConfigHelper(self, config, 'MUTATION')

        exclude = helper.prop('test_bed_exclude').split(',')
        config_file = helper.prop('config_file')
        self._use_command(_CreateTestbedCommand(exclude))
        self._use_command(_InitSessionCommand(config_file))
        self._use_command(_ApplyOperatorFiltersCommand(config_file))
        self._use_command(_ApplyPragmaFiltersCommand())
        self._use_command(_MutationTestCommand(config_file))
        self._use_command(_MutationTestReportCommand())
        self._use_command(_MutationTestReportCopyCommand())

        if helper.bool_prop('enable_killcount_check', 'False'):
            killcount_requirement = helper.float_prop('killcount_requirement')
            self._use_command(_MutationTestCoverageCheckCommand(killcount_requirement))

        if helper.bool_prop('open_mutation_report', 'False'):
            self._use_command(ReportOpenCommand('open-mutation-test-report', _MutationTestReportCommand.TESTBED_REPORT_PATH))

        self._use_command_for_cleanup(FileCleanupCommand('mutation-test-cleanup', ['.mutations.sqlite', '_testbed']))


class _ChangeDirectory:

    def __init__(self, previous_directory: Path, target_directory: Path):
        self._previous_directory = previous_directory
        self._target_directory = target_directory

    def __enter__(self):
        os.chdir(self._target_directory)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self._previous_directory)


class _InitSessionCommand(StatusBasedProcessCommand):

    def __init__(self, config_file: str):
        super().__init__('mutation-init', [0], f'cosmic-ray init {config_file} mutations.sqlite')

    def execute(self) -> bool:
        with _ChangeDirectory(_source_directory, _testbed_directory):
            return super().execute()


class _ApplyOperatorFiltersCommand(StatusBasedProcessCommand):

    def __init__(self, config_file: str):
        super().__init__('mutation-filter-operators', [0], f'cr-filter-operators mutations.sqlite {config_file}')

    def execute(self) -> bool:
        with _ChangeDirectory(_source_directory, _testbed_directory):
            return super().execute()


class _ApplyPragmaFiltersCommand(StatusBasedProcessCommand):

    def __init__(self):
        super().__init__('mutation-filter-pragma-lines', [0], 'cr-filter-pragma mutations.sqlite')

    def execute(self) -> bool:
        with _ChangeDirectory(_source_directory, _testbed_directory):
            return super().execute()


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
        files = list(root.iterdir())
        return [file for file in files if file.name != '.git' and file.name != '_testbed']


class _MutationTestCommand(StatusBasedProcessCommand):

    def __init__(self, config_file: str):
        super().__init__('mutation-test', [-1], f'cosmic-ray exec {config_file} mutations.sqlite')

    def execute(self) -> bool:
        with _ChangeDirectory(_source_directory, _testbed_directory):
            return super().execute()

    def _was_successful(self, status: int):
        return status != self._success_status


class _MutationTestReportCommand(StatusBasedProcessCommand):

    TESTBED_REPORT_PATH = './_testbed/index.html'

    def __init__(self):
        super().__init__('mutation-test-report', [0], 'cr-html mutations.sqlite > ./index.html')

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
        temp_report_directory = _testbed_directory.joinpath('index.html')
        perm_report_directory = _source_directory.joinpath('html').joinpath('index.html')
        if perm_report_directory.is_dir():
            shutil.rmtree(perm_report_directory)
        shutil.copy(temp_report_directory, perm_report_directory)
        print('Generated mutation test report can be found at: ./html/index.html')
        return True


class _MutationTestCoverageCheckCommand(ReportCheckCommand):

    _SOURCE_REPORT_PATH = './html/index.html'

    def __init__(self, killcount_requirement: float):
        super().__init__('mutation-test-check', _MutationTestCoverageCheckCommand._SOURCE_REPORT_PATH)
        self._killcount_requirement = killcount_requirement

    def _check_report(self, html: BeautifulSoup) -> bool:
        tag_with_survivor_rate = list(html.findAll('div', attrs={'id': 'summary_info___collapse_1'}).findAll('p'))[3]
        mutant_survivor_rate = self._parse_survivor_rate(tag_with_survivor_rate)
        mutants_kills = 100 - mutant_survivor_rate
        if mutants_kills < self._killcount_requirement:
            print(f'Mutation kill rate check failed. Expected [{self._killcount_requirement}]% kill rate but only [{mutants_kills}]% of mutants were killed.')
            return False
        else:
            print(f'Mutation kill rate check passed with [{mutants_kills}]% of mutants killed.')
        return True

    def _parse_survivor_rate(self, tag: BeautifulSoup) -> float:
        text = tag.text.strip()
        starting_index = text.rfind('(')
        ending_index = text.rfind(')')
        percent_amount = text[starting_index + 1:ending_index].replace('%', '')
        return float(percent_amount)
