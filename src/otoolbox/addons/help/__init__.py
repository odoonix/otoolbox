"""Adds helps and documents

Resources:
- README.md

"""

import typer
import dotenv

from otoolbox import env
from otoolbox import utils
from otoolbox.constants import (
    RESOURCE_PRIORITY_ROOT,
    RESOURCE_ENV_FILE,
    RESOURCE_ROOT,
    RESOURCE_TAGS_DOCUMENTATION,
    RESOURCE_TAGS_AUTO_UPDATE,
    RESOURCE_TAGS_AUTO_VERIFY,
)

from otoolbox.addons.help import help_utils

###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "help"
app.__depends_on__ = ["workspace"]


###################################################################
# init
###################################################################
def init(addon):
    """Init the resources for the workspace"""
    env.add_resource(
        priority=RESOURCE_PRIORITY_ROOT,
        path="README.rst",
        title="Workspace README",
        description="A readme that shows parts of the workspace",
        init=[utils.touch_file, help_utils.update_readme],
        update=[utils.touch_file, help_utils.update_readme],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
        tags=[RESOURCE_TAGS_DOCUMENTATION, RESOURCE_TAGS_AUTO_UPDATE, RESOURCE_TAGS_AUTO_VERIFY],
    )


    env.add_resource(
        priority=RESOURCE_PRIORITY_ROOT,
        path="docs",
        parent=RESOURCE_ROOT,
        title="Documentation directory",
        description="The documentation directory",
        init=[utils.makedir],
        update=[utils.touch_dir],
        destroy=[utils.delete_dir],
        verify=[utils.is_dir, utils.is_readable, utils.is_writable],
        tags=[RESOURCE_TAGS_DOCUMENTATION, RESOURCE_TAGS_AUTO_UPDATE, RESOURCE_TAGS_AUTO_VERIFY],
    )

    docs_data_path = "addons/help/data/docs"
    for doc_file in env.list_resources(docs_data_path):
        env.add_resource(
            priority=RESOURCE_PRIORITY_ROOT,
            path=f"docs/{doc_file}",
            parent="docs",
            title=f"Documentation: {doc_file}",
            description=f"Documentation file: {doc_file}",
            init=[utils.constructor_copy_resource(f"{docs_data_path}/{doc_file}")],
            update=[utils.constructor_copy_resource(f"{docs_data_path}/{doc_file}")],
            destroy=[utils.delete_file],
            verify=[utils.is_file, utils.is_readable],
            tags=[RESOURCE_TAGS_DOCUMENTATION, RESOURCE_TAGS_AUTO_UPDATE, RESOURCE_TAGS_AUTO_VERIFY],
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
