Custom Plugins
==============

.. toctree::
   :maxdepth: 4


The current build pipeline can be extended with additional custom plugins. Creating a custom plugins requires
creating a class that extends the base **Plugin** class and implementing the required methods.

Additionally the plugin will require at least one command. You can create a command by creating a class that
overrides the base **Command** class and implements the **execute** function.

::

    class MyPlugin(Plugin):

        def __init__(self, name: str, help_text: str):
            # Required call to the Plugin constructor to initialize the plugin name and help text.
            # Note the current pipeline will not allow two plugins to be registered under the same name.
            super().__init__(name, help_text)

        def load_config(self, config: ConfigParser):
            section = config[self.name]  # Get the section of the config with the specific properties for this plugin.
            message = section['message']  # Read in a property from the config section.
            self._use_command(MyCommand(message))  # Add a command to be executed.
            #  An optional step that allows a command to be run after all other commands within the plugin.
            #  This command will even be run if a previous command in the plugin fails. Additionally, if the command
            #  registered here fails it will not stop the build process.
            #  self._use_command_for_cleanup


    class MyCommand(Command):

        def __init__(self, name: str, message: str):
            # required call to the Command constructor to initialize the command name.
            super().__init__(name)
            self._message = message

        def execute(self) -> bool:
            print(self._message)
            # Return True if the command finished successfully, otherwise return False.
            # If False is returned then the build process will be stopped and an error message will be displayed.
            return True