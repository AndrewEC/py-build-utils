# build-utils
build-utils is a simple plugin based build system for running sequential commands to build, test, package, and
document a python project.

It allows you to write a simple python script to execute a series of build steps. The build steps consist of
a series of plugins that are executed sequentially. Each plugin can then execute a series of sequential commands.

Currently this utility has specialized plugins for executing the following:
* Ensure a particular virtual environment is active
* Clean previous build artifacts and directories
* Flake8 static code scanning
* Unit tests with optional code coverage checks
* Integration tests
* Mutation tests with optional kill count checks
* Automated documentation generation using Sphinx


## Usage

### Example build.py File
```python
import click
from buildutils import BuildConfiguration
from buildutils.plugins import CoveragePlugin, IntegrationPlugin, MutationPlugin, FlakePlugin,\
    GenericCommandPlugin, GenericCleanPlugin, EnsureVenvActivePlugin, with_alias, group_plugins


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
            with_alias('clean', GenericCleanPlugin('CLEAN', 'Remove previous build files.')),
            with_alias('install', GenericCommandPlugin('INSTALL', 'Install required dependencies from requirements.txt file.')),
            with_alias('generate-models', GenericCommandPlugin('GENERATE', 'Generate OpenAPI models from spec file.')),
            FlakePlugin(),
            CoveragePlugin(),
            IntegrationPlugin(),
            MutationPlugin(),
            group_plugins(
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

```

### Example build.ini File
```
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
```