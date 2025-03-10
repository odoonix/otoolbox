"""Adds helps and documents

Resources:
- README.md

"""

import logging
import sys

from otoolbox import env
from otoolbox import utils


###################################################################
# init
###################################################################
def init():
    """Init the resources for the workspace"""
    env.add_resource(
        path=".logs.txt",
        title="Default logging resource",
        description="Containes all logs from the sysem",
        init=[utils.touch_file],
        update=[utils.touch_file],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_writable],
        tags=['debug']
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
