"""Module with functions for 'misc' subpackage."""

from __future__ import annotations
from typing import Sequence


from mypythontools.paths import validate_path, PathLike
from mypythontools.types import validate_sequence

from mypythontools.misc import print_progress
from mypythontools.system import (
    check_script_is_available,
    terminal_do_command,
)

from mypythontools_cicd.project_paths import PROJECT_PATHS


def reformat_with_black(
    root_path: None | PathLike = None, extra_args: Sequence[str] = ("--quiet",), verbose: bool = False
) -> None:
    """Reformat code with black.

    Args:
        root_path (None | PathLike, optional): Root path of project. If None, will be inferred.
            Defaults to None.
        extra_args (Sequence[str], optional): Some extra args for black. Defaults to ("--quiet,").
        verbose (bool, optional): If True, result of terminal command will be printed to console.
            Defaults to False.

    Example:
        >>> reformat_with_black()
    """
    print_progress("Reformatting", verbose)
    check_script_is_available("black", "black")
    validate_sequence(extra_args, "extra_args")

    root_path = validate_path(root_path, "Reformating failed") if root_path else PROJECT_PATHS.root

    terminal_do_command(
        f"black . {' '.join(extra_args)}", cwd=root_path, verbose=verbose, error_header="Formatting failed"
    )
