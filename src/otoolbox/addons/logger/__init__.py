"""Adds helps and documents

Resources:
- README.md

"""

import logging
import sys
import dotenv

import typer
from typing_extensions import Annotated
import dotenv

import typer
from typing_extensions import Annotated

from otoolbox import env
from otoolbox import utils

LOG_FILE = ".logs.txt"

###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "log"


@app.command(name="show")
def command_show():
    """Show latest logs"""
    path = env.get_workspace_path(LOG_FILE)
    with open(path, "r", encoding="UTF8") as file:
        for line in file:
            env.console.print(line, end="")


###################################################################
# init
###################################################################


def init():
    """Init the resources for the workspace"""
    env.add_resource(
        path=LOG_FILE,
        title="Default logging resource",
        description="Containes all logs from the sysem",
        init=[utils.touch_file],
        update=[utils.touch_file],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_writable],
        tags=["debug"],
    )

    # Logging
    file_handler = logging.FileHandler(filename=env.get_workspace_path(".logs.txt"))
    handlers = [file_handler]
    verbose = env.context.get("verbose")
    if verbose:
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        handlers.append(stdout_handler)

    logging.basicConfig(
        level=logging.INFO if verbose else logging.ERROR,
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=handlers,
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
