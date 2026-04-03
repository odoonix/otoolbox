"""Addons Management

Manage all addons as a resource

"""

import pkgutil

from importlib import import_module

import typer

# from typing_extensions import Annotated
import dotenv
# import csv

# from typing import List

# from otoolbox import env
# from otoolbox import utils
from rich.console import Console
# from rich.table import Table


# from otoolbox.constants import (
#     RESOURCE_PRIORITY_ROOT,
#     RESOURCE_TAGS_GIT,
# )

# from . import config

###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "extensions"


def _get_addon_dependencies(module_name):
    package = import_module(module_name)
    addon_app = getattr(package, "app", None)
    if not addon_app:
        return []
    depends_on = getattr(addon_app, "__depends_on__", [])
    return depends_on if isinstance(depends_on, list) else []


def _sort_addons_by_dependencies(modules):
    dependencies_by_module = {
        module_name: _get_addon_dependencies(module_name) for module_name in modules
    }
    module_by_alias = {}
    for module_name in modules:
        package = import_module(module_name)
        addon_app = getattr(package, "app", None)
        module_by_alias[module_name] = module_name
        module_by_alias[module_name.rsplit(".", 1)[-1]] = module_name
        cli_name = getattr(addon_app, "__cli_name__", None) if addon_app else None
        if cli_name:
            module_by_alias[cli_name] = module_name

    ordered_modules = []
    permanent_marks = set()
    temporary_marks = set()

    def visit(module_name):
        if module_name in permanent_marks:
            return
        if module_name in temporary_marks:
            raise RuntimeError(f"Cyclic addon dependency detected for {module_name}")

        temporary_marks.add(module_name)
        for dependency_name in dependencies_by_module.get(module_name, []):
            dependency_module = module_by_alias.get(dependency_name)
            if dependency_module and dependency_module in dependencies_by_module:
                visit(dependency_module)

        temporary_marks.remove(module_name)
        permanent_marks.add(module_name)
        if module_name not in ordered_modules:
            ordered_modules.append(module_name)

    for module_name in modules:
        visit(module_name)

    return ordered_modules


def get_all_addons():
    try:
        package_path = __path__
        package_name = __name__
        modules = []
        for module_info in pkgutil.iter_modules(package_path, package_name + "."):
            modules.append(module_info.name)
        return _sort_addons_by_dependencies(modules)
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
def addons_help():
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
