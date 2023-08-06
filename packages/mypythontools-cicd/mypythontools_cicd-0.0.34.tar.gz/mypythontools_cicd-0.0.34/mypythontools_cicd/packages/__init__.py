"""For example you can work with requirements or with versions here. Usually used in 'setup.py'."""

from mypythontools_cicd.packages.packages_internal import (
    get_package_setup_args,
    get_readme,
    get_requirements_files,
    get_requirements,
    get_version,
    increment_version,
    personal_setup_args_preset,
    set_version,
    validate_version,
)

__all__ = [
    "get_package_setup_args",
    "get_readme",
    "get_requirements_files",
    "get_requirements",
    "get_version",
    "increment_version",
    "personal_setup_args_preset",
    "set_version",
    "validate_version",
]
