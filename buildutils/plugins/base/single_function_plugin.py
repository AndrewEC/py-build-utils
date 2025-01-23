from typing import Callable
from configparser import ConfigParser

from .plugin import Plugin

from buildutils.commands import as_command


class SingleFunctionPlugin(Plugin):

    def __init__(self, name: str, help_text: str, function: Callable[[], bool]):
        super().__init__(name, help_text)
        self._command = as_command(f'{name}-command', function)

    def load_config(self, config: ConfigParser):
        self._use_command(self._command)


def as_plugin(name: str, help_text: str, function: Callable[[], bool]) -> Plugin:
    """
    Wraps a single function in the context of a plugin so it can be executed as part of the build process.
    """

    return SingleFunctionPlugin(name, help_text, function)
