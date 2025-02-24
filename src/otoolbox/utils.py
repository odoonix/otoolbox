import os
import logging
import subprocess
import typer

from otoolbox.base import (WorkspaceResource)
from otoolbox import env
from otoolbox.env import (
    get_workspace_path,
    resource_stream,
)
from otoolbox.constants import (
    ERROR_CODE_PRE_VERIFICATION
)

_logger = logging.getLogger(__name__)


def verify_all_resource(should_exit=True):
    continue_on_exception = env.context.get('continue_on_exception', True)
    verified = env.context['resources'].verify(
        continue_on_exception=continue_on_exception
    )
    total = env.context['resources'].get_validators_len()
    if verified != total and should_exit:
        print('Resource verification fail.')
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
        with open(get_workspace_path(".otoolbox/logs.txt"), "a", encoding="utf8") as log:
            ret = subprocess.call(
                command, 
                shell=shell,
                cwd=cwd, 
                stdout=log, 
                stderr=log
            )
            return ret
    except Exception as e:
        _logger.error('Failed to execute command: %s', e)
        return 2


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

def constructor_copy_resource(path, packag_name:str="otoolbox"):
    """Create a constructor to copy resource with path"""
    def copy_resource(context: WorkspaceResource):
        stream = resource_stream(path,packag_name=packag_name)
        # Open the output file in write-binary mode
        out_file_path = get_workspace_path(context.path)
        with open(out_file_path, 'wb') as out_file:
            # Read from the resource stream and write to the output file
            out_file.write(stream.read())
    return copy_resource

###################################################################
# validators
###################################################################


def is_readable(context: WorkspaceResource):
    file = get_workspace_path(context.path)
    assert os.access(file, os.R_OK), \
        f"File {file} doesn't exist or isn't readable"


def is_dir(context: WorkspaceResource):
    file = get_workspace_path(context.path)
    assert os.path.isdir(file), \
        f"File {file} doesn't exist or isn't readable"


def is_file(context: WorkspaceResource):
    file = get_workspace_path(context.path)
    assert os.path.isfile(file), \
        f"File {file} doesn't exist or isn't readable"


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
