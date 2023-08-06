"""Run pipeline if using ``python -m mypythontools_cicd``.

This can be better than console_script when want to ensure that libraries from current venv will be used.
"""

from mypythontools_cicd.cicd import cicd_pipeline

if __name__ == "__main__":
    # Function is configured via sys args
    cicd_pipeline()
