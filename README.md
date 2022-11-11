# build-utils
build-utils is a simple plugin based build system for running sequential commands to build, test, package, and
document a python project.

It allows you to write a simple python script to execute a series of build steps. The build steps consist of
a series of plugins that are executed sequentially. Each plugin can then execute a series of sequential commands.

Currently, this utility has specialized plugins for executing the following:
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
```

### Example build.ini File
```
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
```