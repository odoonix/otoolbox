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
import typer
from rich.console import Console
from rich.table import Table

from otoolbox import env
# from otoolbox.repositories import admin


app = typer.Typer()


def _filter_resources():
    resources = (
        env.context
        .get('resources')
        .filter(lambda resource: resource.has_tag('git'))
    )
    return resources


@app.command()
def info():
    """Display information about the workspace"""
    pass


@app.command()
def init(ssh_git: bool = False):
    """Initialize all resources from addons into the current workspace"""
    env.context.update({
        'ssh_git': ssh_git
    })
    return _filter_resources().build()


@app.command()
def update():
    """Updates current workspace to the latest version"""
    return _filter_resources().update()


@app.command(name="list")
def list_repo():
    """Print list of repositories"""
    table = Table(title="Repositories")
    table.add_column("Parent", justify="left", style="cyan", no_wrap=True)
    table.add_column("Title", justify="left", style="green", no_wrap=True)

    repo_list = _filter_resources()
    for repo in repo_list.resources:
        table.add_row(repo.parent, repo.title)

    console = Console()
    console.print(table)


@app.command()
def add(organization: str, project: str, branch: str, title: str = None, description: str = None, tags: str = None):
    """Add a new repository to the workspace"""
    return _filter_resources().build()


# def add_repo_list_filter(parser):
#     parser.add_argument(
#         '--oca',
#         default=False,
#         action='store_true')
#     parser.add_argument(
#         '--no-oca',
#         dest='python',
#         action='store_false')

#     parser.add_argument(
#         '--viraweb123',
#         default=False,
#         action='store_true')
#     parser.add_argument(
#         '--no-viraweb123',
#         dest='python',
#         action='store_false')

#     parser.add_argument(
#         '--moonsunsoft',
#         default=False,
#         action='store_true')
#     parser.add_argument(
#         '--no-moonsunsoft',
#         dest='python',
#         action='store_false')

# def init_cli(parent_parser):
#     """Init CLI to support maintainer tools
#     """
#     admin_parseer = parent_parser.add_parser('admin',)
#     admin_subparser = admin_parseer.add_subparsers(
#         title="Administrator Tools",
#         description="""
#             Tools and Utilites to help administrators. It makes simple to
#             keep dev repositories up to date.
#         """)

#     # dev update
#     dev_update = admin_subparser.add_parser(
#         'update',
#         description="Update packages")
#     dev_update.set_defaults(func=admin.update_repositories)
#     common.add_repo_list_filter(dev_update)

#     # admin info
#     dev_info = admin_subparser.add_parser(
#         'info',
#         description="List packages")
#     dev_info.set_defaults(func=admin.show_repositories)
#     common.add_repo_list_filter(dev_info)

#     return admin_parseer


def run():
    """Run the application"""
    app()


if __name__ == "__main__":
    run()
