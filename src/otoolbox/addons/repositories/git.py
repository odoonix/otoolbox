import logging
import subprocess
import os

from otoolbox import env
from otoolbox import utils
from otoolbox.base import Resource
from otoolbox.constants import (
    PROCESS_SUCCESS,
    PROCESS_FAIL,
    PROCESS_EMPTY_MESSAGE
)
from otoolbox.addons.repositories.constants import (
    GIT_ADDRESS_HTTPS,
    GIT_ADDRESS_SSH,
    GIT_ERROR_TABLE,
    GIT_COMMAND,
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
    error = GIT_ERROR_TABLE.get(
        error_code,
        {
            "level": "fatal",
            "message": "Unknown GIT error for distination path {path}. Error code is {error_code}. "
            "See .otoolbox/logs.text for more information.",
        },
    )
    message = error["message"].format(error_code=error_code, **context.__dict__)
    if env.context.get("continue_on_exception"):
        _logger.error(message)
        env.errors.append(message)
    else:
        raise RuntimeError(
            error["message"].format(error_code=error_code, **context.__dict__)
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

def _get_branch_name(context: Resource):
    cwd = env.get_workspace_path(context.path)
    result = subprocess.run(
        [GIT_COMMAND, "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
    )
    return next((line.strip() for line in result.stdout.splitlines() if line.strip()), "")

def _is_git_repository(repository_path):
    if not os.path.isdir(repository_path):
        return False

    git_path = os.path.join(repository_path, ".git")
    return os.path.isdir(git_path) or os.path.isfile(git_path)

######################################################################################
#                             Resource Processors                                    #
# Resource processors are used to process resources from the workspace. The resource #
# must be a git repository.                                                          #
######################################################################################


def git_clone(context: Resource):
    """Clone the git repository from github"""
    branch_name = (
        context.branch if context.branch else env.context.get("odoo_version", "18.0")
    )
    cwd = env.get_workspace_path(context.parent)

    result = utils.call_process_safe(
        [
            GIT_COMMAND,
            "clone",
            "--branch",
            branch_name,
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
    return PROCESS_SUCCESS, _get_branch_name(context=context)


def git_pull(context: Resource):
    """Pull the git repository from github"""
    cwd = env.get_workspace_path(context.path)
    result = utils.call_process_safe([GIT_COMMAND, "pull"], cwd=cwd)

    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, _get_branch_name(context=context)


def git_checkout(context: Resource):
    """Pull the git repository from github"""
    cwd = env.get_workspace_path(context.path)
    branch_name = (
        context.branch if context.branch else env.context.get("odoo_version", "18.0")
    )
    result = utils.call_process_safe([GIT_COMMAND, "checkout", branch_name], cwd=cwd)

    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, _get_branch_name(context=context)


def git_add_safe_directory(context: Resource):
    """Add repository path to global git safe.directory list."""
    repository_path = env.get_workspace_path(context.path)
    result = utils.call_process_safe(
        [
            GIT_COMMAND,
            "config",
            "--global",
            "--add",
            "safe.directory",
            repository_path,
        ],
        cwd=env.get_workspace(),
    )

    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, f"safe.directory added: {repository_path}"

def is_git_repository(context: Resource):
    """Check if the given path is a git repository."""
    git_dir = env.get_workspace_path(context.path)
    if _is_git_repository(git_dir):
        return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE
    return PROCESS_FAIL, "Not a git repository."


def is_repository_branch_match_with_odoo_version(context: Resource):
    """Check if the repository branch matches with the odoo version."""
    branch_name = _get_branch_name(context)
    odoo_version = env.context.get("odoo_version", "18.0")
    if branch_name == odoo_version:
        return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE
    return (
        PROCESS_FAIL,
        f"Repository branch '{branch_name}' does not match with Odoo version '{odoo_version}'.",
    )
