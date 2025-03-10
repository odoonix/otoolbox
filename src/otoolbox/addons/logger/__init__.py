"""Adds helps and documents

Resources:
- README.md

"""

import logging
import sys
import dotenv

import typer
from typing_extensions import Annotated

from otoolbox import env
from otoolbox import utils


###################################################################
# cli
###################################################################
app = typer.Typer(pretty_exceptions_show_locals=False)
app.__cli_name__ = "log"

###################################################################
# init
###################################################################


def init():
    """Init the resources for the workspace"""
    env.add_resource(
        path=".logs.txt",
        title="Default logging resource",
        description="Containes all logs from the sysem",
        init=[utils.touch],
        update=[utils.touch],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_writable],
        tags=['debug']
    )

    # Logging
    file_handler = logging.FileHandler(filename=env.get_workspace_path(".logs.txt"))
    handlers = [file_handler]
    if env.context.get("verbose"):
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        handlers.append(stdout_handler)

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=handlers,
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
