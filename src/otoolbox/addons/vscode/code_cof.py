from jsonpath_ng import parse
import json

from otoolbox import env
from otoolbox import utils
from otoolbox.base import Resource
from otoolbox.constants import PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


_jsonpath_addons_expr = parse("$.settings.odoo.addons")


def set_workspace_conf_odoo_addons(context: Resource):
    with open(context.get_abs_path(), "r", encoding="utf-8") as file:
        data = json.load(file)
    resource_set = env.resources.filter(lambda resource: resource.has_tag("addon") and resource.path != "odoo/odoo")
    path_list = ["${workspaceFolder}/odoo/odoo/addons"] + [
        "${workspaceFolder}/" + resource.path for resource in resource_set
    ]
    _jsonpath_addons_expr.update(data, ",".join(path_list))
    with open(context.get_abs_path(), "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE
