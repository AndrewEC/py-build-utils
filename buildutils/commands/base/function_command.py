from typing import Callable

from .command import Command


class FunctionCommand(Command):

    """
    A bare-bones command that wraps a function, so it can be executed as part of a plugin.
    """

    def __init__(self, name: str, function: Callable[[], bool]):
        super().__init__(name)
        self._function = function

    def execute(self) -> bool:
        return self._function()


def as_command(name: str, function: Callable[[], bool]) -> Command:
    """
    Wraps a function in a command, so it can be executed as part of a plugin in the build process.
    """

    return FunctionCommand(name, function)
