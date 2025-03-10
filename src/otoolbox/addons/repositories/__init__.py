"""The **Maintainer** Python package offers CLI tools for automating package updates,
repository tracking, database management, and backups.

The **Maintainer** Python package is a powerful CLI utility designed to simplify the
workflows of software maintainers. It provides commands for automating essential
maintenance tasks, such as updating packages, tracking changes in repositories,
managing and inspecting databases, and creating backups. This tool helps ensure systems
remain up-to-date, secure, and efficient, while reducing manual overhead. Whether
managing single projects or complex multi-repository envs, the Maintainer
package offers a reliable and streamlined solution for maintenance operations.
"""
import os
import json
import dotenv
from typing import List
import typer
from typing_extensions import Annotated

from rich.console import Console
from rich.table import Table

from otoolbox import env
from otoolbox import utils
from otoolbox.constants import (
    RESOURCE_PRIORITY_ROOT,
    RESOURCE_TAGS_GIT,
)

from otoolbox.addons.repositories.constants import (
    REPOSITORIES_PATH,
    RESOURCE_REPOSITORIES_PATH,
)
import otoolbox.addons.repositories.config as config


###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "repo"


@app.command(name="list")
def command_list():
    """Print list of repositories"""
    table = Table(title="Repositories")
    table.add_column("Parent", justify="left", style="cyan", no_wrap=True)
    table.add_column("Title", justify="left", style="green", no_wrap=True)

    repo_list = env.resources.filter(
        lambda resource: resource.has_tag(RESOURCE_TAGS_GIT)
    )
    for repo in repo_list:
        table.add_row(repo.parent, repo.title)

    console = Console()
    console.print(table)


@app.command(name="add")
def command_add(
    organization: Annotated[
        str,
        typer.Option(
            prompt="organization?",
            help="organization."
        ),
    ],
    project: Annotated[
        str,
        typer.Option(
            prompt="project?",
            help="project."
        ),
    ],
    branch: Annotated[
        str,
        typer.Option(
            prompt="branch?",
            help="branch."
        ),
    ],
    title: Annotated[
        str,
        typer.Option(
            help="title."
        ),
    ] = None,
    description: Annotated[
        str,
        typer.Option(
            help="description."
        ),
    ] = None,
    tags: Annotated[
        List[str],
        typer.Option(
            help="tags."
        ),
    ] = None,
):
    """Add a new repository to the workspace"""
    new_repo = {
        'name': project,
        'workspace': organization,
        'branch': branch if branch else env.context.get('odoo_version'),
        'title': title,
        'description': description,
        'tags': tags if tags else []
    }
    reposiotires_path = env.get_workspace_path(REPOSITORIES_PATH)
    data = '[]'
    if os.path.isfile(reposiotires_path):
        with open(reposiotires_path, 'r', encoding="utf8") as f:
            data = f.read()
    repo_list = json.loads(data)
    repo_list.append(new_repo)

    with open(reposiotires_path, 'w', encoding="utf8") as f:
        f.write(json.dumps(repo_list))


@app.command(name="remove")
def command_remove(
    organization: Annotated[
        str,
        typer.Option(
            prompt="organization?",
            help="organization."
        ),
    ],
    project: Annotated[
        str,
        typer.Option(
            prompt="project?",
            help="project."
        ),
    ],
):
    reposiotires_path = env.get_workspace_path(REPOSITORIES_PATH)
    data = '[]'
    if os.path.isfile(reposiotires_path):
        with open(reposiotires_path, 'r', encoding="utf8") as f:
            data = f.read()
    repo_list = json.loads(data)

    new_list = [p for p in repo_list if p['name'] !=
                project or p['workspace'] != organization]

    with open(reposiotires_path, 'w', encoding="utf8") as f:
        f.write(json.dumps(new_list))


###################################################################
# init
###################################################################
def init():
    """Init the resources for the workspace"""
    env.add_resource(
        priority=RESOURCE_PRIORITY_ROOT,
        path=REPOSITORIES_PATH,
        title="List of managed repositories",
        description="Adding, removing, and updating repositories in the workspace is done through this file",
        init=[
            utils.constructor_copy_resource(
                RESOURCE_REPOSITORIES_PATH, packag_name=__name__
            )
        ],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
    )

    config.load_repos_resources()


###################################################################
# Application entry point
# Launch application if called directly
###################################################################
def _main():
    dotenv.load_dotenv(".env")
    app()


if __name__ == "__main__":
    _main()
