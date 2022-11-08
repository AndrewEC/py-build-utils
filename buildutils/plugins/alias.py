from .group import PluginGroup
from buildutils.base import Plugin


class PluginAlias(PluginGroup):

    def __init__(self, name: str, actual_plugin: Plugin):
        """
        Initializes the plugin alias.

        Args:
            name (str): The new name the underlying plugin can be referenced by.
            actual_plugin (Plugin): The underlying plugin to apply the alias to.
        """
        super().__init__(name, (actual_plugin,))


def alias(name: str, plugin: Plugin) -> PluginAlias:
    """
    Attach an alias to the plugin allowing the plugin to be referenced using a different name.

    Returns:
        A new plugin alias instance that wraps the underlying plugin so it can be referenced using a different name.
    """
    return PluginAlias(name, plugin)
