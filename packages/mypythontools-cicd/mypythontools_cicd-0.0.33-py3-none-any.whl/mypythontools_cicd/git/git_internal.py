"""Module with functions for 'git' subpackage."""

from __future__ import annotations
from typing import Sequence

from typing_extensions import Literal

from mypythontools.misc import print_progress
from mypythontools.types import validate_sequence
from mypythontools.paths import PathLike
from mypythontools.system import (
    get_console_str_with_quotes,
    terminal_do_command,
    SHELL_AND,
)

# Lazy loaded
# from git import Repo

from ..project_paths import PROJECT_PATHS
from ..packages import get_version


class TagAlreadyExists(Exception):
    pass


def commit_all(commit_message: str, verbosity: Literal[0, 1, 2] = 1):
    """Stage all changes and create a commit.

    Args:
        commit_message (str): Commit message.
        verbosity (Literal[0, 1, 2], optional): If 0, prints nothing, if 1, then one line description of what
            happened is printed. If 3, all the results from terminal are printed. Defaults to 1.
    """
    print_progress("Creating commit of all changes", verbosity > 0)
    git_command = f"git add . {SHELL_AND} git commit -m {get_console_str_with_quotes(commit_message)}"
    terminal_do_command(git_command, cwd=PROJECT_PATHS.root.as_posix(), verbose=verbosity == 2)


def push(
    tag: str | None = "__version__",
    tag_message: str = "New version",
    verbosity: Literal[0, 1, 2] = 1,
) -> None:
    """Add tag and push.

    If tag is `__version__`, then tag is inferred from `__init__.py`.

    Args:
        tag (str | None, optional): Define tag used in push. If tag is '__version__', than is automatically generated
            from __init__ version. E.g from '1.0.2' to 'v1.0.2'.  Defaults to '__version__'.
        tag_message (str, optional): Message in annotated tag. Defaults to 'New version'.
        verbosity (Literal[0, 1, 2], optional): If 0, prints nothing, if 1, then one line description of what
            happened is printed. If 3, all the results from terminal are printed. Defaults to 1.
    """
    import git.repo
    import git.exc
    from git.exc import GitCommandError

    print_progress("Pushing to github", verbosity > 0)

    git_command = "git push"

    if tag == "__version__":
        tag = f"v{get_version()}"

    if tag:
        check_tag(tag)
        if not tag_message:
            tag_message = "New version"
        try:
            git.repo.Repo(PROJECT_PATHS.root.as_posix()).create_tag(tag, message=tag_message)
        except GitCommandError as err:
            raise RuntimeError("Tag creation failed.") from err

        git_command += " --follow-tags"

    try:
        terminal_do_command(git_command, cwd=PROJECT_PATHS.root.as_posix(), verbose=verbosity == 2)

    except RuntimeError as err:
        git.repo.Repo(PROJECT_PATHS.root.as_posix()).delete_tag(tag)  # type: ignore
        raise RuntimeError("Push to git failed. Version restored and created git tag deleted.") from err


def check_tag(tag: str):
    """Check if tag is not already in repo, so it can be created afterwards.

    Args:
        tag (str): Tag name. E.g. 'v.0.0.3'

    Raises:
        TagAlreadyExists: If tag already exists in repo.
    """
    import git.repo

    repo = git.repo.Repo(PROJECT_PATHS.root.as_posix())

    if tag in [i.name for i in repo.tags]:
        raise TagAlreadyExists(f"Tag '{tag}' already exists.")


def check_branch(allowed_branches: Sequence[str]):
    """Check if project is opened with one of particular branches anr raise error if not.

    Args:
        allowed_branches (Sequence[str]): Sequence of allowed branches.

    Raises:
        RuntimeError: If project is on branch that is not in allowed branches.
    """
    import git.repo
    from git.exc import InvalidGitRepositoryError

    validate_sequence(allowed_branches, "allowed_branches")

    try:
        branch = git.repo.Repo(PROJECT_PATHS.root.as_posix()).active_branch.name
    except InvalidGitRepositoryError:
        raise RuntimeError(
            "Loading of git project failed. Verify whether running pipeline from correct path. If "
            "checks branch with `allowed_branches', there has to be `.git` folder available."
        ) from None

    if branch not in allowed_branches:
        raise RuntimeError(
            "Pipeline started on branch that is not allowed."
            "If you want to use it anyway, add it to allowed_branches parameter and "
            "turn off changing version and creating tag."
        )


def clone_locally(from_path: PathLike, to_path: PathLike):
    """Copy file from one place to another. Main benefit is, that `.gitignore` is used, so things like venv is
    is not copied.

    Args:
        from_path (PathLike): Source
        to_path (PathLike): Destination
    """
    terminal_do_command(f"git clone {from_path} {to_path}")
