"""Otoolbox Copilot Addons

This addons is designe to manage all resources related to copilot.

"""

# import logging
# import sys
import dotenv

import typer
# from typing_extensions import Annotated

from otoolbox.constants import (
    LOG_FILE,
)
from otoolbox import env
from otoolbox import utils
from . import copilot_utils

AGENT_FOLDER = ".github/agents"

AGENT_FILES = [
    "Odoo_17_Backend.agent.md",
    "Odoo_18_Backend.agent.md",
    "Odoo_19_Backend.agent.md",
]

COPILOT_INSTRAUCTIONS_WORKSPACE = "workspace.md"
COPILOT_INSTRAUCTIONS_ODOONIX = "odoonix.md"

###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "copilot"


@app.command(name="list")
def command_show():
    """list all resources related to copilot"""
    path = env.get_workspace_path(LOG_FILE)
    with open(path, "r", encoding="UTF8") as file:
        for line in file:
            env.console.print(line, end="")


###################################################################
# init
###################################################################
def init(addon):
    """Init the resources for the workspace"""
    env.add_resource(
        path=AGENT_FOLDER,
        title="Folder for copilot agents",
        description="Contains all copilot agent files",
        init=[utils.makedir],
        update=[utils.touch_dir],
        destroy=[utils.delete_dir],
        verify=[utils.is_dir, utils.is_readable],
        tags=["copilot", "folder", "github"],
    )

    # add resourse for each agent file
    for agent_file in AGENT_FILES:
        env.add_resource(
            path=f"{AGENT_FOLDER}/{agent_file}",
            parent=AGENT_FOLDER,
            title=f"Copilot agent file: {agent_file}",
            description=f"Copilot agent file for {agent_file.split('.')[0]}",
            init=[
                utils.constructor_copy_resource(f"addons/copilot/agents/{agent_file}")
            ],
            update=[
                utils.touch_file,
                utils.constructor_copy_resource(f"addons/copilot/agents/{agent_file}"),
            ],
            destroy=[utils.delete_file],
            verify=[utils.is_file, utils.is_readable],
            tags=["copilot", "agent", "github", f"{AGENT_FOLDER}/{agent_file}"],
        )

    # add copilot instructions for workspace
    env.add_resource(
        path=".copilot-instructions.md",
        title="Copilot instructions for workspace",
        description="Instructions for using copilot in the workspace",
        init=[
            utils.constructor_copy_resource(
                f"addons/copilot/instructions/{COPILOT_INSTRAUCTIONS_WORKSPACE}"
            )
        ],
        update=[
            utils.touch_file,
            utils.constructor_copy_resource(
                f"addons/copilot/instructions/{COPILOT_INSTRAUCTIONS_WORKSPACE}"
            ),
        ],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
        tags=["copilot", "instructions", "workspace"],
    )

    # add copilot instructions for odoonix
    env.add_resource(
        path="odoonix/.copilot-instructions.md",
        title="Copilot instructions for ODOONIX",
        description="Instructions for using copilot in ODOONIX",
        init=[
            utils.constructor_copy_resource(
                f"addons/copilot/instructions/{COPILOT_INSTRAUCTIONS_ODOONIX}"
            )
        ],
        update=[
            utils.touch_file,
            utils.constructor_copy_resource(
                f"addons/copilot/instructions/{COPILOT_INSTRAUCTIONS_ODOONIX}"
            ),
        ],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
        tags=["copilot", "instructions", "odoonix"],
    )


def post_process(addon):
    copilot_utils.init_verification_process()
    copilot_utils.load_copilot_configuration_resource()


###################################################################
# Application entry point
# Launch application if called directly
###################################################################
def _main():
    dotenv.load_dotenv()
    app()


if __name__ == "__main__":
    _main()
