"""Utilities for otoolbox to mainpulate odools.toml configuration file.

This file is part of otoolbox.

OdooLS is using (since 0.8.0) configuration files to detect your odoo setup and use right
configuration variables according to your needs.

This module provides utilities to create and manage odools.toml configuration file in your project.

"""

import re

from otoolbox import env
from otoolbox.base import Resource
from otoolbox.constants import PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def set_odoo_path(context: Resource):
    """Sets odoo_path varibale in odools.toml configuration file to context.path.

    The odools.toml is depends on all modules. So we suppose this funcition is called after all
    resources are initialized. So we can be sure that odools.toml file is created and we can edit it.

    odoo_path is the abslote path of odoo/odoo resource.

    """
    odoo_community_resource = env.resources["odoo/odoo"]
    odoo_path = env.get_workspace_path(odoo_community_resource.path)

    # Open odools.toml file and set odoo_path variable
    odools_path = env.get_workspace_path("odools.toml")
    with open(odools_path, "r", encoding="utf-8") as f:
        odools_config_data = f.read()
    pattern = r"^odoo_path\s*=\s*.*$"
    replacement = f'odoo_path = "{odoo_path}"'
    if re.search(pattern, odools_config_data, flags=re.MULTILINE):
        odools_config_data = re.sub(
            pattern, replacement, odools_config_data, flags=re.MULTILINE
        )
    else:
        if not odools_config_data.endswith("\n"):
            odools_config_data += "\n"
        odools_config_data += replacement + "\n"
    with open(odools_path, "w", encoding="utf-8") as f:
        f.write(odools_config_data)

    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def set_addons_paths(context: Resource):
    """Sets addons_paths variable in odools.toml configuration file to list of all addons paths in the workspace.


    here is an example of addons_paths variable in odools.toml file:

    addons_paths = [
        "${workspaceFolder}/odoonix/brand"
    ]

    """
    # Get list of target repostiory TARGET_REPOSITORIES which is an array
    # of string like "odoo" or "moonsunsoft". This is an environment
    # variable that can be set in .env file.
    # eg: TARGET_REPOSITORIES=("odoo" "moonsunsoft")
    target_repositories = env.get_env_variable("TARGET_REPOSITORIES", [])

    resource_set = env.resources.filter(
        lambda resource: (
            resource.has_tag("repository")
            and resource.path != "odoo/odoo"
            and resource.enable_in_runtime
            and env.is_addons_path(resource)
            and (not target_repositories or resource.parent in target_repositories)
        )
    )

    # Sort based on periority
    sorted_resources = sorted(list(resource_set), key=lambda r: r.priority)
    addons_paths = [
        "${workspaceFolder}/" + resource.path for resource in sorted_resources
    ]

    # create str value
    addons_paths_str = (
        "[\n" + ",\n".join(f'    "{path}"' for path in addons_paths) + "\n]"
    )
    pattern = r"^addons_paths\s*=\s*\[.*?\]$"
    replacement = f"addons_paths = {addons_paths_str}"

    odools_path = env.get_workspace_path("odools.toml")
    with open(odools_path, "r", encoding="utf-8") as f:
        odools_config_data = f.read()

    if re.search(pattern, odools_config_data, flags=re.MULTILINE | re.DOTALL):
        odools_config_data = re.sub(
            pattern, replacement, odools_config_data, flags=re.MULTILINE | re.DOTALL
        )
    else:
        if not odools_config_data.endswith("\n"):
            odools_config_data += "\n"
        odools_config_data += replacement + "\n"

    with open(odools_path, "w", encoding="utf-8") as f:
        f.write(odools_config_data)

    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE
