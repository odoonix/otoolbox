import os
import json
from typing import List

from otoolbox import env
from otoolbox import utils
# from otoolbox import linux
# from otoolbox.repositories import linux


from otoolbox.constants import (
    RESOURCE_PRIORITY_ROOT
)
from otoolbox.addons.repositories import git
from otoolbox.addons.repositories.constants import (
    REPOSITORIES_PATH,
    RESOURCE_REPOSITORIES_PATH
)


def load_repos_resources():
    """Load the resources for the workspace dynamically

    Each repository is added as a resource in the workspace. The resources are added
    based on the configuration file .repositoires.json. The configuration file is
    added as a resource in the workspace.
    """
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
        tags = item.get('tags') if isinstance(item.get('tags'), List) else []
        env.add_resource(
            path="{}/{}".format(item["workspace"], item["name"]),
            parent=item["workspace"],
            title=item["name"],
            description="""Automaticaly added resources from git.""",
            init=[
                git.git_clone
            ],
            update=[
                utils.touch,
                git.git_pull
            ],
            destroy=[utils.delete_dir],
            verify=[utils.is_dir, utils.is_readable],
            tags=['git', item["workspace"], *tags],
            branch=item.get("branch")
        )
        if item["workspace"] not in workspaces:
            workspaces.append(item["workspace"])

    for workspace_path in workspaces:
        env.add_resource(
            priority=RESOURCE_PRIORITY_ROOT,
            path=workspace_path,
            title="Git workspace: {}".format(workspace_path),
            description="""Automaticaly added resources from git.""",
            init=[
                utils.makedir
            ],
            update=[utils.touch],
            destroy=[utils.delete_dir],
            verify=[utils.is_dir, utils.is_readable],
        )


class ModuleList(list):
    def __rich__(self):
        return '\n'.join(self)

    def difference(self, other):
        new_list = ModuleList()
        for item in self:
            if item not in other:
                new_list.append(item)
        return new_list


def is_addons(name, dir):
    new_path = os.path.join(name, dir)
    for file_name in os.listdir(new_path):
        if file_name == '__manifest__.py':
            return True
    return False


def get_addons_list(name, *args, **kargs):
    addons_list = ModuleList()
    if not os.path.exists(name) \
            or os.path.isfile(name):
        return addons_list

    for dir in os.listdir(name):
        new_path = os.path.join(name, dir)
        if os.path.isdir(new_path) \
                and is_addons(name, dir):
            addons_list.append(dir)

    return addons_list


def git_update(workspace, project, branch_name=None, depth='1'):
    if not branch_name:
        branch_name = get_branch()

    cwd = "{}/{}".format(workspace, project)
    # Replace old scafolding with new one
    if project != 'odoo' and os.path.exists(project):
        linux.run([
            ['mkdir', '-p', 'tmp'],
            ['mv', project, 'tmp'],

            ['mkdir', '-p', workspace],
            ['mv', "tmp/{}".format(project), workspace],

            ['rm', 'tmp']
        ])

    if os.path.exists(cwd):
        linux.call_safe(['git', 'pull'], cwd=cwd)
        state = 'Created'
    else:
        linux.run([
            ['mkdir', '-p', workspace],
        ])
        result = linux.call_safe([
            'git',
            'clone',
            '--branch', branch_name,
            '--depth', depth,
            'git@github.com:' + workspace + '/' + project + '.git'
        ], cwd=workspace)
        if result == 0:
            state = 'Updated'
        else:
            state = 'Fail'
    return state


def get_list(filter_workspace=False):
    # To update repositories
    configs = json.loads(env.resource_string('config.json'))
    result = configs['repositories']
    if filter_workspace:
        result = [repo for repo in configs['repositories']
                  if repo['workspace'] in filter_workspace]
    return result


def get_branch():
    # To update repositories
    configs = json.loads(env.resource_string('config.json'))
    return configs['version']


def get_workspace():
    return env.get_workspace()
