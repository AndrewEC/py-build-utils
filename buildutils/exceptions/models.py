class PluginNotFoundException(Exception):

    def __init__(self, plugin_name: str, message: str):
        super().__init__(message)
        self.plugin_name = plugin_name
