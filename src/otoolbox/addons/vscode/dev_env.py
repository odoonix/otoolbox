import os
import sys
import subprocess
import logging

from otoolbox import env
from otoolbox.base import Resource

from otoolbox.constants import PROCESS_SUCCESS, PROCESS_FAIL, PROCESS_EMPTY_MESSAGE


def pyenv_create(context: Resource):
    """
    Initialize the development env.

    It install and init .venv to the workspace. It also install all required
    tools for the development env. All odoo dependencies are installed
    in the .venv.


    """
    result = subprocess.run(
        [
            "python3",
            "-m",
            "venv",
            env.get_workspace_path(context.path),
        ],
        cwd=env.get_workspace(),
        text=True,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def pyenv_install(context: Resource):
    """Install dependencis in ptython environment from context.path"""

    venv_path = env.context.get("venv_path", ".venv")
    if sys.platform == "win32":
        python_executable = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_executable = os.path.join(venv_path, "bin", "python")

    if not os.path.isfile(python_executable):
        raise RuntimeError(
            f"Error: Python executable not found at '{python_executable}'. Is '{venv_path}' a valid venv?"
        )
    result = subprocess.run(
        [
            python_executable,
            "-m",
            "pip",
            "install",
            "-r",
            env.get_workspace_path(context.path),
        ],
        cwd=env.get_workspace(),
        text=True,
        check=False,
        capture_output=True,
    )
    logging.info(result.stdout)
    logging.info(result.stderr)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE
