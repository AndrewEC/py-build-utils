import subprocess
from configparser import ConfigParser
import re

from buildutils.base import Plugin, Command, parse_python_command_string
from .config import PluginConfigHelper


class FlakePlugin(Plugin):

    """Plugin used to run a Flake8 linter against the project under test.

    This plugin looks for configuration values under the FLAKE8 section of the configuration file. From
    that section pulls the values for the properties 'command' and 'fail_on_error'.

    In addition to the aforementioned properties the flake8 command will load configuration properties from the
    default setup.cfg file. To learn more about what properties are available take a look through the flake8
    documentation: https://flake8.pycqa.org/en/latest/user/index.html

    command: specifies the exact Flake8 command to run such as: python -m flake8.

    fail_on_error: specifies if the plugin should emit an error if the flake command returns any errors or warnings.
    Can be true or false
    """

    def __init__(self):
        super().__init__('flake8', 'Run flake8 against source files.')

    def load_config(self, config: ConfigParser):
        helper = PluginConfigHelper(self, config, 'FLAKE8')
        command = helper.prop('command')
        fail_on_error = helper.bool_prop('fail_on_error', 'False')
        self._use_command(_FlakeCommand(command, fail_on_error))


class _FlakeCommand(Command):

    _ERROR_EXPRESSION = r'^.+:{1}[0-9]+:{1}[0-9]+(?::\sE){1}[0-9]+\s{1}.+$'
    _FATAL_EXPRESSION = r'^.+:{1}[0-9]+:{1}[0-9]+(?::\sF){1}[0-9]+\s{1}.+$'

    def __init__(self, command: str, fail_on_error: bool):
        super().__init__('run-flake')
        self._command = command
        self._fail_on_error = fail_on_error

    def execute(self) -> bool:
        output = self._run_subprocess()
        if output is None:
            return False

        if len(output) == 0:
            print('No linting errors to report.')
            return True

        print(f'Flask8 Lint: \n{output}')

        if self._fail_on_error and self._contains_lint_error(output):
            print('At least one linting error was identified when running flake8.')
            print('You can continue the build when linting errors are presenting using the fail_on_error option under the [FLAKE8] config')
            return False
        return True

    def _contains_lint_error(self, output: str) -> bool:
        lines = output.split('\n')
        for error_expression in [_FlakeCommand._ERROR_EXPRESSION, _FlakeCommand._FATAL_EXPRESSION]:
            pattern = re.compile(error_expression)
            first_error = next((line for line in lines if pattern.match(line) is not None), None)
            if first_error is not None:
                return True
        return False

    def _run_subprocess(self) -> str | None:
        parsed_command = parse_python_command_string(self._command)
        print(f'Executing subprocess with [{parsed_command}]')
        process = subprocess.Popen(parsed_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
        (output, err) = process.communicate()
        status = process.wait()
        if status != 0 and status != 1:
            print(f'Flake8 Error: [{err}]')
            return None
        return output
