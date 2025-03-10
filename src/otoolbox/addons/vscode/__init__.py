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
import dotenv
import typer

from otoolbox import env
from otoolbox import utils

from otoolbox.addons.vscode import dev_env


###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "dev"


@app.command()
def start():
    """Check and start development tools.

    Our default development envirenment is based on docker and vscode. This command
    run vscode and docker if they are not running.
    """
    # # 1- load all repositories
    utils.call_process_safe(
        [
            "code",
            get_workspace_config_resourse(),
        ],
        cwd=env.get_workspace(),
    )


###################################################################
# init
###################################################################
def get_workspace_config_path():
    """Get the path of the workspace configuration file"""
    return env.get_workspace_path(get_workspace_config_resourse())


def get_workspace_config_resourse():
    """Get the resource name of the workspace configuration file"""
    return "odoo-dev.code-workspace"


###################################################################
# init
###################################################################
def init():
    """Init the resources for the workspace"""
    env.add_resource(
        path=get_workspace_config_resourse(),
        title="List of managed repositories",
        description="Adding, removing, and updating repositories in the workspace is "
        "done through this file",
        init=[
            utils.constructor_copy_resource("addons/vscode/workspace.json")
        ],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
        tags=["vscode"],
    )
    env.add_resource(
        path=".venv",
        title="Python vertual environment",
        description="Contlains all libs and tools",
        init=[dev_env.create],
        update=[],
        destroy=[utils.delete_dir],
        verify=[],
        tags=["vscode", "venv", "python"],
    )
    env.add_resource(
        path="requirements.txt",
        parent=".venv",
        title="Python vertual environment",
        description="Contlains all libs and tools",
        init=[utils.touch, dev_env.install],
        update=[dev_env.install],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
        tags=["vscode", "venv", "python"],
    )
    env.add_resource(
        path="requirements.txt",
        parent=".venv",
        title="Python vertual environment",
        description="Contlains all libs and tools",
        init=[utils.touch, dev_env.install],
        update=[dev_env.install],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
        tags=["vscode", "venv", "python"],
    )
    env.add_resource(
        path="odoo/odoo/requirements.txt",
        parent=".venv",
        title="Python vertual environment",
        description="Contlains all libs and tools",
        init=[utils.touch, dev_env.install],
        update=[dev_env.install],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
        tags=["vscode", "venv", "python"],
    )

###################################################################
# Application entry point
# Launch application if called directly
###################################################################


def _main():
    dotenv.load_dotenv(".env")
    app()


if __name__ == "__main__":
    _main()
