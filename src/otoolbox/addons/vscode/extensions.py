import os
import logging
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from dotenv import dotenv_values

from otoolbox.base import Resource
from otoolbox import env
import json
from otoolbox.constants import (
    PROCESS_SUCCESS,
    PROCESS_FAIL,
    PROCESS_WAR,
    PROCESS_EMPTY_MESSAGE,
)


ext_configs = {
    "extensions": {
        "recommendations": [
            "odoo.odoo",
            "github.copilot",
            "github.copilot-chat",
            "ms-python.autopep8",
            "ms-python.python",
            "ms-python.debugpy",
            "ms-python.vscode-python-envs",
            "ms-azuretools.vscode-docker",
            "ms-azuretools.vscode-containers",
            "mechatroner.rainbow-csv",
            "rioj7.command-variable"
        ]
    }
}


def set_recommanded_extensions(context: Resource):
    file_path = env.get_workspace_path(context.path)
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            config = json.load(f)
        except Exception:
            config = {}
    config.update(ext_configs)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE



def verify_recommanded_extensions(context: Resource):
    file_path = env.get_workspace_path(context.path)
    assert os.path.isfile(
        file_path
    ), f"File {file_path} doesn't exist or isn't readable"
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            config = json.load(f)
        except Exception:
            return PROCESS_FAIL, "Invalid JSON format in workspace configuration."
    
    recommendations = config.get("extensions", {}).get("recommendations", [])
    missing_extensions = [ext for ext in ext_configs["extensions"]["recommendations"] if ext not in recommendations]
    
    if missing_extensions:
        message = f"Missing recommended extensions: {', '.join(missing_extensions)}. Please add them to your VSCode workspace configuration."
        return PROCESS_WAR, message
    
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE