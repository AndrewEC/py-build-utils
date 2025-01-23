import sys
from pathlib import Path


_PYTHON_TEMPLATE = '{PYTHON_VENV}'
_PIP_TEMPLATE = '{PIP_VENV}'


def parse_python_command_string(command: str) -> str:
    """
    Replaces the python env template value in the command string with the appropriate value. This aims to identify
    if the current command is being executed within the context of a virtual environment, identify the environment
    and the path to the python binary, and replace the {PYTHON_ENV} placeholder in the command string with the
    absolute path to the python binary.
    """

    if sys.prefix == sys.base_prefix or (_PYTHON_TEMPLATE not in command and _PIP_TEMPLATE not in command):
        return command
    python_executable_path = str(Path(sys.prefix).joinpath('Scripts').joinpath('python'))
    pip_executable_path = str(Path(sys.prefix).joinpath('Scripts').joinpath('pip'))
    return command.replace(_PYTHON_TEMPLATE, python_executable_path).replace(_PIP_TEMPLATE, pip_executable_path)
