"""Module with functions for 'packages' subpackage."""

from __future__ import annotations
from typing import Sequence, Any
from pathlib import Path
import os
import pkg_resources
import re

from typing_extensions import Literal
from mypythontools.paths import validate_path, PathLike

from mypythontools_cicd.project_paths import PROJECT_PATHS

# Lazy import
# from setuptools import find_packages


def get_requirements_files(
    requirements: Literal["infer"] | PathLike | Sequence[PathLike], path: PathLike = PROJECT_PATHS.root
) -> list[Path]:
    """Consolidate requirements into list of paths.

    Args:
        requirements (Literal["infer"] | PathLike | Sequence[PathLike]): E.g. ["requirements.txt",
            "requirements_dev.txt"]. If 'infer', then every file where requirements is in the name is used.
            It working with one level of nested folder if requirements is in the name of the file or folder.
        path (PathLike, optional): If using just names or relative path, and not found, define the root.
            It's also necessary when using another referenced files. If inferring files, it's used to search.
            Defaults to PROJECT_PATHS.root.

    Returns:
        list[Path]: List of paths to requirements files.

    Raises:
        RuntimeError: If no requirements found with 'infer'.
    """

    if requirements == "infer":

        requirements_files = []
        path = validate_path(path)
        for i in [*path.glob("*"), *path.glob("*/*")]:
            if "requirements" in i.as_posix().lower() and i.suffix == ".txt":
                requirements_files.append(i)

        if not requirements_files:
            raise RuntimeError("No requirements found.")

    else:
        if isinstance(requirements, (Path, str, os.PathLike)):
            requirements = [requirements]

        # Enforce Path type and validate if exists
        requirements_files = []
        for req in requirements:
            existing_file = None

            if Path(req).exists():
                existing_file = Path(req)
            elif (Path(path) / req).exists():
                existing_file = Path(path) / req
            else:
                for i in path.glob("*/*"):
                    if i.name == req:
                        existing_file = i
                        break

                if not existing_file:
                    raise FileNotFoundError(
                        f"Requirements file {req} not found. File may be referenced from another "
                        "requirements. Try to use appropriate 'path' parameter."
                    )
            requirements_files.append(existing_file)

    return requirements_files


def get_requirements(
    files: Literal["infer"] | PathLike | Sequence[PathLike], path: PathLike = PROJECT_PATHS.root
) -> list[str]:
    """Get requirements into variable usually used in setup.py.

    Args:
        files (Literal["infer"] | PathLike | Sequence[PathLike]): E.g. ["requirements.txt",
            "requirements_dev.txt"]. If 'infer', then every file where requirements is in the name is used.
            It can be also absolute paths.
        path (PathLike, optional): If using just names or relative path, and not found, define the root.
            It's also necessary when using another referenced files. If inferring files, it's used to search.
            Defaults to PROJECT_PATHS.root.

    Returns:
        list[str]: List of requirements

    Raises:
        RuntimeError: If no requirements files found with 'infer'.
    """
    files = get_requirements_files(files, path)
    all_requirements = []

    for file in files:

        with open(file) as f:
            requirements = f.readlines()
        requirements = [i.strip("\r\n") for i in requirements if i.strip("\r\n")]

        # narrow_requirements calls recursively get_requirements so it can have another -r reference
        requirements = narrow_requirements(requirements, path)
        requirements = [str(requirement) for requirement in pkg_resources.parse_requirements(requirements)]
        all_requirements.extend(requirements)

    return all_requirements


def narrow_requirements(requirements: list[str], path: PathLike = "requirements") -> list[str]:
    """If there is another requirements file reference in requirements.txt, this will replace it with its
    requirements it contains.

    Args:
        requirements (list[str]): List of requirements. You can parse it from file with `get_requirements`.
        path (PathLike, optional): Path with referenced files. Defaults to "requirements".

    Returns:
        list[str]: List of plain pep 508 compatible requirements.
    """
    path = validate_path(path, "'narrow_requirements' failed", "Path with referenced requirements")

    for i in requirements:
        if i.startswith("-r "):
            req_name = i[3:].strip("\r\n")
            requirements.extend(get_requirements(req_name, path=path))
    requirements = [i for i in requirements if not i.startswith("-r ")]
    return requirements


def validate_version(version: str):
    """Check whether parsed version is valid.

    Args:
        version (str): E.g "1.0.1"

    Returns:
        bool: Whether is valid.
    """
    return version == "increment" or (
        len(version.split(".")) == 3 and all([i.isdecimal() for i in version.split(".")])
    )


def get_readme() -> str:
    """Get README content into variable usually used in setup.py.

    Returns:
        str: Content.
    """
    with open(PROJECT_PATHS.readme.as_posix()) as readme_file:
        readme = readme_file.read()
    return readme


def get_version(init_path: None | PathLike = None) -> str:
    """Get version info from `__init__.py` file.

    Args:
        init_path (None | PathLike, optional): Path to `__init__.py` file. If None, will be inferred.
            Defaults to None.

    Returns:
        str: String of version from `__init__.py`.

    Raises:
        ValueError: If no `__version__` is find. Try set init_path...

    Example:
        >>> version = get_version()
        >>> len(version.split(".")) == 3 and all([i.isdecimal() for i in version.split(".")])
        True
    """
    init_path = init_path if init_path else PROJECT_PATHS.init
    try:
        init_path = validate_path(init_path)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Setting version failed. '__init__.py' not found on '{init_path}'."
        ) from None

    with open(init_path.as_posix(), "r") as init_file:
        version = re.findall('__version__ = "(.*)"', init_file.read())[0]

    if validate_version(version):
        return version
    else:
        raise RuntimeError("Version not found in __init__.py")


def set_version(
    version: str = "increment",
    init_path: None | PathLike = None,
) -> None:
    """Change your version in your `__init__.py` file.

    Args:
        version (str, optional): Form that is used in `__init__`, so for example "1.2.3". Do not use 'v'
            appendix. If version is 'increment', it will increment your `__version__` in you `__init__.py` by
            0.0.1. Defaults to "increment".
        init_path (None | PathLike, optional): Path of file where `__version__` is defined.
            Usually `__init__.py`. If None, will be inferred. Defaults to None.

    Raises:
        ValueError: If no `__version__` is find.
    """
    init_path = (
        validate_path(init_path, "Setting version failed", "__init__.py") if init_path else PROJECT_PATHS.init
    )

    is_valid = validate_version(version)

    if not is_valid:
        raise ValueError(
            "Version not validated. Version has to be of form '1.2.3'. Three digits and two dots. "
            f"You used {version}"
        )

    with open(init_path.as_posix(), "r") as init_file:

        list_of_lines = init_file.readlines()

        found = False

        for i, j in enumerate(list_of_lines):
            if j.startswith("__version__"):

                found = True

                delimiter = '"' if '"' in j else "'"
                delimited = j.split(delimiter)

                if version == "increment":
                    delimited[1] = increment_version(delimited[1])
                else:
                    delimited[1] = version

                list_of_lines[i] = delimiter.join(delimited)
                break

        if not found:
            raise ValueError("__version__ variable not found in __init__.py. Try set init.")

    with open(init_path.as_posix(), "w") as init_file:

        init_file.writelines(list_of_lines)


def increment_version(version: str) -> str:
    """Increment patch version by one.

    Args:
        version (str): String format. It can include 'v' prefix.

    Returns:
        str: Incremented version

    Example:
        >>> increment_version("1.2.3")
        '1.2.4'
        >>> increment_version("v1.2.3")
        'v1.2.4'
    """
    version_list = version.split(".")
    version_list[2] = str(int(version_list[2]) + 1)
    return ".".join(version_list)


def get_package_setup_args(
    name: str, development_status: Literal["alpha", "beta", "stable"] = "alpha"
) -> dict[str, Any]:
    """Get setup args, that usually repeats across projects.

    Args:
        name (str): Name used to generate some params.
        development_status (Literal['alpha', 'beta', 'stable']): Project phase. Defaults to 'alpha'.

    Returns:
        dict[str, Any]: Attributes used in `setup.py`. E.g. license, platform
            or long_description_content_type.
    """
    from setuptools import find_packages

    status = {
        "alpha": "Development Status :: 3 - Alpha",
        "beta": "Development Status :: 4 - Beta",
        "stable": "Development Status :: 5 - Production/Stable",
    }[development_status]

    classifiers = [
        status,
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]

    return {
        "license": "mit",
        "include_package_data": True,
        "long_description_content_type": "text/markdown",
        "packages": find_packages(exclude=("tests**",)),
        "platforms": "any",
        "python_requires": ">=3.7",
        "url": f"https://github.com/Malachov/{name}",
        "name": name,
        "version": get_version(),
        "classifiers": classifiers,
    }


personal_setup_args_preset = {
    "author_email": "malachovd@seznam.cz",
    "author": "Daniel Malachov",
}
