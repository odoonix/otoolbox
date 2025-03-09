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
