from typing import List

from configparser import ConfigParser

from buildutils.base import Plugin
from buildutils.exceptions import PluginSectionMissingException, PluginPropertyMissingException


class PluginConfigHelper:

    """
    Utility to help read values from the configuration parser or throw the appropriate exception where
    no value can be read.
    """

    def __init__(self, plugin: Plugin, config: ConfigParser, section_name: str = None):
        self._section_name = section_name if section_name is not None else plugin.source_name
        if self._section_name not in config:
            raise PluginSectionMissingException(plugin.name, self._section_name)

        self._plugin_name = plugin.name
        self._section = config[self._section_name]

    def prop(self, name: str, default_value: str | None = None) -> str:
        """
        Attempts to load a value from the appropriate section of the config parser. Will throw an exception
        if the name of the property cannot be found within the config section and if no default value
        has been specified.

        Args:
            name (str): The name of the property to load.
            default_value (str): An optional value to return if the property cannot be found.
        """

        if name not in self._section:
            if default_value is not None:
                return default_value
            raise PluginPropertyMissingException(self._plugin_name, self._section_name, name)
        return self._section[name]

    def list_prop(self, name: str, delimiter: str = ',', default_value: str | None = None) -> List[str]:
        return self.prop(name, default_value).split(delimiter)

    def int_list_prop(self, name: str, delimiter: str = ',', default_value: str | None = None) -> List[int]:
        return list(map(int, self.list_prop(name, delimiter, default_value)))

    def bool_prop(self, name: str, default_value: str | None = None) -> bool:
        return self.prop(name, default_value).lower() in ['true', '1', 't', 'y', 'yes']

    def int_prop(self, name: str, default_value: str | None = None) -> int:
        return int(self.prop(name, default_value))
