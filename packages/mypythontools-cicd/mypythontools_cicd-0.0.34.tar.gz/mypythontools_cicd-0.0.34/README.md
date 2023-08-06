# mypythontools_cicd

Module with functionality around Continuous Integration and Continuous Delivery.

[![Python versions](https://img.shields.io/pypi/pyversions/mypythontools_cicd.svg)](https://pypi.python.org/pypi/mypythontools_cicd/) [![PyPI version](https://badge.fury.io/py/mypythontools_cicd.svg)](https://badge.fury.io/py/mypythontools_cicd) [![Downloads](https://pepy.tech/badge/mypythontools_cicd)](https://pepy.tech/project/mypythontools_cicd) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Malachov/mypythontools_cicd.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Malachov/mypythontools_cicd/context:python) [![Documentation Status](https://readthedocs.org/projects/mypythontools_cicd/badge/?version=latest)](https://mypythontools_cicd.readthedocs.io/en/latest/?badge=latest) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![codecov](https://codecov.io/gh/Malachov/mypythontools_cicd/branch/master/graph/badge.svg)](https://codecov.io/gh/Malachov/mypythontools_cicd)

Why to use this and not Travis or Circle CI? It's local and it's fast. You can setup it as a task in IDE and
if some phase fails, you know it soon and before pushing to repo.

You can also import mypythontools in your CI/CD and use it there of course.

If you are not sure whether the structure of your app will work with this code, check `project-starter-cookiecutter` on [GitHub](https://github.com/Malachov/project-starter-cookiecutter).

## Links

Official documentation - [readthedocs](https://mypythontools_cicd.readthedocs.io/)

Official repo - [GitHub](https://github.com/Malachov/mypythontools_cicd)


## Installation

Python >=3.6 (Python 2 is not supported).

Install with

```console
pip install mypythontools_cicd
```

There are many extras requirements that can be used with square brackets like for example

```console
pip install mypythontools_cicd[tests]
```

You can use `dev` which install libraries used during development like for example pylint. Most subpackages
has own extras. `'build_app','deploy', 'docs', 'git', 'misc', 'tests', 'venvs'` in particular.

There is also `cicd` which install all libraries necessary for cicd, but without dev dependencies. Last
extras are `all` which use dev as well as cicd.

## Subpackages
Package is divided into several subpackages

### build_app
Build your application to .exe with pyinstaller. It also builds javascript frontend with npm build if configured, which is used mostly in PyVueEel applications.

### cicd
Pipeline for all the other submodules, that provide configurable CI/CD.

### deploy
Build package and push it to PyPi.

### docs
Provide documentation with sphinx.

### git
Works with git. You can check branch here, commit all changes or push to repository.

### misc
Miscellaneous functions that are too small to have own subpackage, like for example formatting with black.

### packages
For example, you can work with requirements here. Usually used in 'setup.py'.

### project_paths
Subpackage where you can get paths used in your project (path to README,  \_\_init__.py etc.).

### tests
Runs tests in more venvs with different python versions, also with wsl linux if configured and create coverage.

### venvs
Works with virtual environments.

## Mypythontools

There is extra library in separate repository which is not about CICD, but normal python helpers.

https://github.com/Malachov/mypythontools

This can help you with a lot of stuff around CICD like getting project paths, generating docs, testing,
deploying to PyPi etc.