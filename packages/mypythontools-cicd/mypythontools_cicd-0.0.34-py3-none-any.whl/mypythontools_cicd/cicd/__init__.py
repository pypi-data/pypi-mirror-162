"""Run cicd functions from other modules in particular order and provide configuration.

This module can be used for example in running deploy pipelines or githooks
(some code automatically executed before commit). This module can run the tests,
edit library version, generate rst files for docs, push to git or deploy app to pypi.

All of that can be done with one function call - with `cicd_pipeline` function that
run other functions, or you can use functions separately. 

Attributes:
    default_pipeline_config (PipelineConfig): Default values for pipeline. If something changes here, it will
        change in all the repos. You can edit any values in pipeline. Intellisense and help tooltip should
        help.

Examples:
=========

    **From python script**

    Create folder utils, create `push_script.py` inside, add::

        from mypythontools_cicd.cicd import cicd_pipeline, default_pipeline_config

        if __name__ == "__main__":
            cicd_pipeline(config=default_pipeline_config)

    **With terminal command**

    Run code like this in terminal::

        mypythontools_cicd --test True --deploy True

    If you need to ensure that it will run from particular venv, prepend ``path_to_python/python.exe -m``

    **VS Code Task example**

    You can push changes with single click with all the hooks displaying results in
    your terminal. All params changing every push (like git message or tag) can
    be configured on the beginning and therefore you don't need to wait for test finish.
    Default values can be also used, so in small starting projects, push is actually very fast.

    Here you can find all the tasks with with interactive version and git message config

    https://github.com/Malachov/Software-settings/blob/master/VS-Code/tasks.json

    Add the tasks to global tasks.json. Here is example of one such a task ::

        {
          "version": "2.0.0",
          "tasks": [
            {
                "label": "Push to PyPi",
                "command": "${command:python.interpreterPath}",
                "args": ["-m", "mypythontools_cicd", "--do_only", "reformat"]
            },
          ]
        }

    **Git hooks example**

    Create folder git_hooks with git hook file - for pre commit name must be `pre-commit`
    (with no extension). Hooks in git folder are gitignored by default (and hooks is not visible
    on first sight).

    Then add hook to git settings - run in terminal (last arg is path (created folder))::

        $ git config core.hooksPath git_hooks

    In created folder on first two lines copy this::

        #!/usr/bin/env python
        # -*- coding: UTF-8 -*-

    Then just import any function from here and call with desired params. E.g.
"""
from mypythontools_cicd.cicd.cicd_internal import (
    default_pipeline_config,
    PipelineConfig,
    cicd_pipeline,
)

__all__ = ["default_pipeline_config", "PipelineConfig", "cicd_pipeline"]
