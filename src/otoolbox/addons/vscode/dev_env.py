
from otoolbox import utils
from otoolbox import env
from otoolbox.base import Resource
from otoolbox.constants import (
    PROCESS_SUCCESS,
    PROCESS_FAIL,
    PROCESS_EMPTY_MESSAGE,
    PROCESS_NOT_IMP_MESSAGE,
)


def install(context: Resource):
    """Install python package from resource"""
    utils.run_command_in_venv(
        env.get_workspace_path(".venv"),
        [
            "python",
            "-m",
            "pip",
            "install",
            "-r",
            env.get_workspace_path(context.path),
        ],
        cwd=env.get_workspace(),
    )
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def create(context: Resource):
    """Creates new VENV"""
    utils.call_process_safe(
        [
            "python3",
            "-m",
            "venv",
            env.get_workspace_path(context.path),
        ],
        cwd=env.get_workspace(),
    )
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE
