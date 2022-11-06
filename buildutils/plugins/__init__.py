from .coverage import CoveragePlugin
from .integration import IntegrationPlugin
from .mutation import MutationPlugin
from .flake import FlakePlugin
from .generic import GenericCommandPlugin, GenericCleanPlugin
from .ensure_env import EnsureVenvActivePlugin
from .alias import PluginGroup, with_alias
from .group import PluginGroup, group_plugins
