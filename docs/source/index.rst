.. consumer documentation master file, created by
   sphinx-quickstart on Thu Jun 17 08:18:03 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to py-build-utils's documentation!
==========================================

build-utils is a simple plugin based build system for running sequential commands to build, test, package, and document
a python project.

It allows you to write a simple python script to execute a series of build steps. The build steps consist of a series
of plugins that are executed sequentially. Each plugin can then execute a series of sequential commands.

Currently this utility has specialized plugins for executing the following:

* Ensure a particular virtual environment is active
* Clean previous build artifacts and directories
* Flake8 static code scanning
* Unit tests with optional code coverage checks
* Integration tests
* Mutation tests with optional kill count checks
* Automated documentation generation using Sphinx


:doc:`usage`
    How to initialize the repository and utilize the example run script.

:doc:`modules`
    A technical reference to the existing APIs.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   usage
   modules
