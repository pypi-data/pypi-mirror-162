"""Module with functions for 'cicd' subpackage."""

from __future__ import annotations
from typing import Sequence
import os
import sys

from typing_extensions import Literal

from mypythontools.config import Config, MyProperty
from mypythontools.misc import GLOBAL_VARS, EMOJIS, print_progress
from mypythontools.paths import PathLike

from .. import git
from .. import venvs
from .. import tests
from ..deploy import deploy_to_pypi
from ..docs import docs_regenerate
from ..misc import reformat_with_black
from ..project_paths import PROJECT_PATHS
from ..venvs import Venv

from .. import packages


class PipelineConfig(Config):
    """Allow to setup CICD pipeline."""

    def __init__(self) -> None:
        """Create subconfigs."""
        self.test: tests.TestConfig = tests.default_test_config

    @MyProperty
    def do_only(
        self,
    ) -> Literal[
        None,
        "prepare_venvs",
        "reformat",
        "test",
        "docs",
        "sync_requirements",
        "git_commit_all",
        "git_push",
        "deploy",
    ]:
        """Run just single function from pipeline, ignore the others.

        Type:
            Literal[
                None, "prepare_venvs", "reformat", "test", "docs", "sync_requirements", "git_commit_all",
                "git_push", "deploy"
            ]

        Default:
            None

        Reason for why to call it form here and not directly is to be able to use sys args or single command
        line entrypoint.
        """
        return None

    @MyProperty
    def venv(self) -> None | Venv:
        """Used venv. Now used only in "deploy" function for build.

        Type:
            None | Venv

        Default:
            Venv("venv")
        """
        return Venv("venv")

    @MyProperty
    def prepare_venvs(self) -> None | list[str]:
        """Create venvs with defined versions.

        Type:
            None | list[str]

        Default:
            None
        """
        return None

    @MyProperty
    def prepare_venvs_path(self) -> PathLike:
        """Prepare venvs in defined path.

        Type:
            str

        Default:
            "venv"
        """
        return "venv"

    @MyProperty
    def reformat(self) -> bool:
        """Reformat all python files with black. Setup parameters in pyproject.toml.

        Type:
            bool

        Default:
            True
        """
        return True

    @MyProperty
    def set_version(self) -> None | str:
        """Overwrite __version__ in __init__.py.

        Type:
            str

        Default:
            'increment'.

        Version has to be in format like '1.0.3' three digits and two dots. If 'None', nothing will happen. If
        'increment', than it will be updated by 0.0.1..
        """
        return "increment"

    @MyProperty
    def docs(self) -> bool:
        """Define whether generate sphinx apidoc and generate rst files for documentation.

        Type:
            bool

        Default:
            True

        Some files in docs source can be deleted - check `docs` docstrings for details.
        """
        return True

    @MyProperty
    def sync_requirements(self) -> None | Literal["infer"] | PathLike | Sequence[PathLike]:
        """Check requirements.txt and update all the libraries.

        Type:
            None | Literal["infer"] | PathLike | Sequence[PathLike]

        Default:
            None

        You can use path to requirements, list of paths. If "infer", auto detected (all requirements), not
        recursively, only on defined path.
        """
        return None

    @MyProperty
    def sync_requirements_path(self) -> PathLike:
        """Define the root if using just names or relative path, and not found.

        Type:
            PathLike

        Default:
            PROJECT_PATHS.root

        It's also necessary when using another referenced files. If inferring files, it's used to search.
        Defaults to PROJECT_PATHS.root.
        """
        return PROJECT_PATHS.root

    @MyProperty
    def git_commit_all(self) -> None | str:
        """Whether take all the changes in repository and create a commit with these changes.

        Note:
            !!! Be cautious here if using with `git_push` !!!

        Type:
            None | str

        Default:
            'New commit'
        """
        return "New commit"

    @MyProperty
    def git_push(self) -> bool:
        """Whether push to repository.

        Type:
            bool

        Default:
            True
        """
        return True

    @MyProperty
    def tag(self) -> str | None:
        """Tag. E.g 'v1.1.2'. If '__version__', get the version.

        Type:
            str | None

        Default:
            '__version__'
        """
        return "__version__"

    @MyProperty
    def tag_message(self) -> str:
        """Tag message.

        Type:
            str

        Default:
            'New version'
        """
        return "New version"

    @MyProperty
    def deploy(self) -> bool:
        """Deploy to PYPI.

        `TWINE_USERNAME` and `TWINE_PASSWORD` are used for authorization.

        Type:
            bool

        Default:
            False
        """
        return False

    @MyProperty
    def allowed_branches(self) -> None | Sequence[str]:
        """Pipeline runs only on defined branches.

        Type:
            None | Sequence[str]

        Default:
            ["master", "main"]
        """
        return ["master", "main"]

    @MyProperty
    def verbosity(self) -> Literal[0, 1, 2]:
        """Pipeline runs only on defined branches.

        Type:
            Literal[0, 1, 2]

        Default:
            1
        """
        return 1


default_pipeline_config = PipelineConfig()


def cicd_pipeline(
    config: PipelineConfig = default_pipeline_config,
) -> None:
    """Run pipeline for pushing and deploying an app or a package.

    Can run tests, generate rst files for sphinx docs, push to github and deploy to pypi. All params can be
    configured not only with function params, but also from command line with params and therefore callable
    from terminal and optimal to run from IDE (for example with creating simple VS Code task).

    Some function suppose some project structure (where are the docs, where is `__init__.py` etc.).
    If you are issuing some error, try functions directly, find necessary paths in parameters
    and set paths that are necessary in paths module.

    Note:
        Beware, that by default, it creates a commit and add all the changes, not only the staged ones.

    When using sys args for boolean values, always define True or False.

    There is command line entrypoint called `mypythontools_cicd`. After mypythontools is installed, you can
    use it in terminal like::

        mypythontools_cicd --do_only reformat

    Args:
        config (PipelineConfig, optional): PipelineConfig object with CICD pipeline configuration. Just import
            default_pipeline_config and use intellisense and help tooltip with description. It is also
            possible to configure all the params with CLI args from terminal.
            Defaults to `default_pipeline_config`.

    Example:
        Recommended use is from IDE (for example with Tasks in VS Code). Check utils docs for how to use it.
        You can also use it from python... ::

            from mypythontools_cicd.cicd import cicd_pipeline, default_pipeline_config

            default_pipeline_config.deploy = True
            # default_pipeline_config.do_only = ""


            if __name__ == "__main__":
                # All the parameters can be overwritten via CLI args
                cicd_pipeline(config=default_pipeline_config)

        It's also possible to use CLI and configure it via args. This example just push repo to PyPi. ::

            python path-to-project/utils/push_script.py --do_only deploy

    Another way how to run it is to use IDE. For example in VS Code you can use Tasks. Check `cicd`
    docs for examples.
    """
    if not GLOBAL_VARS.is_tested:
        config.do.with_argparse()

    do_only = config.do_only

    # If do_only change subconfig value and not config, change it
    if do_only == "test":
        do_only = "run_tests"

    # For do_only True value must be set for boolean even if not configured

    if do_only:
        # There are some boolean variables where is enough to tell do_only name
        do_only_booleans = ["reformat", "run_tests", "git_push", "deploy"]
        do_only_value = config[do_only]
        if do_only in do_only_booleans:
            do_only_value = True
        else:
            # There are some variables, where not only variable is chosen, but also a value must be set
            if not do_only_value:
                raise RuntimeError(
                    "If you are doing just one step from `cicd_pipeline` with 'do_only', for non boolean you "
                    "must have also configured a value in the config."
                )

        config.do.update(
            {
                "prepare_venvs": None,
                "reformat": False,
                "run_tests": False,
                "docs": False,
                "sync_requirements": None,
                "git_commit_all": None,
                "git_push": False,
                "deploy": False,
                "set_version": None,
                "tag": None,
            }
        )
        config.do.update({do_only: do_only_value})

    verbosity = config.verbosity
    progress_is_printed = verbosity > 0

    if config.allowed_branches:
        git.check_branch(config.allowed_branches)

    # Do some checks before run pipeline so not need to rollback eventually
    if config.deploy:
        usr = os.environ.get("TWINE_USERNAME")
        pas = os.environ.get("TWINE_PASSWORD")

        if not usr or not pas:
            raise KeyError("Setup env vars TWINE_USERNAME and TWINE_PASSWORD to use deploy.")

    if config.tag:
        if config.tag == "__version__":
            tag = config.set_version
            if tag == "increment":
                tag = f"v{packages.increment_version(packages.get_version())}"
            if not tag:
                tag = packages.get_version()
        else:
            tag = config.tag
        git.check_tag(tag)

    if config.prepare_venvs:
        venvs.prepare_venvs(
            path=config.prepare_venvs_path, versions=config.prepare_venvs, verbosity=verbosity
        )

    if config.sync_requirements:
        if not venvs.is_venv:
            raise RuntimeError("'sync_requirements' available only if using virtualenv.")
        my_venv = venvs.Venv(sys.prefix)
        my_venv.sync_requirements(
            config.sync_requirements, verbosity=verbosity, path=config.sync_requirements_path
        )

    if config.test:
        tests.run_tests(config.test)

    if config.reformat:
        reformat_with_black()

    if config.set_version:
        print_progress("Setting version", progress_is_printed)
        original_version = packages.get_version()
        packages.set_version(config.set_version)

    if config.docs:
        docs_regenerate(verbosity=verbosity)

    if config.git_commit_all:
        git.commit_all(config.git_commit_all, verbosity=verbosity)

    try:
        if config.git_push:
            git.push(
                tag=config.tag,
                tag_message=config.tag_message,
                verbosity=verbosity,
            )

    except Exception as err:  # pylint: disable=broad-except
        if config.set_version:
            packages.set_version(original_version)  # type: ignore

        raise RuntimeError(
            f"{3 * EMOJIS.DISAPPOINTMENT} Utils pipeline failed {3 * EMOJIS.DISAPPOINTMENT} \n\n"
            f"{'Original version restored. ' if config.set_version else ''}Nothing was pushed to repo, "
            "you can restart pipeline. "
            f"{'All changes already committed.' if config.git_commit_all else ''}"
        ) from err

    try:
        if config.deploy:
            deploy_to_pypi(verbosity=verbosity, venv=config.venv)

    except Exception as err:  # pylint: disable=broad-except
        raise RuntimeError(
            f"{3 * EMOJIS.DISAPPOINTMENT} Deploy failed {3 * EMOJIS.DISAPPOINTMENT} \n\n"
            "Already pushed to repository. Deploy manually."
            f"{'All changes already committed.' if config.git_commit_all else ''}"
            f"{'Version already changed.' if config.set_version else ''}"
        ) from err

    print_progress(f"{3 * EMOJIS.PARTY} Finished {3 * EMOJIS.PARTY}", True)
