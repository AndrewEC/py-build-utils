from typing import List

from configparser import ConfigParser

from buildutils.base import Plugin, StatusBasedProcessCommand, FileCleanupCommand


class GenericCommandPlugin(Plugin):

    """A generic plugin that allows the execution of an arbitrary command and checks if the command
    was successful based on the exit status.

    In this plugin the section of configuration file to be introspected will be determined by the
    'label' argument provided to the constructor.

    Within the section specified in the 'label' argument it will lookup the properties named 'command' and
    'expectedstatus'.

    command: Specifies the command line command that will be executed.

    expectedstatus: Specifies the exit that needs to be returned after completion of the aforementioned command.
    If the exit status returned by the command is not the same as the value specified in this argument then
    this plugin will throw an error and stop the build process.
    """

    def __init__(self, label: str, help_text: str):
        super().__init__(f'generic-command-{label}', help_text)
        self._label = label

    def load_config(self, config: ConfigParser):
        section = config[self._label]

        command = section['command']
        success_status = int(section['expectedstatus'])
        self._use_command(GenericStatusCommand(self._label, command, success_status))


class GenericStatusCommand(StatusBasedProcessCommand):

    def __init__(self, label: str, command: str, status: int):
        super().__init__(f'generic-command-{label}', status, command)


class GenericCleanPlugin(Plugin):

    """A generic plugin for deleting any specified number of files and/or folders.

    The section of the build configuration file that will be introspected is the one with
    """

    def __init__(self, label: str, help_text: str):
        super().__init__(f'generic-clean-plugin-{label}', help_text)
        self._label = label

    def load_config(self, config: ConfigParser):
        section = config[self._label]

        paths = self._parse_paths(section['paths'])
        self._use_command(GenericCleanupCommand(self._label, paths))

    def _parse_paths(self, paths: str):
        if ',' in paths:
            return [path.strip() for path in paths.split(',')]
        return [paths]


class GenericCleanupCommand(FileCleanupCommand):

    def __init__(self, label: str, paths: List[str]):
        super().__init__(f'generic-cleanup-command-{label}', paths)
