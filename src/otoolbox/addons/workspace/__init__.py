"""Loads basics of the workspace

Resources:
- .

"""

import dotenv

import typer

from otoolbox import env
from otoolbox import utils
from otoolbox.constants import (
    RESOURCE_PRIORITY_ROOT,
    RESOURCE_ENV_FILE,
    RESOURCE_ROOT,
    RESOURCE_TAGS_ENV,
    RESOURCE_TAGS_AUTO_UPDATE,
    RESOURCE_TAGS_AUTO_VERIFY,
)


###################################################################
# cli
###################################################################
app = typer.Typer(pretty_exceptions_show_locals=False)
app.__cli_name__ = "workspace"

###################################################################
# init
###################################################################


def init(addon):
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
        path=".env~",
        parent=RESOURCE_ROOT,
        title="Envirenments Variables Template",
        description="The env variables file template",
        init=[
            utils.constructor_copy_resource("addons/workspace/data/env")
        ],
        update=[
            utils.constructor_copy_resource("addons/workspace/data/env")
        ],
        destroy=[utils.delete_file],
        verify=[
            utils.is_file, 
            utils.is_readable, 
            utils.is_writable,
        ],
        tags=[RESOURCE_TAGS_ENV, RESOURCE_TAGS_AUTO_UPDATE, RESOURCE_TAGS_AUTO_VERIFY],
    )
    env.add_resource(
        priority=RESOURCE_PRIORITY_ROOT,
        path=RESOURCE_ENV_FILE,
        parent=RESOURCE_ROOT,
        title="Envirenments Variables",
        description="The env variables file is a readonly file. Fill the file to "
        "controll the workspace behavior",
        init=[
            utils.touch_file,
            # .env is readonly file
        ],
        update=[
            # .env is readonly file
        ],
        destroy=[utils.delete_file],
        verify=[
            utils.is_file, 
            utils.is_readable, 
            utils.is_writable,
            # Checking Variables

        ],
        tags=[RESOURCE_TAGS_ENV, RESOURCE_TAGS_AUTO_UPDATE, RESOURCE_TAGS_AUTO_VERIFY],
    )
    env.add_resource(
        priority=RESOURCE_PRIORITY_ROOT,
        path=".github",
        parent=RESOURCE_ROOT,
        title="GitHub directory",
        description="The GitHub directory",
        init=[utils.makedir],
        update=[utils.touch_dir],
        destroy=[utils.delete_dir],
        verify=[utils.is_dir, utils.is_readable, utils.is_writable],
        tags=[RESOURCE_TAGS_ENV, RESOURCE_TAGS_AUTO_UPDATE, RESOURCE_TAGS_AUTO_VERIFY],
    )
    env.add_resource(
        priority=RESOURCE_PRIORITY_ROOT,
        path=".tmp",
        parent=RESOURCE_ROOT,
        title="Temporary directory",
        description="The temporary directory",
        init=[utils.makedir],
        update=[utils.touch_dir],
        destroy=[utils.delete_dir],
        verify=[utils.is_dir, utils.is_readable, utils.is_writable],
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
