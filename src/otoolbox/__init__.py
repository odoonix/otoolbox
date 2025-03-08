"""Load general CLI and tools related to odoo"""

import sys
import importlib
from importlib.metadata import PackageNotFoundError, version
import chevron
import dotenv


import typer
from typing_extensions import Annotated


from otoolbox import env
from otoolbox import utils

from otoolbox.constants import (
    ERROR_CODE_PRE_VERIFICATION,
    ERROR_CODE_POST_VERIFICATION,
    RESOURCE_TAGS_AUTO_UPDATE,
    RESOURCE_TAGS_AUTO_VERIFY,
)
import otoolbox.addons as addons


try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "otoolbox"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError


###################################################################
# cli
###################################################################
# Launch the CLI application


def result_callback(*args, **kwargs):
    # Automatically update resources after the application is run
    env.context.get("resources").filter(
        lambda resource: resource.has_tag(RESOURCE_TAGS_AUTO_UPDATE)
    ).update()

    # Automatically verify resources after the application is run
    env.context.get("resources").filter(
        lambda resource: resource.has_tag(RESOURCE_TAGS_AUTO_VERIFY)
    ).verify()


app = typer.Typer(
    result_callback=result_callback,
    pretty_exceptions_show_locals=False,
    help="Odoonix Toolbox is a comprehensive suite of tools designed to streamline "
    "the workflows of developers and maintainers working with Odoo. It "
    "simplifies tasks such as tracking changes in addons, cloning "
    "repositories, managing databases, and configuring development "
    "environments. With its user-friendly interface and automation "
    "features, Odoonix Toolbox enables teams to maintain consistency, "
    "reduce manual effort, and speed up development cycles. By integrating "
    "essential functionalities into one cohesive package, it empowers "
    "developers to focus on creating and maintaining high-quality Odoo "
    "solutions efficiently.",
)


@app.callback()
def callback_common_arguments(
    odoo_version: Annotated[
        str,
        typer.Option(
            prompt="Wiche version of odoo?",
            help="The version of odoo to use.",
            envvar="ODOO_VERSION",
        ),
    ],
    silent: Annotated[
        bool,
        typer.Option(
            help="Do not show info more.",
            envvar="SILENT",
        ),
    ] = False,
    pre_check: Annotated[
        bool,
        typer.Option(
            help="Do not show info more.",
            envvar="PRE_CHECK",
        ),
    ] = False,
    post_check: Annotated[
        bool,
        typer.Option(
            help="Do not show info more.",
            envvar="POST_CHECK",
        ),
    ] = False,
    continue_on_exception: Annotated[
        bool,
        typer.Option(
            help="Do not show info more.",
            envvar="CONTINUE_ON_EXCEPTION",
        ),
    ] = True,
):
    env.context.update(
        {
            "odoo_version": odoo_version,
            "path": ".",
            "silent": silent,
            "pre_check": pre_check,
            "post_check": post_check,
            "continue_on_exception": continue_on_exception,
        }
    )
    if not silent:
        print(
            chevron.render(
                template=env.resource_string("data/banner.txt"), data=env.context
            )
        )
    if pre_check:
        utils.verify_all_resource()


@app.command(name="list")
def command_list():
    """
    List all available addons.
    """
    root = env.context.get("resources")
    for resource in root.resources:
        print(resource.path)


###################################################################
# Application entry point
# Launch application if called directly
###################################################################

def main():
    dotenv.load_dotenv(".env")
    addons_list = addons.get_all_addons()
    for addon in addons_list:
        package = importlib.import_module(addon)
        # Initialize the addon
        if hasattr(package, "init"):
            package.init()

        # Load the CLI for the addon
        if hasattr(package, "app"):
            app.add_typer(package.app, name=package.app.__cli_name__)

    # Load the application
    app()


if __name__ == "__main__":
    main()
