"""Adds resources to manage repositories

Resources:
- .otoolbox/repositoires.json

"""
import os
import json

from otoolbox import env
from otoolbox import utils
from otoolbox import addons
from otoolbox.constants import (
    RESOURCE_PRIORITY_ROOT
)

from otoolbox.addons.repositories import git


REPOSITORIES_PATH = ".otoolbox/repositoires.json"
RESOURCE_REPOSITORIES_PATH = "data/repositories.json"
###################################################################
# init
###################################################################


def _load_repositories():
    reposiotires_path = env.get_workspace_path(REPOSITORIES_PATH)
    data = False
    if os.path.isfile(reposiotires_path):
        with open(reposiotires_path, 'r', encoding="utf8") as f:
            data = f.read()

    if not data:
        data = env.resource_string(
            RESOURCE_REPOSITORIES_PATH,
            packag_name=__name__
        )
    repo_list = json.loads(data)
    workspaces = []
    for item in repo_list:
        env.add_resource(
            path="{}/{}".format(item["workspace"], item["name"]),
            parent=item["workspace"],
            title=item["name"],
            description="""Automaticaly added resources from git.""",
            constructors=[
                git.git_clone
            ],
            updates=[
                git.git_pull
            ],
            destructors=[],
            validators=[],
            tags=['git', item["workspace"], *item.get('tags', [])]
        )
        if item["workspace"] not in workspaces:
            workspaces.append(item["workspace"])

    for workspace_path in workspaces:
        env.add_resource(
            priority=RESOURCE_PRIORITY_ROOT,
            path=workspace_path,
            title="Git workspace: {}".format(workspace_path),
            description="""Automaticaly added resources from git.""",
            constructors=[
                utils.makedir
            ],
            updates=[],
            destructors=[],
            validators=[],
        )


def init():
    """Init the resources for the workspace
    """
    (env
        .add_resource(
            priority=RESOURCE_PRIORITY_ROOT,
            path=REPOSITORIES_PATH,
            title="List of managed repositories",
            description="Adding, removing, and updating repositories in the workspace is done through this file",
            constructors=[
                utils.constructor_copy_resource(
                    RESOURCE_REPOSITORIES_PATH,
                    packag_name=__name__)
            ],
            destructors=[
                utils.delete_file
            ],
            validators=[
                utils.is_file,
                utils.is_readable
            ]
        )
     )
    _load_repositories()
