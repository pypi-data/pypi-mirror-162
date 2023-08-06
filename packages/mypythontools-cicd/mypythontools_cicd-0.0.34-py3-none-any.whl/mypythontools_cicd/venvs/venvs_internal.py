"""Module with functions for 'venvs' subpackage."""

from __future__ import annotations
from typing import Sequence
import platform
import shutil
from pathlib import Path
import sys

from typing_extensions import Literal

from mypythontools.paths import PathLike, is_path_free, WslPath
from mypythontools.misc import print_progress
from mypythontools.system import (
    check_script_is_available,
    get_console_str_with_quotes,
    terminal_do_command,
    SHELL_AND,
    is_wsl,
)

from ..project_paths import PROJECT_PATHS
from ..packages import get_requirements
from mypythontools_cicd.project_paths import PROJECT_PATHS


class VenvNotFound(RuntimeError):
    """If some method called on non installed venv."""

    pass


class Venv:
    """You can create new venv or sync it's dependencies.

    Attributes:
        venv_path(Path): Path of venv. E.g. `venv`
        with_wsl(bool, optional): If working with linux venv from linux.

    Example:
        >>> from pathlib import Path
        >>> from mypythontools.system import is_wsl
        ...
        >>> path = "venv/doctest/3.10" if platform.system() == "Windows" and not is_wsl() else "venv/doctest/wsl-3.10"
        >>> venv = Venv(path)
        >>> venv.create()  # If already exists, it's skipped
        >>> venv.install_library("colorama==0.3.9")
        >>> "colorama==0.3.9" in venv.list_packages()
        True
        >>> venv.sync_requirements(verbosity=0, path=PROJECT_PATHS.root)  # There ia a 0.4.4 in requirements.txt
        >>> "colorama==0.4.4" in venv.list_packages()
        True
        >>> venv.remove()
        >>> Path(path).exists()
        False
    """

    def __init__(self, venv_path: PathLike, with_wsl: bool = False) -> None:
        """Init the venv class. To create or update it, you can call extra functions.

        Args:
            venv_path(PathLike): Path of venv. E.g. `venv`
            with_wsl(bool, optional): If working with linux venv from linux.

        Raises:
            FileNotFoundError: No folder found on defined path.
        """
        venv_path = Path(venv_path).resolve()
        self.real_path = venv_path

        self.venv_path_console_str = get_console_str_with_quotes(venv_path)
        self.with_wsl = with_wsl

        wsl = is_wsl() or with_wsl

        self.executable_str: str
        """Path to the executables. Can be directly used in terminal. Some libraries cannot use
        ``python -m package`` syntax and therefore it can be called from scripts folder."""

        if platform.system() == "Windows" and not wsl:
            activate_path = venv_path / "Scripts" / "activate.bat"
            self.installed = activate_path.exists()
            self.executable = venv_path / "Scripts" / "python.exe"
            self.create_command = f"python -m venv {self.venv_path_console_str}"
            self.scripts_path = venv_path / "Scripts"
            self.activate_command = get_console_str_with_quotes(activate_path.as_posix())
            self.executable_str = get_console_str_with_quotes((self.executable).as_posix())

        elif platform.system() == "Windows" and with_wsl:
            venv_path = WslPath(venv_path)
            activate_path = venv_path / "bin" / "activate"
            self.installed = (self.real_path / "bin" / "activate").exists()
            self.executable = venv_path / "bin" / "python"
            self.create_command = f"python3 -m venv {self.venv_path_console_str}"
            self.scripts_path = venv_path / "bin"
            self.activate_command = f". {get_console_str_with_quotes(activate_path.wsl_path)}"
            self.executable_str = get_console_str_with_quotes((venv_path / "bin" / "python").wsl_path)

        else:
            activate_path = venv_path / "bin" / "activate"
            self.installed = activate_path.exists()
            self.executable = venv_path / "bin" / "python"
            self.create_command = f"python3 -m venv {self.venv_path_console_str}"
            self.scripts_path = venv_path / "bin"
            self.activate_command = f". {get_console_str_with_quotes(activate_path)}"
            self.executable_str = get_console_str_with_quotes((venv_path / "bin" / "python"))

        self.venv_path = venv_path
        """Path to venv prefix, e.g. .../venv"""

        self.subprocess_prefix = f"{self.activate_command} {SHELL_AND} {self.executable_str} -m "
        """Run as module, so library can be directly call afterwards. Can be directly used in terminal. It can
        look like this for example::
        
            .../Scripts/activate.bat && .../venv/Scripts/python.exe -m
        """

    def create(self, verbose: bool = False) -> None:
        """Create virtual environment. If it already exists, it will be skipped and nothing happens.

        Args:
            verbose (bool, optional): If True, result of terminal command will be printed to console.
                Defaults to False.
        """
        if not self.installed:
            terminal_do_command(
                self.create_command,
                cwd=PROJECT_PATHS.root.as_posix(),
                shell=True,
                verbose=verbose,
                error_header="Venv creation failed",
                with_wsl=self.with_wsl,
            )
        self.installed = True

    def sync_requirements(
        self,
        requirements_files: None | Literal["infer"] | PathLike | Sequence[PathLike] = "infer",
        requirements: None | list[str] = None,
        verbosity: Literal[0, 1, 2] = 1,
        path: PathLike = PROJECT_PATHS.root,
    ) -> None:
        """Sync libraries based on requirements. Install missing, remove unnecessary.

        Args:
            requirements_files (Literal["infer"] | PathLike | Sequence[PathLike], optional): Define what libraries
                will be installed. If "infer", autodetected. Can also be a list of more files e.g
                `["requirements.txt", "requirements_dev.txt"]`. Defaults to "infer".
            requirements (list[str], optional): List of requirements. Defaults to None.
            verbosity (Literal[0, 1, 2], optional): If 0, prints nothing, if 1, then one line description of
                what happened is printed. If 3, all the results from terminal are printed. Defaults to 1.
            path (PathLike, optional): If using just names or relative path, and not found, define the root.
                It's also necessary when using another referenced files. If inferring files, it's used to
                search. Defaults to PROJECT_PATHS.root.
        """
        print_progress("Syncing requirements", verbosity > 0)

        self._raise_if_not_installed()

        self.install_library("pip-tools")

        requirements_all = []

        if requirements_files:
            try:
                requirements_all.extend(get_requirements(requirements_files, path))
            except RuntimeError:
                pass

        if requirements:
            requirements_all.extend(requirements)

        if not requirements_all:
            raise RuntimeError("No requirements found.")

        requirements_all_path = self.venv_path / "requirements_all.in"
        if isinstance(self.venv_path, WslPath):
            requirements_all_console_path_str = get_console_str_with_quotes(requirements_all_path.wsl_path)  # type: ignore
            freezed_requirements_console_path_str = get_console_str_with_quotes(
                (self.venv_path / "requirements.txt").wsl_path
            )
        else:
            freezed_requirements_console_path_str = get_console_str_with_quotes(
                (self.venv_path / "requirements.txt")
            )
            requirements_all_console_path_str = get_console_str_with_quotes(requirements_all_path)

        with open(requirements_all_path, "w") as requirement_libraries:
            requirement_libraries.write("\n".join(requirements_all))

        pip_compile_command = (
            f"pip-compile {requirements_all_console_path_str} --output-file "
            f"{freezed_requirements_console_path_str} --quiet"
        )

        pip_sync_command = f"pip-sync {freezed_requirements_console_path_str} --quiet"
        sync_commands = {
            pip_compile_command: "Creating joined requirements.txt file failed.",
            pip_sync_command: "Requirements syncing failed.",
        }

        for i, j in sync_commands.items():
            terminal_do_command(
                f"{self.activate_command} {SHELL_AND} {i}",
                verbose=verbosity == 2,
                error_header=j,
                with_wsl=self.with_wsl,
            )

    def list_packages(self) -> str:
        """Get list of installed libraries in the venv.

        The reason why it's meta coded via string parsing and not parsed directly is that it needs to be
        available from other venv as well.
        """
        self._raise_if_not_installed()

        result = terminal_do_command(
            f"{self.activate_command} {SHELL_AND} {self.executable_str} -m pip freeze",
            with_wsl=self.with_wsl,
            verbose=False,
        )

        return result

    def install_library(
        self, name: str, verbose: bool = False, upgrade: bool = False, path: None | PathLike = None
    ) -> None:
        """Install package to venv with pip install.

        You can use extras with square brackets.

        Args:
            name (str): Name of installed library.
            verbose (bool, optional): If True, result of terminal command will be printed to console.
                Defaults to False.
            upgrade (bool, optional): Update flag. If True, then latest is installed. If False, and already
                exists, it's skipped. Defaults to False
            path (None | Pathlike, optional): If installing from local path, this is path from where you can use
                relative paths. Defaults to None.
        """
        self._raise_if_not_installed()

        command = f"{self.activate_command} {SHELL_AND} {self.executable_str} -m pip install {name} {'--upgrade' if upgrade else ''}"
        terminal_do_command(
            command,
            shell=True,
            verbose=verbose,
            error_header="Library installation failed.",
            with_wsl=self.with_wsl,
            cwd=path,
        )

    def uninstall_library(self, name: str, verbose: bool = False) -> None:
        """Uninstall package to venv with pip install.

        Args:
            name (str): Name of library to uninstall.
            verbose (bool, optional): If True, result of terminal command will be printed to console.
                Defaults to False.
        """
        self._raise_if_not_installed()

        command = f"{self.activate_command} {SHELL_AND} {self.executable_str} -m pip uninstall {name}"

        terminal_do_command(
            command,
            shell=True,
            verbose=verbose,
            error_header="Library removal failed",
            with_wsl=self.with_wsl,
            input="y",
        )

    def remove(self) -> None:
        """Remove the folder with venv."""
        shutil.rmtree(self.venv_path.as_posix())

    def get_script_path(self, name: str) -> str:
        """Get script path such as pip for example."""
        if platform.system() == "Windows" and not is_wsl():
            return get_console_str_with_quotes(self.scripts_path / f"{name}.exe")
        else:
            return get_console_str_with_quotes(self.scripts_path / name)

    def _raise_if_not_installed(self):
        if not self.installed:

            raise VenvNotFound("Installed venv not found, first create it with 'create' or create multiple.")


def is_venv() -> bool:
    """True if run in venv, False if run in main interpreter directly."""
    return sys.base_prefix.startswith(sys.prefix)


def prepare_venvs(
    path: None | PathLike = "venv",
    versions: Sequence[str] = ["3.7", "3.10", "wsl-3.7", "wsl-3.10"],
    verbosity: Literal[0, 1, 2] = 1,
):
    """This will install virtual environments with defined versions.

    Installation will be skipped if there is already existing folder with content. It is possible tu use wsl
    on windows. You have to install python launcher when using linux or wsl. More about python-launcher
    https://github.com/brettcannon/python-launcher

    Args:
        path (None | PathLike): Where venvs will be stored. If None, cwd() will be used. Defaults to "venv".
        versions (Sequence[str], optional): List of used versions. If you want to use wsl, add `wsl-` prefix
            like for example `wsl-3.7`. Defaults to ["3.7", "3.10", "wsl-3.7", "wsl-3.10"].
        verbosity (Literal[0, 1, 2], optional): If 0, prints nothing, if 1, then one line description of what
            happened is printed. If 3, all the results from terminal are printed. Defaults to 1.
    """
    print_progress("Preparing venvs", verbosity > 0)

    if path is None:
        path = Path.cwd()

    if not isinstance(versions, list):
        raise TypeError("'versions' param has to be list.")

    for version in versions:
        venv_path = Path(f"{path}/{version}")

        if version.startswith("wsl-"):
            wsl = True
            version = version[4:]  # remove "wsl-"
        else:
            wsl = False

        if not is_path_free(venv_path):
            if Venv(venv_path, with_wsl=wsl).installed:
                continue
            else:
                raise RuntimeError(
                    f"There is not empty folder on defined path '{venv_path.as_posix()}' and existing "
                    "virtualenv for current OS not detected there. Clean it first or check the settings "
                    "whether it should be an wsl venv."
                )

        if wsl:
            check_script_is_available(
                "wsl py",
                message=(
                    "Verify whether python launcher is installed. If not, install it from "
                    "https://github.com/brettcannon/python-launcher . \n If it's installed in "
                    "'/home/linuxbrew/.linuxbrew/bin/py' it will be not visible from wsl. "
                    "You can use /usr/local/..."
                ),
            )
        create_command = f"py -{version} -m venv {venv_path.as_posix()}"

        terminal_do_command(
            create_command,
            verbose=verbosity == 2,
            error_header=(
                f"Creating virtual environment for{' wsl ' if wsl else ' '}version {version} failed. "
                "If fails with wsl, try to install 'python3.x-venv' on wsl."
            ),
            with_wsl=wsl,
        )
