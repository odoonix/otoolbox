"""Loads basics of the workspace

Resources:
- .

"""

import dotenv

import typer
from typing_extensions import Annotated

from otoolbox import env
from otoolbox import utils
from otoolbox.constants import (
    RESOURCE_PRIORITY_ROOT,
    RESOURCE_ENV_FILE,
    RESOURCE_ROOT,
    RESOURCE_TAGS_ENV,
    RESOURCE_TAGS_AUTO_UPDATE,
    RESOURCE_TAGS_AUTO_VERIFY
)


###################################################################
# cli
###################################################################
app = typer.Typer(pretty_exceptions_show_locals=False)
app.__cli_name__ = "workspace"

###################################################################
# init
###################################################################


def init():
    """Init the resources for the workspace"""
    env.add_resource(
        priority=RESOURCE_PRIORITY_ROOT,
        path=RESOURCE_ROOT,
        title="Workspace directory",
        description="The current workspace directory",
        init=[utils.makedir],
        destroy=[utils.delete_dir],
        verify=[utils.is_dir, utils.is_readable],
        tags=[RESOURCE_TAGS_AUTO_UPDATE, RESOURCE_TAGS_AUTO_VERIFY],
    )
    env.add_resource(
        priority=RESOURCE_PRIORITY_ROOT,
        path=RESOURCE_ENV_FILE,
        title="Envirenments Variables",
        description="The env variables file",
        init=[utils.touch_file, utils.set_to_env_all],
        update=[utils.set_to_env_all],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable, utils.is_writable],
        tags=[RESOURCE_TAGS_ENV, RESOURCE_TAGS_AUTO_UPDATE, RESOURCE_TAGS_AUTO_VERIFY],
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
