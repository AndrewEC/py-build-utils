from setuptools import setup

if __name__ == '__main__':
    setup(
        name='buildutils',
        version='1.0',
        description='Python build utilities for building python apps',
        author='Andrew Cumming',
        author_email='andrew.cumming@gmail.com',
        url='https://github.com/AndrewEC/py-build-utils',
        packages=[
            'buildutils',
            'buildutils.commands',
            'buildutils.commands.base',
            'buildutils.plugins',
            'buildutils.plugins.base',
            'buildutils.exceptions'
        ],
        install_requires=[
            'beautifulsoup4==4.12.3'
        ]
    )
