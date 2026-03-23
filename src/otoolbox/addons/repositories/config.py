"""Manage repository configurations"""

import os
import json
import re

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        tomllib = None

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
        set([
            *item.get("tags", []),
            "git",
            "repository",
            f"{item.get('organization')}/{item.get('repository')}",
            item.get("organization"),
            item.get("branch")
        ])
    )
    item.update(
        {
            "path": f"{item.get('organization')}/{item.get('repository')}",
            "parent": item.get("organization"),
            "title": item.get("repository"),
            "description": """Automaticaly added resources from git.""",
            "init": [git.git_add_safe_directory, git.git_clone],
            "update": [
                git.git_add_safe_directory,
                git.git_checkout,
                git.git_pull,
                utils.touch_dir,
            ],
            "destroy": [utils.delete_dir],
            "verify": [
                utils.is_dir, 
                utils.is_readable,
                utils.has_otoolbox_toml,
                git.is_git_repository,
                git.is_repository_branch_match_with_odoo_version,
            ],
            "tags": tags,
            "branch": item.get("branch"),
            "is_existe": item.get("is_existe", False),
        }
    )
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


def _discover_workspace_repositories():
    workspace_path = env.get_workspace()
    if not os.path.isdir(workspace_path):
        return []

    repo_list = []
    for organization_entry in sorted(os.scandir(workspace_path), key=lambda entry: entry.name):
        if not organization_entry.is_dir():
            continue

        for repository_entry in sorted(
            os.scandir(organization_entry.path), key=lambda entry: entry.name
        ):
            if not repository_entry.is_dir():
                continue

            git_dir = os.path.join(repository_entry.path, ".git")
            if os.path.isdir(git_dir):
                repo_list.append(
                    {
                        "repository": repository_entry.name,
                        "organization": organization_entry.name,
                    }
                )

    return repo_list





def _load_repository_toml(organization, repository):
    if tomllib is None:
        return {}

    toml_path = env.get_workspace_path(organization, repository, "otoolbox.toml")
    if not os.path.isfile(toml_path):
        return {}

    with open(toml_path, "rb") as file:
        data = tomllib.load(file)

    if isinstance(data.get("repository"), dict):
        return data.get("repository", {})
    if isinstance(data.get("resource"), dict):
        return data.get("resource", {})
    if (
        isinstance(data.get("otoolbox"), dict)
        and isinstance(data["otoolbox"].get("repository"), dict)
    ):
        return data["otoolbox"]["repository"]
    return data if isinstance(data, dict) else {}


def _extract_first_mirror(toml_data):
    mirror_list = toml_data.get("mirror")
    if not isinstance(mirror_list, list):
        return None

    for mirror_item in mirror_list:
        if isinstance(mirror_item, dict):
            return mirror_item
    return None


def _enrich_repository_item(item):
    organization = item.get("organization")
    repository = item.get("repository")
    if not organization or not repository:
        return item

    repo_path = env.get_workspace_path(organization, repository)
    toml_data = _load_repository_toml(organization, repository)

    # Priority: otoolbox.toml overrides repositories.json
    # Start with the lower-priority base (JSON), then let TOML win.
    merged_item = dict(item)
    merged_item.update(toml_data)

    first_mirror = _extract_first_mirror(toml_data)
    if first_mirror:
        linked_shielded_repository = first_mirror.get("repository")
        linked_shielded_organization = first_mirror.get("organization")
        merged_item.update(
            {
                "enable_in_runtime": False,
                "is_shielded": True,
                "linked_shielded_repository": linked_shielded_repository,
                "linked_shielded_organization": linked_shielded_organization,
                "linked_shielded_repo": linked_shielded_repository,
            }
        )

    merged_item.setdefault("organization", organization)
    merged_item.setdefault("repository", repository)
    merged_item["is_existe"] = git._is_git_repository(env.get_workspace_path(repo_path))
    merged_item["has_mirror"] = bool(merged_item.get("is_shielded", False))
    return merged_item


def _merge_repository_lists(repo_list, extra_repo_list):
    merged_repo_list = []
    seen = set()

    for item in [*repo_list, *extra_repo_list]:
        organization = item.get("organization")
        repository = item.get("repository")
        if not organization or not repository:
            continue

        repo_key = (organization, repository)
        if repo_key in seen:
            continue

        seen.add(repo_key)
        merged_repo_list.append(item)

    return merged_repo_list


def _load_repository_list():
    reposiotires_path = env.get_workspace_path(REPOSITORIES_PATH)
    data = False
    if os.path.isfile(reposiotires_path):
        with open(reposiotires_path, "r", encoding="utf8") as f:
            data = f.read()

    if data:
        repo_list = json.loads(data)
    else:
        data = env.resource_string(RESOURCE_REPOSITORIES_PATH, package_name=__name__)
        repo_list = json.loads(data)

    workspace_repo_list = _discover_workspace_repositories()
    merged_repo_list = _merge_repository_lists(repo_list, workspace_repo_list)
    return [_enrich_repository_item(item) for item in merged_repo_list]


def save_repository_list(repo_list):
    """Save the repository list to the configuration file
    
    Repositories in the list should have the following format:
    {
    "organization": "odoonix",
    "repository": "cnp",
    "branch": "17.0",
    "enable_in_runtime": False,
    "is_shielded": True,
    "linked_shielded_repository": "cnp",
    "linked_shielded_organization": "odoonix",
    "linked_shielded_repo": "cnp",
    ...
    }

    You have more control over the repositoy item by adding more fields in the item, 
    but the above fields are required for the basic functionality of the repository management.
    """
    reposiotires_path = env.get_workspace_path(REPOSITORIES_PATH)
    _save_json_file(reposiotires_path, repo_list)


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
    # NOTE: No need to save the list.
    # _save_repository_list(new_repo_list)
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
    # NOTE: No need to save the list.
    # _save_repository_list(new_repo_list)


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
    env_path = os.path.join(directory, ".env")
    with open(env_path, "r", encoding="utf8") as file:
        content = file.read()
    pattern = r'ODOO_VERSION="(\d+\.\d+)"'
    match = re.search(pattern, content)
    if match:
        version = match.group(1)
        return version
    else:
        raise RuntimeError("The source repository must be part of odoo workspace.")


def _merge_item_to_db(repo_db, repo_item, odoo_version):
    repo_item["tags"].append(odoo_version)
    for index, item in enumerate(repo_db):
        if (
            item["organization"] == repo_item["organization"]
            and item["repository"] == repo_item["repository"]
        ):
            repo_db[index]["tags"] = list(set(item["tags"] + [odoo_version]))
            return
    repo_db.append(repo_item)


def _remove_tag_if_not_in(repo_db, repo_item, odoo_version):
    for index, item in enumerate(repo_db):
        if (
            item["organization"] == repo_item["organization"]
            and item["repository"] == repo_item["repository"]
        ):
            return index
    repo_item["tags"] = list(set(repo_item["tags"]) - set([odoo_version]))


def merge_repository(dist, src):
    dist_repo = _load_json_file(dist)
    src_repo = _load_json_file(src)
    odoo_version = _get_odoo_version(src)
    for item in src_repo:
        _merge_item_to_db(dist_repo, item, odoo_version)

    for item in dist_repo:
        _remove_tag_if_not_in(src_repo, item, odoo_version)

    _save_json_file(dist, dist_repo)
