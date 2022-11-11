class PluginNotFoundException(Exception):

    def __init__(self, plugin_name: str):
        super().__init__(f'Could not find a plugin with the following name to execute: [{plugin_name}]')


class ProfileNotFoundException(Exception):

    def __init__(self, profile: str):
        super().__init__(f'Could not find the requested build profile: [{profile}].')


class ConfigNotFoundException(Exception):

    def __init__(self, file_name: str):
        super().__init__(f'The required configuration file could not be found at: [{file_name}]')


class PropertyMissingException(Exception):

    def __init__(self, section: str, property: str):
        super().__init__(f'The property [{property}] could not be found within the config section [{section}]')


class PluginSectionMissingException(Exception):

    def __init__(self, plugin: str, section: str):
        super().__init__(f'Coudl not find the [{section}] as required for the plugin [{plugin}] in the config file.')


class PluginPropertyMissingException(Exception):

    def __init__(self, plugin: str, section: str, property: str):
        super().__init__(f'Could not find the property [{property}] within section [{section}] as required for the plugin [{plugin}].')
