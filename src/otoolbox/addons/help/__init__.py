"""Adds helps and documents

Resources:
- README.md

"""

import typer
from typing_extensions import Annotated
import dotenv


from otoolbox import env
from otoolbox import utils

from otoolbox.addons.help import help_utils

###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "help"


###################################################################
# init
###################################################################
def init(addon):
    """Init the resources for the workspace"""
    env.add_resource(
        path="README.rst",
        title="Workspace README",
        description="A readme that shows parts of the workspace",
        init=[
            utils.touch_file,
            help_utils.update_readme
        ],
        update=[
            utils.touch_file,
            help_utils.update_readme
        ],
        destroy=[
            utils.delete_file
        ],
        verify=[
            utils.is_file, 
            utils.is_readable
        ],
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
