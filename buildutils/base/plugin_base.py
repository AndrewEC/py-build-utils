from typing import List

from abc import ABC, abstractmethod
import traceback
from configparser import ConfigParser

from .command_base import Command


class Plugin(ABC):

    """
    A high level abstract definition of a Plugin. This provides the necessary definition for creating custom
    plugins that are interoperable with the existing build system.

    A plugin is a definition containing a list of commands. When the plugin is executed it will execute each of the
    commands registered to the plugin in the order they were registered.

    The "success" of the plugin's execution is derived from the success of the command's execution. If a command fails
    the command fails then the plugin will short-circuit and report a failure back to the main build pipeline.
    """

    def __init__(self, name: str, help_text: str):
        """
        Initializes the plugin.

        Args:
            name (str): The name of the plugin. A unique name is required for each plugin registered. The names can be
            used to specify a subset of all the registered plugins that should be executed.
            help_text (str): A informational message regarding the general purpose of the plugin.
        """
        self.name = name
        self.help_text = help_text
        self._commands: List[Command] = []
        self._cleanup_command: Command | None = None

    def __repr__(self) -> str:
        return f'{self.name} - {self.help_text}'

    def _use_command(self, command: Command):
        self._commands.append(command)

    def _use_command_for_cleanup(self, command: Command):
        self._cleanup_command = command

    @abstractmethod
    def load_config(self, config: ConfigParser):
        """
        Initializes the plugin by loading values from a previously parsed configuration file.

        Args:
            config (ConfigParser): The config parser instance containing a reference to the values parsed from the
            specified config file.
        """
        pass

    def execute(self) -> bool:
        """
        Executes the plugin. The plugin will execute the series of registered commands in the order in which the
        command were registered.

        Returns:
            True if the execution of the command completed without any errors, otherwise false.
        """

        for command in self._commands:
            try:
                print(f'Executing command [{command.name}]')
                if not command.execute():
                    print(f'Command [{command.name}] reported a failure. Stopping build.')
                    self._run_cleanup()
                    return False
            except Exception:
                print(f'An uncaught exception occurred while running command [{command.name}]')
                traceback.print_exc()
                self._run_cleanup()
                return False
        self._run_cleanup()
        return True

    def _run_cleanup(self):
        if self._cleanup_command is not None:
            print(f'Running cleanup command [{self._cleanup_command.name}]')
            try:
                if not self._cleanup_command.execute():
                    print(f'Cleanup command [{self._cleanup_command.name}] reported failure.')
            except Exception as e:
                print(f'An uncaught exception occurred while running cleanup command [{self._cleanup_command.name}]')
                print(e)
                pass
