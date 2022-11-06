from .group import PluginGroup
from buildutils.base import Plugin


class PluginAlias(PluginGroup):

    def __init__(self, alias: str, actual_plugin: Plugin):
        """
        Initializes the plugin alias.

        Args:
            alias (str): The new name the underlying plugin can be referenced by.
            actual_plugin (Plugin): The underlying plugin to apply the alias to.
        """
        super().__init__(alias, (actual_plugin,))


def with_alias(alias: str, plugin: Plugin) -> PluginAlias:
    """
    Attach an alias to the plugin allowing the plugin to be referenced using a different name.

    Returns:
        A new plugin alias instance that wraps the underlying plugin so it can be referenced using a different name.
    """
    return PluginAlias(alias, plugin)
