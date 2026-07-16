from rich.console import Console
from rich.table import Table


def export_console_table(repo_list):
    table = Table(title="Repositories")
    table.add_column("Parent", justify="left", style="cyan", no_wrap=True)
    table.add_column("Title", justify="left", style="green", no_wrap=True)
    table.add_column("Mirror", justify="left", style="green", no_wrap=True)
    table.add_column("Tags", justify="left", style="green", no_wrap=True)

    for repo in repo_list:
        table.add_row(
            repo.parent,
            repo.title,
            "{repository}/{organization}".format(
                repository=repo.linked_shielded_repository,
                organization=repo.linked_shielded_organization,
            )
            if repo.has_mirror
            else "N/A",
            ", ".join([str(tag) for tag in repo.tags]),
        )

    console = Console()
    console.print(table)


def export_console_list(repo_list):
    console = Console()
    for repo in repo_list:
        console.print(
            "{organization}/{repository}".format(
                repository=repo.title,
                organization=repo.parent,
            )
        )
