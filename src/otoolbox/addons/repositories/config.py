"""Manage repository configurations"""

import os
import json

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
    env.add_resource(
        path=f"{item.get("organization")}/{item.get("repository")}",
        parent=item.get("organization"),
        title=item.get("repository"),
        description="""Automaticaly added resources from git.""",
        init=[git.git_clone],
        update=[
            git.git_pull,
            utils.touch_dir,
        ],
        destroy=[utils.delete_dir],
        verify=[utils.is_dir, utils.is_readable],
        tags=tags,
        branch=item.get("branch"),
    )


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
        tags=["git", organization],
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
    with open(reposiotires_path, "w", encoding="utf8") as f:
        f.write(json.dumps(repo_list))


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
