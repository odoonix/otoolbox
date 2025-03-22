"""The **Developer** module in Odoonix Toolbox streamlines DevOps processes for Odoo
developers by automating tasks, managing envs, and simplifying workflows.

The **Developer** module in the Odoonix Toolbox is a specialized tool designed to
streamline the DevOps processes for Odoo developers. It provides utilities for
automating repetitive tasks, managing development envs, and simplifying
workflows. With features such as addon management, env configuration,
database handling, and integration tools, the Developer module empowers developers
to focus on coding and innovation rather than setup and maintenance. This module
bridges the gap between development and operations, enhancing productivity and
ensuring a seamless development experience in Odoo projects.
"""

import subprocess
import dotenv

import typer
from typing_extensions import Annotated

from otoolbox import env
from otoolbox import utils
from otoolbox.constants import RESOURCE_PRIORITY_ROOT, RESOURCE_PRIORITY_DEFAULT

from otoolbox.addons.vscode import dev_env
from otoolbox.addons.vscode import code_cof


###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "dev"


@app.command(name="start")
def command_start():
    """Check and start development tools.

    Our default development envirenment is based on docker and vscode. This command
    run vscode and docker if they are not running.
    """
    # # 1- load all repositories
    subprocess.run(
        [
            "code",
            env.get_workspace_path("odoo-dev.code-workspace"),
        ],
        cwd=env.get_workspace(),
        check=False,
    )


###################################################################
# init
###################################################################
def init():
    """Init the resources for the workspace"""
    env.context.update({"venv_path": ".venv"})

    env.add_resource(
        path="odoo-dev.code-workspace",
        title="List of managed repositories",
        description="Adding, removing, and updating repositories in the workspace is "
        "done through this file",
        init=[
            utils.constructor_copy_resource("addons/vscode/workspace.json"),
            code_cof.set_workspace_conf_odoo_addons,
            code_cof.rebuile_folder_config
        ],
        update=[
            code_cof.set_workspace_conf_odoo_addons,
            code_cof.rebuile_folder_config
        ],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
        tags=["vscode"],
    )

    env.add_resource(
        path=".venv",
        title="Python Virtual Environment",
        description="This environment is used to install dev tools.",
        init=[dev_env.pyenv_create],
        update=[utils.touch_dir],
        destroy=[utils.delete_dir],
        verify=[utils.is_dir, utils.is_readable],
        tags=["vscode", "python", "venv"],
        priority=RESOURCE_PRIORITY_ROOT,
    )

    env.add_resource(
        path="odoo/odoo/requirements.txt",
        parent="odoo/odoo",
        title="Odoo dependencies",
        description="Libs required in development or runtime environment.",
        init=[dev_env.pyenv_install],
        update=[dev_env.pyenv_install],
        destroy=[],
        verify=[utils.is_file, utils.is_readable],
        tags=["vscode", "python", "venv"],
        priority=RESOURCE_PRIORITY_DEFAULT,
    )

    env.add_resource(
        path="requirements.txt",
        parent=".",
        title="Custom dependencies",
        description="Libs required in development environemnt.",
        init=[utils.touch_file, dev_env.pyenv_install],
        update=[utils.touch_file, dev_env.pyenv_install],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
        tags=["vscode", "python", "venv"],
        priority=RESOURCE_PRIORITY_DEFAULT,
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
