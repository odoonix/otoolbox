"""Adds helps and documents

Resources:
- README.md

"""
import typer
from typing_extensions import Annotated
import dotenv

import typer
from typing_extensions import Annotated

from otoolbox import env
from otoolbox import utils

###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "help"

###################################################################
# init
###################################################################
def init():
    """Init the resources for the workspace"""
    env.add_resource(
        path="README.md",
        title="Workspace README",
        description="A readme that shows parts of the workspace",
        init=[utils.constructor_copy_resource("addons/help/WORKSPACE_README.md")],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
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
