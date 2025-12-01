"""Addons Management

Manage all addons as a resource

"""

import typer
from typing_extensions import Annotated
import dotenv
import csv

from typing import List

from otoolbox import env
from otoolbox import utils
from rich.console import Console
from rich.table import Table


from otoolbox.constants import (
    RESOURCE_PRIORITY_ROOT,
    RESOURCE_TAGS_GIT,
)

from . import config

###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "addons"


@app.command(name="list")
def addons_list(
    tags: Annotated[
        List[str],
        typer.Option(help="tags."),
    ] = None,
    csv_file: Annotated[
        str,
        typer.Option("--csv", help="CSV file name."),
    ] = None,
):
    """List all addons"""
    console = Console()
    console.print("List of addons")

    branch = env.context.get("odoo_version")
    tags = tags if tags else []
    addons_list = env.resources.filter(
        lambda resource: resource.has_tag("addon") and resource.has_tag(*tags)
    )

    # Console Table
    table = Table(title="Repositories")
    table.add_column("Organization", justify="left", style="cyan", no_wrap=True)
    table.add_column("Repository", justify="left", style="green", no_wrap=True)
    table.add_column("Technical Name", justify="left", style="green", no_wrap=True)
    table.add_column("Version", justify="left", style="green", no_wrap=True)
    table.add_column("Title", justify="left", style="green", no_wrap=True)
    for resource in addons_list:
        table.add_row(
            resource.organization,
            resource.repository,
            resource.name,
            resource.version,
            resource.title,
        )
    console.print(table)

    if csv_file:
        with open(
            f"db.module.template_{csv_file}.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["id", "name", "repository_url", "active"])
            for resource in addons_list:
                writer.writerow(
                    [
                        resource.name,
                        resource.name,
                        (
                            # resource.website or
                            f"https://github.com/{resource.organization}/{resource.repository}"
                        ),
                        1,
                    ]
                )
        with open(
            f"db.module.module{csv_file}.csv", "w", newline="", encoding="utf-8"
        ) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["id", "module_template_id/id", "version_id/id", "active"])
            for resource in addons_list:
                writer.writerow(
                    [
                        f"{resource.name}_{branch.replace(".", "_")}",
                        resource.name,
                        branch.replace(".", "_"),
                        1,
                    ]
                )


###################################################################
# init
###################################################################
def init():
    """Init the resources for the workspace"""
    # load all available addons
    config.load_addon_resources()


###################################################################
# Application entry point
# Launch application if called directly
###################################################################
def _main():
    dotenv.load_dotenv()
    app()


if __name__ == "__main__":
    _main()
