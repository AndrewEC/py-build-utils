from typing import List

from configparser import ConfigParser

from buildutils.base import Plugin, StatusBasedProcessCommand, FileCleanupCommand
from .config import PluginConfigHelper


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

    def load_config(self, config: ConfigParser):
        helper = PluginConfigHelper(self, config)

        command = helper.prop('command')
        statuses = helper.int_list_prop('expectedstatus')

        command_name = f'generic-command-{self.name}'
        self._use_command(StatusBasedProcessCommand(command_name, statuses, command))

    def _parse_statuses(self, statuses: str) -> List[int]:
        if ',' not in statuses:
            return[int(statuses)]
        return list(map(int, statuses.split(',')))


class GenericCleanPlugin(Plugin):

    """A generic plugin for deleting any specified number of files and/or folders.

    The section of the build configuration file that will be introspected is the one with
    """

    def __init__(self, label: str, help_text: str):
        super().__init__(label, help_text)

    def load_config(self, config: ConfigParser):
        paths = PluginConfigHelper(self, config).list_prop('paths')
        self._use_command(FileCleanupCommand(f'generic-cleanup-command-{self.name}', paths))

    def _parse_paths(self, paths: str):
        if ',' in paths:
            return [path.strip() for path in paths.split(',')]
        return [paths.strip()]
