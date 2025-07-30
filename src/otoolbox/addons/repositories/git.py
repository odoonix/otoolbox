import os
import logging
import subprocess

from otoolbox import env
from otoolbox import utils
from otoolbox.base import Resource
from otoolbox.constants import (
    PROCESS_SUCCESS,
    PROCESS_FAIL,
    PROCESS_EMPTY_MESSAGE,
    PROCESS_NOT_IMP_MESSAGE,
)
from otoolbox.addons.repositories.constants import (
    GIT_ADDRESS_HTTPS,
    GIT_ADDRESS_SSH,
    GIT_ERROR_TABLE,
    GIT_COMMAND
)

_logger = logging.getLogger(__name__)





######################################################################################
#                                Git Utilities                                       #
#                                                                                    #
#                                                                                    #
######################################################################################

def _rais_git_error(context, error_code):
    if not error_code:
        return
    error = GIT_ERROR_TABLE.get(error_code, {
        'level': 'fatal',
        'message': "Unknown GIT error for distination path {path}. Error code is {error_code}. "
        "See .otoolbox/logs.text for more information."
    })
    message = error['message'].format(error_code=error_code, **context.__dict__)
    if env.context.get('continue_on_exception'):
        _logger.error(message)
        env.errors.append(message)
    else:
        raise RuntimeError(
            error['message'].format(error_code=error_code, **context.__dict__)
        )

def _get_branch_info(context: Resource):
    cwd = env.get_workspace_path(context.path)
    result = subprocess.run(
        [GIT_COMMAND, "show-branch", "--current"],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
    )
    return str.strip(result.stdout)

######################################################################################
#                             Resource Processors                                    #
# Resource processors are used to process resources from the workspace. The resource #
# must be a git repository.                                                          #
######################################################################################

def git_clone(context: Resource):
    """Clone the git repository from github"""
    branch_name = context.branch if context.branch else env.context.get("odoo_version", "18.0")
    cwd = env.get_workspace_path(context.parent)
    depth = env.context.get("depth", "1")

    result = utils.call_process_safe(
        [
            GIT_COMMAND,
            "clone",
            "--branch",
            branch_name,
            "--depth",
            depth,
            (
                GIT_ADDRESS_HTTPS
                if not env.context.get("ssh_git", True)
                else GIT_ADDRESS_SSH
            ).format(path=context.path),
        ],
        cwd=cwd,
    )

    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, _get_branch_info(context=context)


def git_pull(context: Resource):
    """Pull the git repository from github"""
    cwd = env.get_workspace_path(context.path)
    result = utils.call_process_safe([GIT_COMMAND, "pull"], cwd=cwd)

    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, _get_branch_info(context=context)
