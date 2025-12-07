"""Addons Management

Manage all addons as a resource

"""
import pkgutil

from importlib import (
    import_module
)

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

# from . import config

###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "extensions"


def get_all_addons():
    try:
        package_path = __path__
        package_name = __name__
        modules = []
        for module_info in pkgutil.iter_modules(package_path, package_name + "."):
            modules.append(module_info.name)
        return modules
    except AttributeError:
        return []  # Not a packag


@app.command(name="list")
def addons_list():
    """List all extensions"""
    console = Console()
    console.print("List of addons")

    extensions = get_all_addons()
    for extension in extensions:
        console.print(extension)


@app.command(name="help")
def addons_list():
    """List all extensions"""
    console = Console()
    console.print("List of addons")

    extensions = get_all_addons()
    for extension in extensions:
        package = import_module(extension)
        # Print module docstring if exists
        doc = package.__doc__
        if doc:
            console.print(doc.strip())
        else:
            console.print("No docstring found for module.")


###################################################################
# init
###################################################################
def init():
    """Init the resources for the workspace"""
    # load all available addons
    # config.load_addon_resources()
    pass


###################################################################
# Application entry point
# Launch application if called directly
###################################################################
def _main():
    dotenv.load_dotenv()
    app()


if __name__ == "__main__":
    _main()
