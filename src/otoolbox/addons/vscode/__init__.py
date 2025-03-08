"""The **Developer** module in Odoonix Toolbox streamlines DevOps processes for Odoo
developers by automating tasks, managing environments, and simplifying workflows.

The **Developer** module in the Odoonix Toolbox is a specialized tool designed to
streamline the DevOps processes for Odoo developers. It provides utilities for
automating repetitive tasks, managing development environments, and simplifying
workflows. With features such as addon management, environment configuration,
database handling, and integration tools, the Developer module empowers developers
to focus on coding and innovation rather than setup and maintenance. This module
bridges the gap between development and operations, enhancing productivity and
ensuring a seamless development experience in Odoo projects.
"""
import dotenv
import typer

from otoolbox import env
from otoolbox import utils


###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "dev"


@app.command(name="init")
def command_init():
    """
    Initialize the development environment.

    It install and init .venv to the workspace. It also install all required
    tools for the development environment. All odoo dependencies are installed
    in the .venv.


    """
    utils.call_process_safe(
        [
            "python3",
            "-m",
            "venv",
            env.get_workspace_path(".venv"),
        ],
        cwd=env.get_workspace(),
    )

    utils.run_command_in_venv(
        env.get_workspace_path(".venv"),
        [
            "python",
            "-m",
            "pip",
            "install",
            "-r",
            env.get_workspace_path("odoo/odoo/requirements.txt"),
        ],
        cwd=env.get_workspace(),
    )

    # TODO: check if need to update settings
    pass


@app.command()
def start():
    """Check and start development tools.

    Our default development envirenment is based on docker and vscode. This command
    run vscode and docker if they are not running.

    """
    # # 1- load all repositories
    # admin.update_repositories(**kargs)

    result = utils.call_process_safe(
        [
            "code",
            get_workspace_config_resourse(),
        ],
        cwd=env.get_workspace(),
    )

    pass


###################################################################
# init
###################################################################
def get_workspace_config_path():
    """Get the path of the workspace configuration file"""
    return env.get_workspace_path(get_workspace_config_resourse())


def get_workspace_config_resourse():
    """Get the resource name of the workspace configuration file"""
    return "./odoo-dev.code-workspace"


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
        constructors=[
            utils.constructor_copy_resource("addons/vscode/data/workspace.json")
        ],
        destructors=[utils.delete_file],
        validators=[utils.is_file, utils.is_readable],
        tags=["vscode"],
    )


###################################################################
# Application entry point
# Launch application if called directly
###################################################################
if __name__ == "__main__":
    dotenv.load_dotenv()
    app()
