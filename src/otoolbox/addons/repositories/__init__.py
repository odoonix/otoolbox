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
from typing import List
import re

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
from otoolbox.addons.repositories import config


###################################################################
# Utils
###################################################################


def extract_github_info(github_url):
    # Regular expression pattern for GitHub repository URL
    # Matches both SSH (git@github.com:org/repo.git) and HTTPS (https://github.com/org/repo.git) formats
    patterns = [
        r"(?:git@|https://)github\.com[:/](?P<organization>[A-Za-z0-9-]+)/(?P<repository>[A-Za-z0-9_-]+)(?:\.git)?$",
        r"^(?P<organization>[A-Za-z0-9-]+)/(?P<repository>[A-Za-z0-9_-]+)$",
    ]

    if not github_url:
        return None, None, "GitHub URL cannot be empty"
    # Try to match the pattern
    for pattern in patterns:
        match = re.match(pattern, github_url)

        if match:
            organization = match.group("organization")
            repository = match.group("repository")

            # Validate repository name according to Git repository naming rules
            # Repository names can contain letters, numbers, hyphens, underscores, and periods
            # Must not start or end with a period, must not contain consecutive periods
            repo_valid_pattern = (
                r"^[A-Za-z0-9](?:[A-Za-z0-9_-]*[A-Za-z0-9])?$|^[A-Za-z0-9]$"
            )

            if not re.match(repo_valid_pattern, repository):
                return None, None, "Invalid repository name"

            return organization, repository, None

    return None, None, "Invalid GitHub URL format"


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
    url: Annotated[str, typer.Argument(help="The repository URL.")] = None,
    organization: Annotated[
        str,
        typer.Option(help="organization."),
    ] = None,
    repository: Annotated[
        str,
        typer.Option(help="repository."),
    ] = None,
    branch: Annotated[
        str,
        typer.Option(help="branch."),
    ] = None,
    title: Annotated[
        str,
        typer.Option(help="title."),
    ] = None,
    description: Annotated[
        str,
        typer.Option(help="description."),
    ] = None,
    tags: Annotated[
        List[str],
        typer.Option(help="tags."),
    ] = None,
):
    """Add a new repository to the workspace"""
    if url:
        organization, repository, message = extract_github_info(url)
        if message:
            env.console.print(message)
            return

    if not repository or not organization:
        env.console.print("Repository and Organization name is required!!")
        return
    repository = repository.lower()
    organization = organization.lower()
    tags = tags if tags else []
    branch = branch if branch else env.context.get("odoo_version")
    config.add_repository(
        {
            "repository": repository,
            "organization": organization,
            "branch": branch,
            "title": title,
            "description": description,
            "tags": tags,
        }
    )
    utils.print_result(
        env.resources.filter(
            lambda resource: resource.path == f"{organization}/{repository}"
        )
        .executor(["init", "verify"])
        .execute()
    )
    utils.print_result(
        env.resources.filter(
            lambda resource: resource.path == "odoo-dev.code-workspace"
        )
        .executor(["update"])
        .execute()
    )


@app.command(name="remove")
def command_remove(
    repository: Annotated[str, typer.Argument(help="The repository URL.")] = None,
    organization: Annotated[
        str,
        typer.Option(help="organization."),
    ] = None,
    project: Annotated[
        str,
        typer.Option(help="project."),
    ] = None,
):
    """Remove a repository from workspace"""
    if repository:
        organization, project, message = extract_github_info(repository)
        if message:
            env.console.print(message)
            return

    if not project or not organization:
        env.console.print("Project and Organization name is required!!")
        return
    repository = repository.lower()
    organization = organization.lower()

    config.remove_repository(organization, project)
    utils.print_result(
        env.resources.filter(
            lambda resource: resource.path == f"{organization}/{project}"
        )
        .executor(["destroy"])
        .execute()
    )
    env.resources = env.resources - env.resources.filter(
        lambda resource: resource.path == f"{organization}/{project}"
    )
    utils.print_result(
        env.resources.filter(
            lambda resource: resource.path == "odoo-dev.code-workspace"
        )
        .executor(["update"])
        .execute()
    )


@app.command(name="merge")
def command_merge(
    repo_db: Annotated[
        str,
        typer.Option(
            prompt="The distination repository",
            help="The repository database."
        ),
    ] = None,
    repo: Annotated[
        str,
        typer.Option(
            prompt="The source repository",
            help="Project repository."),
    ] = None
):
    """Remove a repository from workspace"""
    env.context.update({
        "should_skip_auto_operations": True
    })
    config.merge_repository(repo_db, repo)


@app.command(name="init")
def command_init(
    repository: Annotated[str, typer.Argument(
        help="The repository URL or path.")] = None,
):
    """Inint a repository with precommit"""

    # TODO: maso, 2025: check if copier, pre-commit are installed
    # Clone this template and answer its questions
    # copier copy --UNSAFE https://github.com/OCA/oca-addons-repo-template.git some-repo
    organization, project, message = extract_github_info(repository)
    if message:
        env.console.print(message)
        return
    organization = organization.lower()
    project = project.lower()
    resource = env.resources[f"{organization}/{project}"]
    if not resource:
        env.console.print("Related resource not found.")
        return

    result = utils.call_process_safe(
        [
            "copier",
            "copy",
            "--UNSAFE",
            "https://github.com/OCA/oca-addons-repo-template.git",
            resource.path
        ],
        cwd=env.get_workspace(),
        timeout=60
    )

    if result.returncode != 0:
        env.console.print(result.stderr)
        return

    # Commit that
    # cd some-repo
    # git add .
    # pre-commit install
    utils.call_process_safe(
        [
            "pre-commit",
            "install",
        ],
        cwd=env.get_workspace_path(repository)
    )
    # pre-commit run -a
    # git commit -am 'Hello world 🖖'


@app.command(name="sync-shielded")
def command_sync_shielded(
    public_name: Annotated[
        str,
        typer.Option(
            prompt="The source organization",
            help="The source organization to copy from.",
            envvar="PUBLIC_ORGANIZATION",
        ),
    ] = None,
    shielded_name: Annotated[
        str,
        typer.Option(
            prompt="The target organization",
            help="The target organization name.",
            envvar="SHIELDED_ORGANIZATION"
        )
    ] = None
):
    """Copy from public to shielded organization and remove history of the git"""
    # rsync -av --delete --exclude '.git' "$source/" "$dist/"
    public_organization = env.resources.filter(
        lambda resource: resource.path == public_name
    )[0]
    shielded_organization = env.resources.filter(
        lambda resource: resource.path == shielded_name
    )[0]
    repo_list = env.resources.filter(
        lambda resource: resource.has_tag(RESOURCE_TAGS_GIT)
    ).filter(
        lambda resource: resource.parent == public_organization.path
    )
    for repo in repo_list:
        # 1. repo is not an organization
        # 2. repo is a git project in public_organization
        if repo.is_shielded:
            repo_name = repo.linked_shielded_repo or repo.path[len(repo.parent)+1:]
            result = utils.call_process_safe(
                [
                    "rsync",
                    "-a",
                    "-v",
                    "--delete",
                    "--exclude",
                    ".git",
                    repo.path + "/",
                    shielded_organization.path + "/" + repo_name + "/"
                ],
                cwd=env.get_workspace(),
                timeout=60
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
        init=[
            utils.constructor_copy_resource(
                RESOURCE_REPOSITORIES_PATH, packag_name=__name__
            )
        ],
        udpate=[],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
        tags=[]
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
