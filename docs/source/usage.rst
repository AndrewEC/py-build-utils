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
    from buildutils.plugins import CoveragePlugin, IntegrationPlugin, MutationPlugin, FlakePlugin,\
        GenericCommandPlugin, GenericCleanPlugin, EnsureVenvActivePlugin, group


    @click.command()
    @click.option('--plugins', '-p')
    @click.option('--list-plugins', '-l', is_flag=True)
    def main(plugins: str, list_plugins: bool):
        plugin_names = plugins.split(',') if plugins is not None else []

        build_config = (
            BuildConfiguration()
            .config('build.ini')
            .plugins(
                EnsureVenvActivePlugin(),
                GenericCleanPlugin('CLEAN', 'Remove previous build files.'),
                GenericCommandPlugin('INSTALL', 'Install required dependencies from requirements.txt file.'),
                FlakePlugin(),
                CoveragePlugin(),
                IntegrationPlugin(),
                MutationPlugin(),
                group(
                    'generate-docs',
                    GenericCommandPlugin('PREPARE_DOCS', 'Prepare Sphinx for generating documentation from inline comments.'),
                    GenericCommandPlugin('GENERATE_DOCS', 'Generate documentation from inline comments using Sphinx')
                )
            )
        )

        if list_plugins:
            return build_config.print_available_plugins()

        build_config.build(plugin_names)


    if __name__ == '__main__':
        main()


Below is an example of a build.ini file used to provide the configuration values for the above build script.::

    [ENSURE_VENV]
    name = python-code-quality-venv

    [CLEAN]
    paths = .coverage,.mutmut-cache,mappings,__files,consumer-provider.json,html,htmlcov,pact-mock-service.log,log,_mutmutbed

    [INSTALL]
    command = pip install -r requirements.txt
    expectedstatus = 0

    [GENERATE]
    command = datamodel-codegen --input ./consumer/producer-open-api-spec.json --output ./consumer/app/generated/producer_models.py
    expectedstatus = 0

    [FLAKE8]
    command = {PYTHON_VENV} -m flake8
    fail_on_error = True

    [COVERAGE]
    command = coverage run --omit=./consumer/tests/* --source=consumer.app --branch --module consumer.tests._run_all
    enable_coverage_check = true
    coverage_requirement = 80
    open_coverage_report = false

    [INTEGRATION]
    command = {PYTHON_VENV} -m unittest consumer.tests.integration.integration_test

    [MUTATION]
    command = mutmut run
    test_bed_exclude = python-code-quality-venv
    enable_killcount_check = true
    killcount_requirement = 30
    open_mutation_report = false

    [PREPARE_DOCS]
    command = sphinx-apidoc -o docs/source/ consumer
    expectedstatus = 0

    [GENERATE_DOCS]
    command = sphinx-build -b html docs/source/ docs/build/
    expectedstatus = 0
