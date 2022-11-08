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

    expectedstatus: Specifies the exit code that needs to be returned after completion of the aforementioned command
    for the commands execution to be considered successful. If the exit status returned by the command is not the
    same as the value specified in this argument then this plugin will throw an error and stop the build process.
    """

    def __init__(self, label: str, help_text: str):
        super().__init__(label, help_text)
        self._label = label

    def load_config(self, config: ConfigParser):
        section = config[self._label]

        command = section['command']
        statuses = self._parse_statuses(section['expectedstatus'])
        self._use_command(_GenericStatusCommand(self._label, command, statuses))

    def _parse_statuses(self, statuses: str) -> List[int]:
        if ',' not in statuses:
            return[int(statuses)]
        return list(map(int, statuses.split(',')))


class _GenericStatusCommand(StatusBasedProcessCommand):

    def __init__(self, label: str, command: str, statuses: List[int]):
        super().__init__(f'generic-command-{label}', statuses, command)


class GenericCleanPlugin(Plugin):

    """A generic plugin for deleting any specified number of files and/or folders.

    The section of the build configuration file that will be introspected is the one with
    """

    def __init__(self, label: str, help_text: str):
        super().__init__(label, help_text)
        self._label = label

    def load_config(self, config: ConfigParser):
        section = config[self._label]

        paths = self._parse_paths(section['paths'])
        self._use_command(_GenericCleanupCommand(self._label, paths))

    def _parse_paths(self, paths: str):
        if ',' in paths:
            return [path.strip() for path in paths.split(',')]
        return [paths.strip()]


class _GenericCleanupCommand(FileCleanupCommand):

    def __init__(self, label: str, paths: List[str]):
        super().__init__(f'generic-cleanup-command-{label}', paths)
