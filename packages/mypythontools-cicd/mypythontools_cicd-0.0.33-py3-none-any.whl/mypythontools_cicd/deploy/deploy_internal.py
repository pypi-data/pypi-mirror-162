"""Module with functions for 'deploy' subpackage."""

from __future__ import annotations
import os

from typing_extensions import Literal

from mypythontools.paths import validate_path, PathLike
from mypythontools.misc import delete_files, print_progress
from mypythontools.system import check_script_is_available, terminal_do_command, PYTHON

from mypythontools_cicd.project_paths import PROJECT_PATHS
from mypythontools_cicd.venvs import Venv


def deploy_to_pypi(
    setup_path: None | PathLike = None,
    clean: bool = True,
    verbosity: Literal[0, 1, 2] = 1,
    pep517: bool = False,
    venv: None | Venv = Venv("venv"),
) -> None:
    """Publish python library to PyPi.

    Username and password are set with env vars `TWINE_USERNAME` and `TWINE_PASSWORD`.

    Note:
        You need working `setup.py` file. If you want to see example, try the one from project-starter on

        https://github.com/Malachov/mypythontools/blob/master/content/project-starter/setup.py

    Args:
        setup_path (None | PathLike, optional): Function suppose, that there is a setup.py somewhere in cwd.
            If not, path will be inferred. Build and dist folders will be created in same directory.
            Defaults to None.
        clean (bool, optional): Whether delete created build and dist folders.
        verbosity (Literal[0, 1, 2], optional): If 0, prints nothing, if 1, then one line description of what
            happened is printed. If 3, all the results from terminal are printed. Defaults to 1.
        pep517 (bool, optional): Whether using PEP 517, that use pyproject.toml to build distribution. Without
            it it's faster, but with it, pyproject.TOML can be used. Defaults to False.
        venv (None | Venv): Venv used for building distribution. Defaults to Venv("venv").
    """
    print_progress("Deploying to PyPi", verbosity > 0)
    verbose = verbosity == 2

    usr = os.environ.get("TWINE_USERNAME")
    password = os.environ.get("TWINE_PASSWORD")

    if not usr or not password:
        raise KeyError("Setup env vars TWINE_USERNAME and TWINE_PASSWORD to use deploy.")

    check_script_is_available("twine", "twine")

    setup_path = (
        validate_path(setup_path, "Deploy with `deploy_to_pypi` failed", "setup.py")
        if setup_path
        else PROJECT_PATHS.root / "setup.py"
    )

    setup_dir_path = setup_path.parent

    dist_path = setup_dir_path / "dist"
    build_path = setup_dir_path / "build"

    delete_files(dist_path)
    delete_files(build_path)

    activate_command = "" if not venv else f"{venv.activate_command} && "

    if pep517:
        build_command = f"{activate_command} {PYTHON} -m build --wheel --sdist"
    else:
        build_command = f"{activate_command} {PYTHON} setup.py sdist bdist_wheel"

    terminal_do_command(
        build_command,
        cwd=setup_dir_path.as_posix(),
        verbose=verbose,
        error_header=(
            "Build python distribution for PyPi deployment failed. Change of 'pep517' parameter may help."
        ),
    )

    command = "twine upload dist/*"

    terminal_do_command(
        command,
        cwd=setup_dir_path.as_posix(),
        verbose=verbose,
        error_header="Deploying to PyPi failed.",
    )

    if clean:
        delete_files(dist_path)
        delete_files(build_path)
