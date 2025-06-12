"""Manage repository configurations"""

import os
import json
import re

from otoolbox import env
from otoolbox import utils


from otoolbox.constants import RESOURCE_PRIORITY_ROOT
from otoolbox.addons.repositories import git
from otoolbox.addons.repositories.constants import (
    REPOSITORIES_PATH,
    RESOURCE_REPOSITORIES_PATH,
)


def _add_repo_to_resources(item):
    tags = list(
        set(
            item.get("tags", [])
            + [
                "git",
                "addon",
                f"{item.get("organization")}/{item.get("repository")}",
                item.get("organization"),
                item.get("branch"),
            ]
        )
    )
    item.update({
        "path": f"{item.get("organization")}/{item.get("repository")}",
        "parent": item.get("organization"),
        "title": item.get("repository"),
        "description": """Automaticaly added resources from git.""",
        "init": [git.git_clone],
        "update": [
            git.git_pull,
            utils.touch_dir,
        ],
        "destroy": [utils.delete_dir],
        "verify": [utils.is_dir, utils.is_readable],
        "tags": tags,
        "branch": item.get("branch"),
    })
    env.add_resource(**item)


def _add_organization_to_resources(organization):
    env.add_resource(
        priority=RESOURCE_PRIORITY_ROOT,
        path=organization,
        title=f"Git organization: {organization}",
        description="""Automaticaly added resources from git.""",
        init=[utils.makedir],
        update=[utils.touch_dir],
        destroy=[utils.delete_dir],
        verify=[utils.is_dir, utils.is_readable],
        tags=["organization", organization],
    )


def _load_repository_list():
    reposiotires_path = env.get_workspace_path(REPOSITORIES_PATH)
    data = False
    if os.path.isfile(reposiotires_path):
        with open(reposiotires_path, "r", encoding="utf8") as f:
            data = f.read()

    if data:
        return json.loads(data)
    branch = env.context.get("odoo_version")
    data = env.resource_string(RESOURCE_REPOSITORIES_PATH, packag_name=__name__)
    repo_list = json.loads(data)
    repo_list = [item for item in repo_list if branch in item.get("tags", [branch])]
    return repo_list


def _save_repository_list(repo_list):
    reposiotires_path = env.get_workspace_path(REPOSITORIES_PATH)
    _save_json_file(reposiotires_path,  repo_list)


def load_repos_resources():
    """Load the resources for the organization dynamically

    Each repository is added as a resource in the workspace. The resources are added
    based on the configuration file .repositoires.json. The configuration file is
    added as a resource in the workspace.
    """
    repo_list = _load_repository_list()
    for item in repo_list:
        _add_repo_to_resources(item)
    organizations = list(set([item["organization"] for item in repo_list]))
    for organization in organizations:
        _add_organization_to_resources(organization)


def add_repository(new_repo):
    """Adding a new repository into the list"""
    new_repo_list = _load_repository_list()
    for item in new_repo_list:
        if item.get("organization") == new_repo.get("organization") and item.get(
            "repository"
        ) == new_repo.get("repository"):
            return
    new_repo_list.append(new_repo)
    _save_repository_list(new_repo_list)
    _add_repo_to_resources(new_repo)


def remove_repository(organization, repository):
    """Remove a repository from list"""
    repo_list = _load_repository_list()
    new_repo_list = [
        d
        for d in repo_list
        if not (
            d.get("repository") == repository and d.get("organization") == organization
        )
    ]
    _save_repository_list(new_repo_list)


# Merge db

def _load_json_file(file_path):
    data = False
    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf8") as f:
            data = f.read()
    if not data:
        raise RuntimeError("Distination repository DB is not valid")
    return json.loads(data)


def _save_json_file(file_path, data):
    with open(file_path, "w", encoding="utf8") as f:
        f.write(json.dumps(data))


def _get_odoo_version(repository_path):
    directory = os.path.dirname(repository_path)
    env_path = os.path.join(directory, '.env')
    with open(env_path, 'r', encoding="utf8") as file:
        content = file.read()
    pattern = r'ODOO_VERSION="(\d+\.\d+)"'
    match = re.search(pattern, content)
    if match:
        version = match.group(1)
        return version
    else:
        raise RuntimeError("The source repository must be part of odoo workspace.")


def _merge_item_to_db(repo_db, repo_item, odoo_version):
    repo_item['tags'].append(odoo_version)
    for index, item in enumerate(repo_db):
        if item["organization"] == repo_item["organization"] and item["repository"] == repo_item["repository"]:
            repo_db[index]["tags"] = list(
                set(item["tags"] + [odoo_version]))
            return
    repo_db.append(repo_item)


def _remove_tag_if_not_in(repo_db, repo_item, odoo_version):
    for index, item in enumerate(repo_db):
        if item["organization"] == repo_item["organization"] and item["repository"] == repo_item["repository"]:
            return index
    repo_item["tags"] = list(
        set(repo_item["tags"]) - set([odoo_version]))


def merge_repository(dist, src):
    dist_repo = _load_json_file(dist)
    src_repo = _load_json_file(src)
    odoo_version = _get_odoo_version(src)
    for item in src_repo:
        _merge_item_to_db(dist_repo, item, odoo_version)

    for item in dist_repo:
        _remove_tag_if_not_in(src_repo, item, odoo_version)

    _save_json_file(dist, dist_repo)
