"""
Setup file for utils.
Use setup.cfg to configure your project.

This file was generated with PyScaffold 4.6.
PyScaffold helps you to put up the scaffold of your new Python project.
Learn more under: https://pyscaffold.org/
"""

from setuptools import setup
import sys


def _platform_scripts():
    scripts = [
        "bin/otoolbox-commit",
        "bin/otoolbox-common",
        "bin/otoolbox-doctor",
        "bin/otoolbox-init-tests",
        "bin/otoolbox-pre-commit",
        "bin/otoolbox-pull",
        "bin/otoolbox-push",
        "bin/otoolbox-push-shielded",
        "bin/otoolbox-repo-add-all",
        "bin/otoolbox-repo-init",
        "bin/otoolbox-sync-shielded",
        "bin/otoolbox-tests-by-repo",
    ]
    if sys.platform.startswith("win"):
        scripts = [item + ".bat" for item in scripts]
    return scripts

if __name__ == "__main__":
    try:
        setup(
            use_scm_version={"version_scheme": "no-guess-dev"},
            scripts=_platform_scripts(),
        )
    except:  # noqa
        # pylint: disable=W8116
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
