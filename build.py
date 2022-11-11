import click
from buildutils import BuildConfiguration
from buildutils.plugins import FlakePlugin, GenericCommandPlugin, EnsureVenvActivePlugin, group


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
            FlakePlugin(),
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
