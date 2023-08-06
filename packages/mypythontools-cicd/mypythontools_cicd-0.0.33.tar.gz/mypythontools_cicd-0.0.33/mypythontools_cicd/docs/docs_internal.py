"""Module with functions for 'doc' subpackage."""

from __future__ import annotations
from typing import Sequence
import ast

from typing_extensions import Literal

from mypythontools.paths import validate_path, PathLike
from mypythontools.types import validate_sequence

from mypythontools.misc import delete_files, print_progress
from mypythontools.system import (
    check_script_is_available,
    get_console_str_with_quotes,
    terminal_do_command,
    SHELL_AND,
)

from mypythontools_cicd.project_paths import PROJECT_PATHS


def docs_regenerate(
    docs_path: None | PathLike = None,
    build_locally: bool = True,
    git_add: bool = True,
    keep: Sequence[PathLike] = (),
    ignore: Sequence[PathLike] = ("modules.rst", "**/*internal.py"),
    verbosity: Literal[0, 1, 2] = 1,
) -> None:
    """Generate all rst files necessary for sphinx documentation generation with sphinx-apidoc.

    It automatically delete rst files from removed or renamed files.

    Note:
        All the files except ['conf.py', 'index.rst', '_static', '_templates', 'content/**'], and files in
        'keep' parameter will be deleted!!! Because if some files would be deleted or
        renamed, rst would stay and html was generated. If you have some extra files or folders in docs
        source, add it to content folder or to 'keep' parameter.

    Function suppose sphinx build and source in separate folders...

    Args:
        docs_path (None | PathLike, optional): Where source folder is. If None, will be inferred.
            Defaults to None.
        build_locally (bool, optional): If true, build folder with html files locally.
            Defaults to True.
        git_add (bool, optional): Whether to add generated files to stage. False mostly for
            testing reasons. Defaults to True.
        keep (Sequence[PathLike], optional): List of files and folder names that will not be
            deleted. Deletion is because if some file would be renamed or deleted, rst docs would still stay.
            Glob-style patterns can be used, but it's not recursive, but only first level of source folder is
            used. Defaults to None.
        ignore (Sequence[PathLike], optional): Whether ignore some files from generated rst files. For example
            It can be python modules that will be ignored or it can be rst files created, that will be
            deleted. to have no errors in sphinx build for unused modules, or for internal modules. Glob-style
            patterns can be used. Defaults to ("modules.rst", "**/*_.py")
        verbosity (Literal[0, 1, 2], optional): If 0, prints nothing, if 1, then one line description of what
            happened is printed. If 3, all the results from terminal are printed. Defaults to 1.

    Note:
        Function suppose structure of docs like::

            -- docs
            -- -- source
            -- -- -- conf.py
            -- -- make.bat
    """
    print_progress("Sphinx docs generation", verbosity > 0)
    check_script_is_available("sphinx-apidoc", "sphinx")

    validate_sequence(keep, keep)
    validate_sequence(ignore, ignore)

    verbose = verbosity == 2

    docs_path = (
        validate_path(docs_path, "Docs generation with 'docs_regenerate' failed", "Docs path")
        if docs_path
        else PROJECT_PATHS.docs
    )

    docs_source_path = docs_path / "source"

    source_path = PROJECT_PATHS.app
    source_console_path = get_console_str_with_quotes(source_path)

    keep = [
        *keep,
        "conf.py",
        "index.rst",
        "_static",
        "_templates",
        "content",
    ]
    ignore_list = [*ignore]

    ignored = " "

    for i in ignore_list:
        for file in source_path.rglob(str(i)):
            ignored = ignored + f"{get_console_str_with_quotes(file)} "

    for file in docs_source_path.iterdir():
        if not any((file.match(str(pattern)) for pattern in keep)):
            delete_files(file)

    apidoc_command = (
        f"sphinx-apidoc --module-first --force --separate -o source {source_console_path} {ignored}"
    )

    terminal_do_command(
        apidoc_command, cwd=docs_path, verbose=verbose, error_header="Docs sphinx-apidoc failed."
    )

    if ignore_list:
        for file in docs_source_path.iterdir():
            if any((file.match(str(pattern)) for pattern in ignore_list)):
                delete_files(file)

    if build_locally:
        terminal_do_command(
            f"make clean {SHELL_AND} make html",
            cwd=docs_path,
            verbose=verbose,
            error_header="Sphinx build failed.",
            shell=True,
        )

    if git_add:
        terminal_do_command("git add docs", cwd=PROJECT_PATHS.root.as_posix(), verbose=verbose)


def generate_readme_from_init(git_add: bool = True) -> None:
    """Generate README file from `__init__.py` docstrings.

    Because i had very similar things in main `__init__.py` and in readme. It was to maintain news
    in code. For better simplicity i prefer write docs once and then generate. One code, two use cases.

    Why `__init__`? - Because in IDE on mouseover developers can see help.
    Why README.md? - Good for github.com

    Args:
        git_add (bool, optional): Whether to add generated files to stage. False mostly
            for testing reasons. Defaults to True.
    """
    with open(PROJECT_PATHS.init.as_posix()) as init_file:
        file_contents = init_file.read()
    module = ast.parse(file_contents)
    docstrings = ast.get_docstring(module)

    if docstrings is None:
        docstrings = ""

    with open(PROJECT_PATHS.readme.as_posix(), "w") as file:
        file.write(docstrings)

    if git_add:
        terminal_do_command(f"git add {PROJECT_PATHS.readme}", cwd=PROJECT_PATHS.root.as_posix())
