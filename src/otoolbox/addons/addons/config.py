"""Ma"""
import os
import json
import re
import importlib.util
import ast




from otoolbox import env
from otoolbox import utils
from otoolbox.constants import RESOURCE_PRIORITY_ROOT
from otoolbox.addons.repositories import git
from otoolbox.addons.repositories.config import (
    _load_repository_list,

)
from .constants import (
    REPOSITORIES_KEY
)



def _convert_addon_to_resources(item):
        # {
        #     "repository": "website",
        #     "organization": "odoonix",
        #     "is_shielded": true,
        #     "enable_in_runtime": true,
        #     "tags": ["15.0", "16.0", "17.0"]
        
            # "technical_name": folder_name,
            # "manifest": manifest_dict,
        # },
    manifest = item.get("manifest")
    tags = list(
        set(
            item.get("tags", [])
            + [
                "addon",
                f"{item.get('organization')}/{item.get('repository')}/{item.get('technical_name')}",
                f"{item.get('organization')}/{item.get('repository')}",
                item.get("organization"),
            ]
        )
    )
    item.update({
        "path": f"{item.get('organization')}/{item.get('repository')}/{item.get('technical_name')}",
        "parent": f"{item.get('organization')}/{item.get('repository')}",
        "name": item.get('technical_name'),
        "title": manifest.get("name"),
        "description": manifest.get("summary"),
        "author": manifest.get("author"),
        "organization": item.get('organization'),
        "repository": item.get('repository'),
        "version": manifest.get("version"),
        "website": manifest.get("website"),
        "license": manifest.get("license"),
        "category": manifest.get("category"),
        "installable": manifest.get("installable"),
        # TODO: add others form __manifest__.py
        "init": [],
        "update": [],
        "destroy": [],
        "verify": [],
        "tags": tags,
        "branch": item.get("branch"),
    })
    return item





def load_addon_resources():
    """Load the resources for all addons dynamically

    Each addon is added as a resource in the workspace. Addons are added
    based on the repositoires.json.
    """
    repo_list = _load_repository_list()
    addons_list = []
    for item in repo_list:
        # Load lis of addons        
        repo_path =  env.get_workspace_path(item.get('organization'),item.get('repository'))
        if not os.path.isdir(repo_path):
            # TODO: maso, 2025: add a logger
            continue
        for folder_name in os.listdir(repo_path):
            folder_path = os.path.join(repo_path, folder_name)
            manifest_path = os.path.join(folder_path, "__manifest__.py")
            if os.path.isdir(folder_path) and os.path.isfile(manifest_path):
               
                with open(manifest_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    manifest_dict = ast.literal_eval(content)

                addons_list.append({
                    **item,
                    "technical_name": folder_name,
                    "manifest": manifest_dict,
                })

    for addon in addons_list:
        item = _convert_addon_to_resources(addon)
        env.add_resource(**item)