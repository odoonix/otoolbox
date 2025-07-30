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
from otoolbox.constants import (
    RESOURCE_PRIORITY_DEFAULT
)


###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "ubuntu"


@app.command(name="install")
def install():
    env.console.print("Run ./ubuntu-install-apps.sh in terminal.")

###################################################################
# init
###################################################################


def init():
    """Init the resources for the workspace"""
    env.add_resource(
        priority=RESOURCE_PRIORITY_DEFAULT,
        path=".bin",
        title="Workspace configuration directory",
        description="All configuration related to current workspace are located in this folder",
        init=[utils.makedir],
        destroy=[utils.delete_dir],
        verify=[utils.is_dir, utils.is_readable],
    )

    env.add_resource(
        priority=RESOURCE_PRIORITY_DEFAULT,
        path="ubuntu-install-apps.sh",
        title="Ubuntu application installer",
        description="Install all required application in ubuntu.",
        init=[
            utils.constructor_copy_resource("addons/ubuntu/ubuntu-install-apps.sh"),
            utils.chmod_executable,
            utils.touch_file
        ],
        updat=[
            utils.constructor_copy_resource("addons/ubuntu/ubuntu-install-apps.sh"),
            utils.chmod_executable,
            utils.touch_file
        ],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_executable],
    )

    # pipx install copier
    # pipx install pre-commit
    # pipx ensurepath

    env.add_resource(
        priority=RESOURCE_PRIORITY_DEFAULT,
        path="application://copier",
        title="Copier tool",
        description="Copier",
        init=[
            utils.pipx_install,
            utils.pipx_ensurepath
        ],
        update=[
            utils.pipx_update,
            utils.pipx_ensurepath
        ],
        destroy=[
            utils.pipx_remove
        ],
        verify=[
            utils.pipx_is_install,
            utils.pipx_ensurepath
        ],
        tags=['application', 'oca', 'maintainer']
    )

    env.add_resource(
        priority=RESOURCE_PRIORITY_DEFAULT,
        path="application://pre-commit",
        title="pre-commit tool",
        description="pre-commit",
        init=[
            utils.pipx_install,
            utils.pipx_ensurepath
        ],
        update=[
            utils.pipx_update,
            utils.pipx_ensurepath
        ],
        destroy=[
            utils.pipx_remove
        ],
        verify=[
            utils.pipx_is_install,
            utils.pipx_ensurepath
        ],
        tags=['application', 'oca', 'maintainer']
    )


###################################################################
# Application entry point
# Launch application if called directly
###################################################################
def _main():
    dotenv.load_dotenv()
    app()


if __name__ == "__main__":
    _main()
