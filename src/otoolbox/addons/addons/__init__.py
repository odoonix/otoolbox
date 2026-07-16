"""Addons Management

Manage all addons as a resource

"""

import typer
from typing_extensions import Annotated
import dotenv
import csv

from typing import List

from otoolbox import env

from rich.console import Console
from rich.table import Table

from . import config


###################################################################
# Utils
###################################################################


def _export_addons_to_console(addons_list):
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

    console = Console()
    console.print("List of addons")
    console.print(table)


def _export_odoo_db_module_template(addons_list, csv_file):
    with open(
        f"db.module.template{csv_file}.csv", "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "name", "repository_id/id", "website", "active"])
        for resource in addons_list:
            writer.writerow(
                [
                    resource.name,
                    resource.name,
                    "db_repo_{organization}_{repository}".format(
                        organization=resource.organization,
                        repository=resource.repository,
                    ),
                    (
                        # resource.website or
                        f"https://github.com/{resource.organization}/{resource.repository}"
                    ),
                    1,
                ]
            )


def _export_odoo_db_module_module(addons_list, csv_file):
    branch = env.context.get("odoo_version")
    with open(
        f"db.module.module{csv_file}.csv", "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "module_template_id/id", "version_id/id", "active"])
        for resource in addons_list:
            writer.writerow(
                [
                    f"{resource.name}_{branch.replace('.', '_')}",
                    resource.name,
                    "vw_db_" + branch.replace(".", "_"),
                    1,
                ]
            )


def _export_odoo_db_module_module_version(addons_list, csv_file):
    branch = env.context.get("odoo_version")
    if branch == "19.0":
        pbranch = "18.0"
    if branch == "18.0":
        pbranch = "17.0"
    if branch == "17.0":
        pbranch = "16.0"
    with open(
        f"db.module.module{csv_file}_pre.csv", "w", newline="", encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "module_template_id/id", "version_id/id", "active"])
        for resource in addons_list:
            writer.writerow(
                [
                    f"{resource.name}_{pbranch.replace('.', '_')}",
                    resource.name,
                    "vw_db_" + pbranch.replace(".", "_"),
                    1,
                ]
            )


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
    tags = tags if tags else []
    addons_list = env.resources.filter(
        lambda resource: resource.has_tag("addon") and resource.has_tag(*tags)
    )

    # Console Table
    _export_addons_to_console(addons_list)

    if csv_file:
        _export_odoo_db_module_template(addons_list, csv_file)
        _export_odoo_db_module_module(addons_list, csv_file)
        _export_odoo_db_module_module(addons_list, csv_file)


###################################################################
# init
###################################################################
def init(*args, **kwargs):
    """Init the resources for the workspace"""
    # load all available addons
    config.load_addon_resources(*args, **kwargs)


###################################################################
# Application entry point
# Launch application if called directly
###################################################################
def _main():
    dotenv.load_dotenv()
    app()


if __name__ == "__main__":
    _main()
