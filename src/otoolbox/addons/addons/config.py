"""Ma"""

import os
import ast
import traceback

from otoolbox import env
from otoolbox.addons.repositories.config import (
    _load_repository_list,
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
    item.update(
        {
            "path": f"{item.get('organization')}/{item.get('repository')}/{item.get('technical_name')}",
            "parent": f"{item.get('organization')}/{item.get('repository')}",
            "name": item.get("technical_name"),
            "title": manifest.get("name"),
            "description": manifest.get("summary"),
            "author": manifest.get("author"),
            "organization": item.get("organization"),
            "repository": item.get("repository"),
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
        }
    )
    return item





def load_addon_resources():
    """Load the resources for all addons dynamically.

    Each addon is added as a resource in the workspace.
    Addons are discovered based on repositories.json.
    """

    repo_list = _load_repository_list()
    addons_list = []

    for item in repo_list:
        # Resolve addon root path
        if item.get("organization") == "odoo" and item.get("repository") == "odoo":
            repo_path = env.get_workspace_path(
                item.get("organization"), item.get("repository"), "addons"
            )
        elif (
            item.get("organization") == "odoo"
            and item.get("repository") == "enterprise"
        ):
            repo_path = env.get_workspace_path(
                item.get("organization"), item.get("repository"), "odoo", "addons"
            )
        else:
            repo_path = env.get_workspace_path(
                item.get("organization"), item.get("repository")
            )

        if not os.path.isdir(repo_path):
            # Skip missing repositories
            continue

        for folder_name in os.listdir(repo_path):
            folder_path = os.path.join(repo_path, folder_name)
            manifest_path = os.path.join(folder_path, "__manifest__.py")

            if not (os.path.isdir(folder_path) and os.path.isfile(manifest_path)):
                continue

            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Safely parse manifest file
                manifest_dict = ast.literal_eval(content)

                addons_list.append(
                    {
                        **item,
                        "technical_name": folder_name,
                        "manifest": manifest_dict,
                    }
                )

            except (SyntaxError, ValueError) as exc:
                # Print clear error and continue
                print("=" * 80)
                print("Invalid __manifest__.py detected")
                print(f"Addon      : {folder_name}")
                print(f"Path       : {manifest_path}")
                print(f"Error type : {type(exc).__name__}")
                print(f"Message    : {exc}")
                print("=" * 80)
                continue

            except Exception:
                # Catch any unexpected error to avoid breaking the scan
                print("=" * 80)
                print("Unexpected error while reading __manifest__.py")
                print(f"Addon : {folder_name}")
                print(f"Path  : {manifest_path}")
                traceback.print_exc()
                print("=" * 80)
                continue

    # Register addons as resources
    for addon in addons_list:
        resource = _convert_addon_to_resources(addon)
        env.add_resource(**resource)

