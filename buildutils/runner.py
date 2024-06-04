from __future__ import annotations

from typing import List

import sys
import os
from configparser import ConfigParser

from buildutils.base import Plugin
from buildutils.exceptions import PluginNotFoundException, ProfileNotFoundException, ConfigNotFoundException, \
    PropertyMissingException


class BuildConfiguration:

    """The main entry point to the build utils module.

    Allows for the configuration of the build script including setting the config properties and the
    list of plugins to execute.
    """

    _PROFILE_SECTION_TEMPLATE = 'BUILD_PROFILE:{}'
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

    def _read_plugins_from_profile(self, profile: str | None) -> List[str]:
        if profile is None:
            return []
        config = self._load_config_parser()

        profile_section_name = BuildConfiguration._PROFILE_SECTION_TEMPLATE.format(profile.upper())
        if profile_section_name not in config:
            raise ProfileNotFoundException(profile)

        profile_section = config[profile_section_name]
        if 'plugins' not in profile_section:
            raise PropertyMissingException(profile_section_name, 'plugins')
        return profile_section['plugins'].split(',')

    def build(self, profile: str | None = None, plugins: str | None = None, list_plugins=False):
        """
        Execute the build plugins in the specified order. The order in which the plugins will be executed will be
        determined in the following way.

        1. If the profile argument is present then lookup the profile from the build configuration and get the plugin
            order.
        2. If the plugins argument is present then parse the comma delimited list of plugins and execute the plugins
            in the order specified.
        3. If neither the profile nor the plugins argument are present then execute all the plugins in the order they
            were registered.

        Args:
            profile (str): The optional name of the profile from which the list of plugins to be executed will be
                pulled from.
            plugins (str): An optional comma delimited list of plugins to execute. The order in which the plugins will
                be executed will match the order in which the names appear in this parameter.
            list_plugins (bool): If True this will print the plugins and their default execution order then exit.
        """

        print(f'Using configuration file: [{self._config_file}]')
        plugins_to_execute = self._get_plugins_to_execute(profile, plugins)
        if list_plugins:
            return self.print_available_plugins(plugins_to_execute)
        self._build(plugins_to_execute)

    def _get_plugins_to_execute(self, profile: str | None, plugins: str | None) -> List[str]:
        plugins_to_execute = self._read_plugins_from_profile(profile)
        if len(plugins_to_execute) > 0:
            print(f'Using plugins specified in profile: [{profile}]')
            return plugins_to_execute

        plugins_to_execute = plugins.split(',') if plugins is not None else []
        if len(plugins_to_execute) > 0:
            print(f'Using manually specified plugins: [{plugins}]')
            return plugins_to_execute

        print('Using all available plugins in registered order.')
        return self.get_plugin_names()

    def _build(self, plugins_to_execute: List[str]):
        print(f'Executing provided plugins: [{plugins_to_execute}]')
        self._load_config(plugins_to_execute)
        self._execute_plugins(plugins_to_execute)

    def get_plugin_names(self) -> List[str]:
        return [plugin.name.lower() for plugin in self._plugins]

    def print_available_plugins(self, plugin_names: List[str]):
        print('List of available plugins:')
        print('----- ----- ----- ----- -----')
        for plugin_name in plugin_names:
            plugin = self._get_plugin_with_name(plugin_name)
            if plugin is None:
                raise PluginNotFoundException(plugin_name)
            print(str(plugin))

    def _load_config_parser(self) -> ConfigParser:
        if not os.path.isfile(self._config_file):
            raise ConfigNotFoundException(self._config_file)

        config = ConfigParser()
        config.read(self._config_file)
        return config

    def _load_config(self, plugins_to_execute: List[str]):
        config = self._load_config_parser()
        for plugin_name in plugins_to_execute:
            plugin = self._get_plugin_with_name(plugin_name)
            if plugin is None:
                raise PluginNotFoundException(plugin_name)
            print(f'Loading config for plugin: [{plugin.name}]')
            plugin.load_config(config)

    def _get_plugin_with_name(self, plugin_name: str) -> Plugin | None:
        return next((plugin for plugin in self._plugins if plugin.name.lower() == plugin_name.lower()), None)

    def _execute_plugins(self, plugins_to_execute: List[str]):
        for plugin_name in plugins_to_execute:
            plugin = self._get_plugin_with_name(plugin_name)
            if plugin is None:
                raise PluginNotFoundException(plugin_name)
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
