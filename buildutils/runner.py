from __future__ import annotations

from typing import List

import sys
import os
from configparser import ConfigParser

from buildutils.base import Plugin
from buildutils.exceptions import PluginNotFoundException


class BuildConfiguration:

    """The main entry point to the build utils module.

    Allows for the configuration of the build script including setting the config properties and the
    list of plugins to execute.
    """

    _DEFAULT_CONFIG_FILE = 'build.ini'

    def __init__(self):
        self._plugins: List[Plugin] = []
        self._config_file = BuildConfiguration._DEFAULT_CONFIG_FILE

    def config(self, config_file: str) -> BuildConfiguration:
        self._config_file = config_file
        return self

    def plugins(self, *plugins: Plugin) -> BuildConfiguration:
        self._plugins = plugins
        self._validate_plugins(*plugins)
        return self

    def _validate_plugins(self, *plugins: Plugin):
        names = set()
        for plugin in plugins:
            if plugin.name in names:
                raise ValueError(f'Two or more plugins tried to register under the same name of: [{plugin.name}]')
            names.add(plugin.name)

    def build(self, plugins_to_execute: List[str]):
        self._load_config()
        if len(plugins_to_execute) == 0:
            self._execute_plugins(self.get_plugin_names())
        self._execute_plugins(plugins_to_execute)

    def get_plugin_names(self) -> List[str]:
        return [plugin.name.lower() for plugin in self._plugins]

    def print_available_plugins(self):
        print('List of available plugins:')
        print('----- ----- ----- ----- -----')
        for plugin in self._plugins:
            print(str(plugin))

    def _load_config(self):
        if not os.path.isfile(self._config_file):
            print(f'Build config file could not be found at [{self._config_file}]')
            return

        config = ConfigParser()
        config.read(self._config_file)

        for plugin in self._plugins:
            plugin.load_config(config)

    def _get_plugin_with_name(self, plugin_name: str) -> Plugin | None:
        return next((plugin for plugin in self._plugins if plugin.name.lower() == plugin_name.lower()), None)

    def _execute_plugins(self, plugins_to_execute: List[str]):
        for plugin_name in plugins_to_execute:
            plugin = self._get_plugin_with_name(plugin_name)
            if plugin is None:
                raise PluginNotFoundException(plugin_name, 'A plugin matching the specified name could not be found.')
            try:
                print(f'\n--------------- Running Plugin: {plugin.name} ---------------')
                if not plugin.execute():
                    print(f'Plugin [{plugin.name}] reported failure. Stopping build')
                    sys.exit(1)
                print('--------------- ---------------')
            except Exception as e:
                print(f'An uncaught exception occurred while executing plugin [{plugin.name}]')
                print(e)
                sys.exit(1)
