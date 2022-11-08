from configparser import ConfigParser

from buildutils.base import StatusBasedProcessCommand, Plugin, FileCleanupCommand


class IntegrationPlugin(Plugin):

    """Plugin to run integration tests against the python project.

    This plugin looks for values under the INTEGRATION section of the configuration file. From that section
    it pulls the values for the 'command' property.

    command: Specifies the command to run the integration tests. Example: python -m unittest <test_class>
    """

    def __init__(self):
        super().__init__('integration-test', 'Run integration tests without code coverage checks.')

    def load_config(self, config: ConfigParser):
        integration_section = config['INTEGRATION']

        command = integration_section['command']
        self._use_command(_IntegrationTestCommand(command))
        self._use_command_for_cleanup(_IntegrationCleanupCommand())


class _IntegrationTestCommand(StatusBasedProcessCommand):

    def __init__(self, command: str):
        super().__init__('integration-test', [0], command)


class _IntegrationCleanupCommand(FileCleanupCommand):

    def __init__(self):
        super().__init__('coverage-cleanup', ['__files', 'mappings', 'consumer-provider.json', 'pact-mock-service.log'])
