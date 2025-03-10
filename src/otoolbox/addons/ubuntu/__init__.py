"""Support tools to init and config Ubuntu workspace

Resources:
- .bin
"""

import os
import dotenv

import typer
from typing_extensions import Annotated

from otoolbox import env
from otoolbox import utils

###################################################################
# cli
###################################################################
app = typer.Typer(pretty_exceptions_show_locals=False)
app.__cli_name__ = "ubuntu"

###################################################################
# init
###################################################################


def init():
    """Init the resources for the workspace"""
    env.add_resource(
        priority=100,
        path=".bin",
        title="Workspace configuration directory",
        description="All configuration related to current workspace are located in this folder",
        init=[utils.makedir],
        destroy=[utils.delete_dir],
        verify=[utils.is_dir, utils.is_readable],
    )

###################################################################
# Application entry point
# Launch application if called directly
###################################################################


def _main():
    dotenv.load_dotenv(".env")
    app()


if __name__ == "__main__":
    _main()
