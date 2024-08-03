Built In Plugins
================

.. toctree::
   :maxdepth: 4


The py-build-utils package currently contains some pre-built plugins to complete common code quality tasks.

The **configuration** part of each section indicates what values need to be added to the build.ini file to
configure each of the associated plugins.

**{PYTHON_VENV}** - You might notice this appear in some configuration files. When using one of the built-in
plugins they will attempt to substitute this with the path to the Python executable within your virtual
environment. This, of course, requires that you are running the build in a virtual environment to work.


EnsureVenvActivePlugin
~~~~~~~~~~~~~~~~~~~~~~

Responsible for ensuring a particular virtual environment is active. This should typically be executed first to
ensure all plugins are executed in said virtual environment to ensure consistent and controllable behaviour.

Configuration
^^^^^^^^^^^^^

::

    [ENSURE_VENV]
    name = name_of_your_virtual_environment


FlakePlugin
~~~~~~~~~~~

Runs flake8 and, optionally, fails the build when certain warnings or errors are detected in flake's output. Most of
the configuration of this plugin is configuration for flake. Rather than replicating flake's existing
configuration options within the plugin this will read flake config from the standard setup.cfg file where
flake's normal configuration comes from.

Configuration
^^^^^^^^^^^^^

::

    [FLAKE8]
    command = {PYTHON_VENV} -m flake8
    fail_on_error = True


CoveragePlugin
~~~~~~~~~~~~~~

The coverage plugin is designed to execute your unit tests and measure the code coverage using Python's coverage
package. Optionally, you can also fail the build if the code coverage doesn't meet a certain threshold.

The command configuration value should be replaced with the value required to execute your unit tests
under the coverage plugin. The example command assumes we are using the unittest module but unittest is not
strictly required.

Configuration
^^^^^^^^^^^^^

::

    [COVERAGE]
    command = coverage run --omit=./consumer/tests/* --source=consumer.app --branch --module consumer.tests.__run_all
    enable_coverage_check = true
    coverage_requirement = 80
    open_coverage_report = false

GenericCommandPlugin
~~~~~~~~~~~~~~~~~~~~

The generic command plugin is a plugin that allows for the execution of any arbitrary command or process and measure
it's success or failure based on the exit status of the process.

The configuration of any generic command requires two properties. The command to be run and the comma delimited
list of status codes that constitute success.

Configuration
^^^^^^^^^^^^^

::

    GenericCommandPlugin('MY_COMMAND')

::

    [MY_COMMAND]
    command = enter_your_command_here
    expected_status = 0


GenericCleanPlugin
~~~~~~~~~~~~~~~~~~

The generic clean plugin is a plugin that will delete an arbitrary set of files and directories.

This plugin accepts a comma delimited list of files and folders as input. It does not currently support
globbing.

Configuration
^^^^^^^^^^^^^

::

    GenericCleanPlugin('CLEAN')

::

    [CLEAN]
    paths = path1,path2,path3