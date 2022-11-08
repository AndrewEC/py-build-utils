from typing import Tuple

from configparser import ConfigParser

from buildutils.base import Plugin, Command


def _form_help_text(plugins: Tuple[Plugin]):
    if len(plugins) == 1:
        return plugins[0].help_text
    text = 'Run the following plugins in order:\n'
    plugin_messages = '\n'.join('\t{} - {}'.format(plugin.name, plugin.help_text) for plugin in plugins)
    return text + plugin_messages


class PluginGroup(Plugin):

    def __init__(self, alias: str, actual_plugins: Tuple[Plugin]):
        super().__init__(alias, _form_help_text(actual_plugins))
        self._actual_plugins = actual_plugins

    def load_config(self, config: ConfigParser):
        for plugin in self._actual_plugins:
            plugin.load_config(config)
            self._use_command(_PluginGroupCommand(self.name, plugin))


class _PluginGroupCommand(Command):

    def __init__(self, alias: str, actual_plugin: Plugin):
        super().__init__(f'{alias}-{actual_plugin.name}')
        self._actual_plugin = actual_plugin

    def execute(self) -> bool:
        return self._actual_plugin.execute()


def group(alias: str, *plugins: Plugin) -> PluginGroup:
    """
    Group together a various number of plugins in a pseudo plugin that can be executed as part of the regular
    build pipeline.

    This grouping allows a number of plugins to be sequentially executed using the input 'alias' value in place
    of the name of each individual plugin.

    Typically, this should be used when you have two tightly coupled plugins that must be run together, in sequence,
    in order to fulfill a larger more complicated process.

    A good example would be generating documentation using Sphinx. Sphinx requires two commands to be run,
    one to prepare the docs for generation, and one to generate the actual HTML.

    Args:
        alias (str): The name the new plugin group can be referenced by.
        plugins (Plugin): A variable length tuple specifying the plugins that should be grouped together.

    Returns:
        A new plugin group.
    """
    return PluginGroup(alias, plugins)
