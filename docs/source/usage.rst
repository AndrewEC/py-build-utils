Usage
=====

.. toctree::
   :maxdepth: 4

   existing
   custom


The build utils consist of two components: build script and build configuration.

Typically these will be represented by the build.ini and build.py files.

Below is an example of a build.py script that can be invoked via the command line thanks to its integration with
Click.::

    import click
    from buildutils import BuildConfiguration
    from buildutils.plugins import CoveragePlugin, FlakePlugin,\
        GenericCommandPlugin, GenericCleanPlugin, EnsureVenvActivePlugin, group


    @click.command()
    @click.option('--profile', '-pr')
    @click.option('--plugins', '-p')
    @click.option('--list-plugins', '-l', is_flag=True)
    def main(profile: str, plugins: str, list_plugins: bool):
        (
            BuildConfiguration()
            .config('build.ini')
            .plugins(
                EnsureVenvActivePlugin(),
                GenericCleanPlugin('CLEAN', 'Remove previous build files.'),
                GenericCommandPlugin('INSTALL', 'Install required dependencies from requirements.txt file.'),
                FlakePlugin(),
                CoveragePlugin(),
                group(
                    'generate-docs',
                    GenericCommandPlugin('PREPARE_DOCS', 'Prepare Sphinx for generating documentation from inline comments.'),
                    GenericCommandPlugin('GENERATE_DOCS', 'Generate documentation from inline comments using Sphinx')
                )
            )
            .build(profile, plugins, list_plugins)
        )


Below is an example of a build.ini file used to provide the configuration values for the above build script.::

    [BUILD_PROFILE:DOCS]
    plugins = ensure-virtual-env,clean,install,generate-docs

    [ENSURE_VENV]
    name = py-timeout-venv

    [CLEAN]
    paths = .coverage,.mutmut-cache,html,htmlcov,_mutmutbed

    [INSTALL]
    command = pip install -r requirements.txt
    expectedstatus = 0

    [FLAKE8]
    command = {PYTHON_VENV} -m flake8
    fail_on_error = False

    [COVERAGE]
    command = coverage run --omit=./timeout/tests/* --source=timeout.lib --branch --module timeout.tests.__run_all
    enable_coverage_check = true
    coverage_requirement = 80
    open_coverage_report = false

    [PREPARE_DOCS]
    command = sphinx-apidoc -o docs/source/ timeout
    expectedstatus = 0

    [GENERATE_DOCS]
    command = sphinx-build -b html docs/source/ docs/build/
    expectedstatus = 0
