"""The **Maintainer** Python package offers CLI tools for automating package updates,
repository tracking, database management, and backups.

The **Maintainer** Python package is a powerful CLI utility designed to simplify the
workflows of software maintainers. It provides commands for automating essential
maintenance tasks, such as updating packages, tracking changes in repositories,
managing and inspecting databases, and creating backups. This tool helps ensure systems
remain up-to-date, secure, and efficient, while reducing manual overhead. Whether
managing single projects or complex multi-repository environments, the Maintainer
package offers a reliable and streamlined solution for maintenance operations.
"""

import dotenv
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


@app.command(name="info")
def command_info():
    """Display information about the workspace"""
    pass


@app.command(name="init")
def command_init(
    ssh_git: Annotated[
        bool,
        typer.Option(
            prompt="Use SSH for git clone?",
            help="Use SSH for git clone. By enabling SSH, ssh key must be added to the git server."
            "The default ssh key is used.",
            envvar="OTOOLBOX_SSH_GIT",
        ),
    ] = True,
):
    """Initialize all resources from addons into the current workspace"""
    env.context.update({"ssh_git": ssh_git})
    return (
        env.context.get("resources")
        .filter(lambda resource: resource.has_tag(RESOURCE_TAGS_GIT))
        .build()
    )


@app.command(name="update")
def command_update():
    """Updates current workspace to the latest version"""
    repo_list = env.context.get("resources").filter(
        lambda resource: resource.has_tag(RESOURCE_TAGS_GIT)).update()

    # Show informations
    for root_result, root_resource in repo_list:
        print("\nResource:", root_resource.title)
        for updates, resource in root_result:
            for result, update in updates:
                print(f"[{result}] {update.__name__}")


@app.command(name="list")
def command_list():
    """Print list of repositories"""
    table = Table(title="Repositories")
    table.add_column("Parent", justify="left", style="cyan", no_wrap=True)
    table.add_column("Title", justify="left", style="green", no_wrap=True)

    repo_list = env.context.get("resources").filter(
        lambda resource: resource.has_tag(RESOURCE_TAGS_GIT)
    )
    for repo in repo_list.resources:
        table.add_row(repo.parent, repo.title)

    console = Console()
    console.print(table)


@app.command(name="add")
def command_add(
    organization: str,
    project: str,
    branch: str,
    title: str = None,
    description: str = None,
    tags: str = None,
):
    """Add a new repository to the workspace"""
    return (
        env.context.get("resources")
        .filter(lambda resource: resource.has_tag(RESOURCE_TAGS_GIT))
        .build()
    )


@app.command(name="remove")
def command_remove(
    organization: str,
    project: str,
    branch: str,
    title: str = None,
    description: str = None,
    tags: str = None,
):
    """Add a new repository to the workspace"""
    return (
        env.context.get("resources")
        .filter(lambda resource: resource.has_tag(RESOURCE_TAGS_GIT))
        .build()
    )


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
        constructors=[
            utils.constructor_copy_resource(
                RESOURCE_REPOSITORIES_PATH, packag_name=__name__
            )
        ],
        destructors=[utils.delete_file],
        validators=[utils.is_file, utils.is_readable],
    )

    config.load_repos_resources()


###################################################################
# Application entry point
# Launch application if called directly
###################################################################
if __name__ == "__main__":
    dotenv.load_dotenv()
    app()
