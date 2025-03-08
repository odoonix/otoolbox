import os
import logging
import subprocess
import sys
from pathlib import Path

import typer
from dotenv import load_dotenv, dotenv_values

from otoolbox.base import WorkspaceResource
from otoolbox import env
from otoolbox.env import (
    get_workspace_path,
    resource_stream,
)
from otoolbox.constants import ERROR_CODE_PRE_VERIFICATION, RESOURCE_ENV_FILE

_logger = logging.getLogger(__name__)


def verify_all_resource(should_exit=True):
    continue_on_exception = env.context.get("continue_on_exception", True)
    verified = env.context["resources"].verify(
        continue_on_exception=continue_on_exception
    )
    total = env.context["resources"].get_validators_len()
    if verified != total and should_exit:
        print("Resource verification fail.")
        typer.Exit(ERROR_CODE_PRE_VERIFICATION)
    return verified != total, verified, total


###################################################################
# constructors
###################################################################


def call_process_safe(command, shell=False, cwd=None):
    """Execute a command in a subprocess and log the output"""
    try:
        if not cwd:
            cwd = env.get_workspace()
        with open(get_workspace_path(".logs.txt"), "a", encoding="utf8") as log:
            ret = subprocess.call(command, shell=shell, cwd=cwd, stdout=log, stderr=log)
            return ret
    except Exception as e:
        _logger.error("Failed to execute command: %s", e)
        return 2


def run_command_in_venv(venv_path, command, shell=False, cwd=None):
    """
    Runs a command in a specified virtual environment using subprocess.

    Args:
        venv_path (str): Path to the virtual environment directory (e.g., './myenv').
        command (list): Command to run as a list (e.g., ['python', '-c', 'print("Hello")']).
    """
    if sys.platform == "win32":
        python_executable = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_executable = os.path.join(venv_path, "bin", "python")

    if not cwd:
        cwd = env.get_workspace()
    if not os.path.isfile(python_executable):
        print(
            f"Error: Python executable not found at '{python_executable}'. Is '{venv_path}' a valid venv?"
        )
        return

    if command[0] == "python":
        command[0] = python_executable
    else:
        command = [python_executable] + command

    try:
        result = subprocess.run(
            command, check=True, text=True, capture_output=True, shell=shell, cwd=cwd
        )
        print("Output:", result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")
    except FileNotFoundError:
        print(f"Error: '{command[0]}' not found.")


###################################################################
# constructors
###################################################################


def makedir(context: WorkspaceResource):
    """Create new directory in the current workspace.

    Parameters:
    context (WorkspaceResource): The resource detail"""
    path = get_workspace_path(context.path)
    if not os.path.exists(path):
        os.makedirs(path)


def touch(context: WorkspaceResource):
    """Touch the file in the current workspace."""
    file_path = get_workspace_path(context.path)
    Path(file_path).touch()


def constructor_copy_resource(path, packag_name: str = "otoolbox"):
    """Create a constructor to copy resource with path"""

    def copy_resource(context: WorkspaceResource):
        stream = resource_stream(path, packag_name=packag_name)
        # Open the output file in write-binary mode
        out_file_path = get_workspace_path(context.path)
        with open(out_file_path, "wb") as out_file:
            # Read from the resource stream and write to the output file
            out_file.write(stream.read())

    return copy_resource


###################################################################
# validators
###################################################################


def is_readable(context: WorkspaceResource):
    file = get_workspace_path(context.path)
    assert os.access(file, os.R_OK), f"File {file} doesn't exist or isn't readable"


def is_writable(context: WorkspaceResource):
    file = get_workspace_path(context.path)
    assert os.access(file, os.W_OK), f"File {file} doesn't exist or isn't writable"


def is_dir(context: WorkspaceResource):
    file = get_workspace_path(context.path)
    assert os.path.isdir(file), f"File {file} doesn't exist or isn't readable"


def is_file(context: WorkspaceResource):
    file = get_workspace_path(context.path)
    assert os.path.isfile(file), f"File {file} doesn't exist or isn't readable"


###################################################################
# destructors
###################################################################


def delete_file(context: WorkspaceResource):
    """
    Delete a file
    """
    file_path = get_workspace_path(context.path)
    # Check if the file exists before attempting to delete it
    if os.path.exists(file_path):
        os.remove(file_path)
        _logger.info(f"{file_path} has been deleted successfully.")
    else:
        _logger.warn(f"{file_path} does not exist.")


def delete_dir(context: WorkspaceResource):
    """
    Delete a directory and its contents
    """
    pass


###################################################################
# destructors
###################################################################
def is_not_primitive(value):
    primitive_types = (int, float, str, bool, type(None))
    return not isinstance(value, primitive_types)

def set_to_env(path, key, value):
    """Adds new environment variable to the .env file and optionally to the current process environment."""

    if is_not_primitive(value):
        return
    key = key.upper()
    value = str(value)

    env_vars = dotenv_values(path)
    env_vars[key] = value
    

    # Write all variables back to the .env file
    with open(path, "w", encoding="utf8") as f:
        for k, v in env_vars.items():
            f.write(f'{k}="{v}"\n')

    # Optionally, update the current process environment
    os.environ[key] = str(value)


def set_to_env_all(context: WorkspaceResource):
    """Adds all environment variables to the .env file and optionally to the current process environment."""
    path = env.get_workspace_path(context.path)
    for k, v in env.context.items():
        set_to_env(path, k, v)
