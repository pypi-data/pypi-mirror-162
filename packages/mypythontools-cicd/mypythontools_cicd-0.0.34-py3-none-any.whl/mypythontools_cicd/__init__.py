"""Module with functionality around Continuous Integration and Continuous Delivery.

.. image:: https://img.shields.io/pypi/pyversions/mypythontools_cicd.svg
    :target: https://pypi.python.org/pypi/mypythontools_cicd/
    :alt: Python versions

.. image:: https://badge.fury.io/py/mypythontools_cicd.svg
    :target: https://badge.fury.io/py/mypythontools_cicd
    :alt: PyPI version

.. image:: https://pepy.tech/badge/mypythontools_cicd
    :target: https://pepy.tech/project/mypythontools_cicd
    :alt: Downloads

.. image:: https://img.shields.io/lgtm/grade/python/github/Malachov/mypythontools_cicd.svg
    :target: https://lgtm.com/projects/g/Malachov/mypythontools_cicd/context:python
    :alt: Language grade: Python

.. image:: https://readthedocs.org/projects/mypythontools_cicd/badge/?version=latest
    :target: https://mypythontools_cicd.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License: MIT

.. image:: https://codecov.io/gh/Malachov/mypythontools_cicd/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/Malachov/mypythontools_cicd
    :alt: Codecov

Why to use this and not Travis or Circle CI? It's local and it's fast. You can setup it as a task in IDE and
if some phase fails, you know it soon and before pushing to repo.

You can also import mypythontools in your CI/CD and use it there of course.

If you are not sure whether the structure of your app will work with this code, check
`project-starter-cookiecutter` on https://github.com/Malachov/project-starter-cookiecutter

Links
-----

Official documentation - https://mypythontools_cicd.readthedocs.io

Official repo - https://github.com/Malachov/mypythontools_cicd


Installation
------------

Python >=3.6 (Python 2 is not supported).

Install with::

    pip install mypythontools_cicd
    
There are many extras requirements that can be used with square brackets like for example

    pip install mypythontools_cicd[tests]

You can use `dev` which install libraries used during development like for example pylint. Most subpackages
has own extras. `'build','deploy', 'docs', 'git', 'misc', 'tests', 'venvs'` in particular.

There is also `cicd` which install all libraries necessary for cicd, but without dev dependencies. Last
extras is `all` which use dev as well as cicd.

Subpackages
-----------
Package is divided into several subpackages

:py:mod:`mypythontools_cicd.build_app`
--------------------------------------
Build your application to .exe with pyinstaller. It also builds javascript frontend with npm build if configured,
which is used mostly in PyVueEel applications.

:py:mod:`mypythontools_cicd.cicd`
----------------------------------
Pipeline for all the other submodules, that provide configurable CI/CD.

:py:mod:`mypythontools_cicd.deploy`
-----------------------------------
Build package and push it to PyPi.

:py:mod:`mypythontools_cicd.docs`
-----------------------------------
Provide documentation with sphinx.

:py:mod:`mypythontools_cicd.git`
--------------------------------
Works with git. You can check branch here, commit all changes or push to repository.

:py:mod:`mypythontools_cicd.misc`
--------------------------------
Miscellaneous functions that are too small to have own subpackage, like for example formatting with black.

:py:mod:`mypythontools_cicd.packages`
-------------------------------------
For example, you can work with requirements here. Usually used in 'setup.py'.

:py:mod:`mypythontools_cicd.project_paths`
------------------------------------------
Subpackage where you can get paths used in your project (path to README,  `__init__.py` etc.).

:py:mod:`mypythontools_cicd.tests`
----------------------------------
Runs tests in more venvs with different python versions, also with wsl linux if configured and create coverage.

:py:mod:`mypythontools_cicd.venvs`
----------------------------------
Works with virtual environments.


Mypythontools
=============

There is extra library in separate repository which is not about CICD, but normal python helpers.

https://github.com/Malachov/mypythontools

This can help you with a lot of stuff around CICD like getting project paths, generating docs, testing,
deploying to PyPi etc.
"""
from mypythontools_cicd import build_app, deploy, packages, cicd, project_paths, tests, venvs

__all__ = ["build_app", "deploy", "packages", "project_paths", "cicd", "tests", "venvs"]

__version__ = "0.0.34"

__author__ = "Daniel Malachov"
__license__ = "MIT"
__email__ = "malachovd@seznam.cz"
