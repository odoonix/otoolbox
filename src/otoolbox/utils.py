import os
import logging
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv, dotenv_values

from otoolbox.base import Resource
from otoolbox import env
from otoolbox.constants import (
    ERROR_CODE_PRE_VERIFICATION,
    RESOURCE_ENV_FILE,
    PROCESS_SUCCESS,
    PROCESS_FAIL,
    PROCESS_EMPTY_MESSAGE,
    PROCESS_NOT_IMP_MESSAGE,
)

_logger = logging.getLogger(__name__)


######################################################################################
#                                 IO Utilities                                       #
#                                                                                    #
#                                                                                    #
######################################################################################
def _get_modif_date(context):
    path = env.get_workspace_path(context.path)
    result = subprocess.run(
        ["stat", "-c", "%y", path],
        capture_output=True,
        text=True,
        check=False,
    )
    return str.strip(result.stdout)


###################################################################
# constructors
###################################################################


def call_process_safe(command, **kwargs):
    """Execute a command in a subprocess and log the output"""
    if not kwargs.get("cwd"):
        kwargs.update({
            "cwd", env.get_workspace()
        })

    kwargs.update({
        # Use shell=True if command is a string (be cautious with security)
        'stdout': subprocess.PIPE,  # Capture stdout
        'stderr': subprocess.PIPE,  # Capture stderr
        'text': True,
        'check': False,
    })
    _logger.info("Command: %s", kwargs)
    result = subprocess.run(command, **kwargs)

    if result.stdout:
        _logger.info("Command output: %s", result.stdout.strip())

    # Log stderr (if any)
    if result.stderr:
        _logger.error("Command error: %s", result.stderr.strip())

    # Return the exit code
    return result


def run_command_in_venv(venv_path, command, cwd=None):
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

    cwd = cwd if cwd else env.get_workspace()
    if not os.path.isfile(python_executable):
        raise RuntimeError(
            f"Error: Python executable not found at '{python_executable}'. Is '{venv_path}' a valid venv?"
        )

    if command[0] == "python":
        command[0] = python_executable
    else:
        command = [python_executable] + command

    result = subprocess.run(
        command, check=True, text=True, capture_output=True, cwd=cwd
    )
    if result.stdout:
        _logger.info("Command output: %s", result.stdout.strip())

    # Log stderr (if any)
    if result.stderr:
        _logger.error("Command error: %s", result.stderr.strip())

    # Return the exit code
    return result.returncode


###################################################################
# constructors
###################################################################


def makedir(context: Resource):
    """Create new directory in the current workspace.

    Parameters:
    context (Resource): The resource detail"""
    path = env.get_workspace_path(context.path)
    if not os.path.exists(path):
        os.makedirs(path)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def touch_file(context: Resource):
    """Touch the file in the current workspace."""
    file_path = env.get_workspace_path(context.path)
    Path(file_path).touch()
    return PROCESS_SUCCESS, _get_modif_date(context=context)


def touch_dir(context: Resource):
    """Touch the file in the current workspace."""
    dir_path = env.get_workspace_path(context.path)
    subprocess.call(["mkdir", "-p", dir_path], text=True)
    Path(dir_path).touch()
    return PROCESS_SUCCESS, _get_modif_date(context=context)


def constructor_copy_resource(path, packag_name: str = "otoolbox"):
    """Create a constructor to copy resource with path"""

    def copy_resource(context: Resource):
        stream = env.resource_stream(path, packag_name=packag_name)
        # Open the output file in write-binary mode
        out_file_path = env.get_workspace_path(context.path)
        with open(out_file_path, "wb") as out_file:
            # Read from the resource stream and write to the output file
            out_file.write(stream.read())
        return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE

    return copy_resource


def chmod_executable(context: Resource):
    file_path = env.get_workspace_path(context.path)
    os.chmod(file_path, 0o755)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


###################################################################
# validators
###################################################################


def is_readable(context: Resource):
    file_path = env.get_workspace_path(context.path)
    assert os.access(
        file_path, os.R_OK
    ), f"File {file_path} doesn't exist or isn't readable"
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def is_writable(context: Resource):
    file_path = env.get_workspace_path(context.path)
    assert os.access(
        file_path, os.W_OK
    ), f"File {file_path} doesn't exist or isn't writable"
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def is_dir(context: Resource):
    file_path = env.get_workspace_path(context.path)
    assert os.path.isdir(file_path), f"File {file_path} doesn't exist or isn't readable"
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def is_file(context: Resource):
    file_path = env.get_workspace_path(context.path)
    assert os.path.isfile(
        file_path
    ), f"File {file_path} doesn't exist or isn't readable"
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def is_executable(context: Resource):
    is_file(context=context)

    file_path = env.get_workspace_path(context.path)
    mode = os.stat(file_path).st_mode
    assert mode & (0o100 | 0o010 | 0o001), f"File {file_path} isn't executable"
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


###################################################################
# destructors
###################################################################


def delete_file(context: Resource):
    """
    Delete a file
    """
    file_path = env.get_workspace_path(context.path)
    # Check if the file exists before attempting to delete it
    if os.path.exists(file_path):
        os.remove(file_path)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def delete_dir(context: Resource):
    """
    Delete a directory and its contents
    """
    result = subprocess.run(
        ["rm", "-fR", context.get_abs_path()],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        return PROCESS_FAIL, str.strip(result.stderr)
    return PROCESS_SUCCESS, str.strip(result.stdout)


###################################################################
# destructors
###################################################################
def __is_not_primitive(value):
    primitive_types = (int, float, str, bool, type(None))
    return not isinstance(value, primitive_types)


def set_to_env(path, key, value):
    """Adds new environment variable to the .env file and optionally to the current
    process environment."""

    if __is_not_primitive(value):
        return
    key = key.upper()
    value = str(value)

    if key in ["PATH"]:
        _logger.warning(
            "Forbiden to change Linux default environment variables: %s", key
        )
        return

    env_vars = dotenv_values(path)
    env_vars[key] = value

    # Write all variables back to the .env file
    with open(path, "w", encoding="utf8") as f:
        for k, v in env_vars.items():
            f.write(f'{k}="{v}"\n')

    # Optionally, update the current process environment
    os.environ[key] = str(value)


def set_to_env_all(context: Resource):
    """Adds all environment variables to the .env file and optionally to the current
    process environment."""
    path = env.get_workspace_path(context.path)
    for k, v in env.context.items():
        set_to_env(path, k, v)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def print_result(result=None):
    """Print resource executors"""
    if not result:
        return
    counter = 0
    for processors, executor in result:
        counter += 1
        env.console.print(
            f"\n{executor.resource} ({counter}, {executor.resource.priority})"
        )
        for res, message, processor in processors:
            env.console.print(f"[{res}] {processor} ({message})")


###################################################################
# destructors
###################################################################
def _find_text_in_lines(text, pattern):
    pattern = pattern.lower()
    for line in text.splitlines():
        if pattern in line.lower():
            return line
    return None


def pipx_install(context: Resource):
    """Install an aplication  from pipx"""
    url = urlparse(context.path)
    if url.scheme != 'application':
        raise RuntimeError(
            "Impossible to use PIPX installer for non application resources")
    application = url.netloc
    cwd = env.get_workspace_path(".")
    result = call_process_safe(
        [
            "pipx",
            "install",
            application
        ],
        cwd=cwd,
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, f"apaplication {application} is installed"


def pipx_remove(context: Resource):
    pass


def pipx_update(context: Resource):
    pass


def pipx_is_install(context: Resource):
    """Check if the application is installed with pipx"""
    url = urlparse(context.path)
    if url.scheme != 'application':
        raise RuntimeError(
            "Impossible to use PIPX installer for non application resources")
    application = url.netloc
    cwd = env.get_workspace_path(".")
    result = call_process_safe(
        [
            "pipx",
            "list",
            "--short"
        ],
        cwd=cwd,
    )

    version = _find_text_in_lines(result.stdout, application)
    if not version:
        raise RuntimeError(f"Application {application} is not installed with pipx")
    return PROCESS_SUCCESS, version


def pipx_ensurepath(context: Resource):
    """Check if pipx path is ok"""
    cwd = env.get_workspace_path(".")
    result = call_process_safe(
        [
            "pipx",
            "ensurepath"
        ],
        cwd=cwd,
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE
