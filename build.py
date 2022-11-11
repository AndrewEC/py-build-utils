import click
from buildutils import BuildConfiguration
from buildutils.plugins import FlakePlugin, GenericCommandPlugin, EnsureVenvActivePlugin, group


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
            FlakePlugin(),
            group(
                'generate-docs',
                GenericCommandPlugin('PREPARE_DOCS', 'Prepare Sphinx for generating documentation from inline comments.'),
                GenericCommandPlugin('GENERATE_DOCS', 'Generate documentation from inline comments using Sphinx')
            )
        )
        .build(profile, plugins, list_plugins)
    )


if __name__ == '__main__':
    main()
