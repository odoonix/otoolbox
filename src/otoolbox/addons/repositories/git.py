import os
import logging

from otoolbox import env
from otoolbox import utils
from otoolbox.constants import (
    PROCESS_SUCCESS,
    PROCESS_FAIL,
    PROCESS_EMPTY_MESSAGE,
    PROCESS_NOT_IMP_MESSAGE,
)

_logger = logging.getLogger(__name__)

# GIT
GIT_ADDRESS_HTTPS = "https://github.com/{path}.git"
GIT_ADDRESS_SSH = "git@github.com:{path}.git"

GIT_ERROR_TABLE = {
    2: {
        "level": "fatal",
        "message": "Resource {path}, doese not exist or is not a git repository.",
    },
    128: {
        "level": "fatal",
        "message": "Destination path '{path}' already exists and is not an empty directory.",
    },
}


def _rais_git_error(context, error_code):
    if not error_code:
        return
    error = GIT_ERROR_TABLE.get(
        error_code,
        {
            "level": "fatal",
            "message": "Unknown GIT error for distination path {path}. Error code is {error_code}. "
            "See .logs.text for more information.",
        },
    )
    raise RuntimeError(
        error["message"].format(error_code=error_code, **context.__dict__)
    )


def git_clone(context):
    """Clone the git repository from github"""
    branch_name = context.branch if context.branch else env.context.get("odoo_version", "18.0")
    cwd = env.get_workspace_path(context.parent)
    depth = env.context.get("depth", "1")

    result = utils.call_process_safe(
        [
            "git",
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

    _rais_git_error(context=context, error_code=result)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def git_pull(context):
    """Pull the git repository from github"""
    cwd = env.get_workspace_path(context.path)
    result = utils.call_process_safe(["git", "pull"], cwd=cwd)

    _rais_git_error(context=context, error_code=result)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE
