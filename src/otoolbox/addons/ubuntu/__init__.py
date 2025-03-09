"""Support tools to init and config Ubuntu workspace

Resources:
- .bin
"""

import os

from otoolbox import env
from otoolbox import utils

###################################################################
# init
###################################################################


def init():
    """Init the resources for the workspace"""
    env.add_resource(
        priority=100,
        path=".bin",
        title="Workspace configuration directory",
        description="All configuration related to current workspace are located in this folder",
        init=[utils.makedir],
        destroy=[utils.delete_dir],
        verify=[utils.is_dir, utils.is_readable],
    )
