from jsonpath_ng import parse
import json

from otoolbox import env
from otoolbox import utils
from otoolbox.base import Resource
from otoolbox.constants import PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


_jsonpath_addons_expr = parse("$.settings.odoo.addons")
_jsonpath_folders_expr = parse("$.folders")


def _load_data(context: Resource):
    with open(context.get_abs_path(), "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def _store_data(context: Resource, data):
    with open(context.get_abs_path(), "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def set_workspace_conf_odoo_addons(context: Resource):
    data = _load_data(context)
    resource_set = env.resources.filter(
        lambda resource: resource.has_tag("addon") and resource.path != "odoo/odoo")
    path_list = ["${workspaceFolder}/odoo/odoo/addons"] + [
        "${workspaceFolder}/" + resource.path for resource in resource_set if resource.enable_in_runtime
    ]
    _jsonpath_addons_expr.update(data, ",".join(path_list))
    _store_data(context, data)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def rebuile_folder_config(context: Resource):
    """Set folders in workspace configuration"""
    ############################################################
    # Adding all orgainizations as folder
    ############################################################
    # resource_set = env.resources.filter(
    #     lambda resource: resource.has_tag("organization"))
    # folders = []
    # for resource in resource_set:
    #     folders.append({
    #         "path": resource.path
    #     })

    ############################################################
    # Adding all the root folder
    ############################################################
    folders = [{
        "path": ".",
        "name": f"Odoo {env.context.get("odoo_version")}"
    }]

    # save to workspace
    data = _load_data(context)
    _jsonpath_folders_expr.update(data, folders)
    _store_data(context, data)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE
