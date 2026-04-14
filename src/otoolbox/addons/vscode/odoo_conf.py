from jsonpath_ng import parse
import json
import os

from otoolbox import env
from otoolbox.base import Resource
from otoolbox.constants import PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def _load_config(context: Resource):
    file_path = env.get_workspace_path(context.path)
    with open(file_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config


def _save_config(context: Resource, config):
    file_path = env.get_workspace_path(context.path)
    with open(file_path, "w", encoding="utf-8") as workspace_file:
        json.dump(
            config, 
            workspace_file, 
            indent=4, 
            sort_keys=True
        )



############################################################################################
# odoo.addons
############################################################################################


def set_workspace_conf_odoo_addons(context: Resource):
    """Filter list of addons"""
    data = _load_config(context)
    resource_set = env.resources.filter(
        lambda resource: (
            resource.has_tag("repository")
            and resource.path != "odoo/odoo"
            and env.is_addons_path(resource)
            and resource.enable_in_runtime
        )
    )

    # Sort based on periority
    sorted_resources = sorted(list(resource_set), key=lambda r: r.priority)
    path_list = ["${workspaceFolder}/odoo/odoo/addons"] + [
        "${workspaceFolder}/" + resource.path for resource in sorted_resources
    ]
    # Set addons path
    settings = data.get("settings", {})
    settings["odoo.addons"] = ",".join(path_list)
    # Remove nested odoo if exists
    if isinstance(settings.get("odoo"), dict):
        settings.pop("odoo", None)
    data["settings"] = settings

    # Store configuration
    _save_config(context, data)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def rebuile_folder_config(context: Resource):
    """Set folders in workspace configuration"""
    data = _load_config(context)
    data["folders"] = [{
        "path": ".", 
        "name": f"Odoo {env.context.get('odoo_version')}"
    }]
    _save_config(context, data)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE



############################################################################################
# odoo.bin
############################################################################################

def is_odoo_bin_set(context: Resource):
    config = _load_config(context)

    settings = config.get("settings", {})
    
    odoo_bin = settings["odoo.bin"]
    if not odoo_bin:
        return PROCESS_FAIL, "Odoo bin path is not set. \"odoo_bin\" should be set in the workspace configuration file."

    if not odoo_bin.endswith("/odoo/odoo/odoo-bin"):
        return PROCESS_WAR, "Odoo bin path seems not be set correctly. Please make sure the path is correct and the odoo-bin file exists."

    # Save config
    _save_config(context, config)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE

def set_odoo_bin(context: Resource):
    config = _load_config(context)

    settings = config.get("settings", {})
    settings["odoo.bin"] = "${workspaceFolder}/odoo/odoo/odoo-bin"

    # Save config
    _save_config(context, config)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE




############################################################################################
# editor settings
############################################################################################
_editor_config = {
    "editor.defaultFormatter": "ms-python.autopep8",
    "editor.wordWrap": "on",
    "editor.wordWrapColumn": 88,
    "editor.rulers": [88, 90],
}

def set_editor_setting(context: Resource):
    config = _load_config(context)

    settings = config.get("settings", {})
    settings.update(_editor_config)

    # Save config
    _save_config(context, config)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def is_editor_setting_set(context: Resource):
    config = _load_config(context)
    settings = config.get("settings", {})

    for key, value in _editor_config.items():
        if key not in settings:
            return PROCESS_WAR, f"Editor setting '{key}' is not set. Expected: {key}: {value}"

    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE



############################################################################################
# python settings
############################################################################################
_python_config = {
    "python.analysis.autoImportCompletions": True,
    "python.analysis.enableSyncServer": True,
    "python.analysis.supportAllPythonDocuments": True,
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.languageServer": "Pylance",
    "python.terminal.activateEnvInCurrentTerminal": True,
}
def set_python_setting(context: Resource):
    config = _load_config(context)

    settings = config.get("settings", {})
    settings.update(_python_config)

    # Save config
    _save_config(context, config)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def is_python_setting_set(context: Resource):
    config = _load_config(context)
    settings = config.get("settings", {})

    for key, value in _python_config.items():
        if key not in settings:
            return PROCESS_WAR, f"Python setting '{key}' is not set. Expected: {key}: {value}"

    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE

