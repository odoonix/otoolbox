"""Adds helps and documents

Resources:
- README.md

"""

from otoolbox import env
from otoolbox import utils


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
