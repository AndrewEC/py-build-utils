import sys
from pathlib import Path
from configparser import ConfigParser

from buildutils.commands import as_command

from .base import Plugin
from .config import PluginConfigHelper


class EnsureVenvActivePlugin(Plugin):

    """A plugin that helps ensure the project build is being executed in a specific
    named virtual environment.

    This plugin looks for configuration values under the ENSURE_VENV section of the configuration
    file. From that section it will only pull the name property.

    name: The case-insensitive name of the virtual environment the build is required to be
    executed from.
    """

    def __init__(self):
        super().__init__('ensure-virtual-env', 'Ensure build is being run from a specific virtual environment.')
        self._name = None

    def load_config(self, config: ConfigParser):
        self._name = PluginConfigHelper(self, config, 'ENSURE_VENV').prop('name')
        self._use_command(as_command('ensure-virtual-env-command', self._verify_proper_venv_active))

    def _verify_proper_venv_active(self) -> bool:
        print(f'Ensuring commands are being run in virtual environment of: [{self._name}]')
        if sys.prefix == sys.base_prefix or Path(sys.prefix).name.lower() != self._name.lower():
            print(f'Build is not being executed in expected virtual environment of: [{self._name}]')
            return False
        return True
