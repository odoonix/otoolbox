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
        constructors=[utils.constructor_copy_resource("data/WORKSPACE_README.md")],
        destructors=[utils.delete_file],
        validators=[utils.is_file, utils.is_readable],
    )
