"""Loads basics of the workspace

Resources:
- .

"""

import dotenv

import typer
from typing_extensions import Annotated

from otoolbox import env
from otoolbox import utils
from otoolbox.constants import (
    RESOURCE_PRIORITY_ROOT,
    RESOURCE_ENV_FILE,
    RESOURCE_ROOT,
    RESOURCE_TAGS_ENV,
    RESOURCE_TAGS_AUTO_UPDATE,
)


###################################################################
# cli
###################################################################
app = typer.Typer(pretty_exceptions_show_locals=False)
app.__cli_name__ = "workspace"


@app.command(name="init")
def command_init(
    ssh_git: Annotated[
        bool,
        typer.Option(
            prompt="Use SSH for git clone?",
            help="Use SSH for git clone. By enabling SSH, ssh key must be added to the git server."
            "The default ssh key is used.",
            envvar="OTOOLBOX_SSH_GIT",
        ),
    ] = True,
) -> None:
    """Initialize all resources from addons into the current workspace"""
    env.context.update({"ssh_git": ssh_git})

    utils.print_result(env.resources.executor(["init", "build", "verify"]).execute())


@app.command()
def verify():
    """Verify all resources in the workspace"""
    utils.print_result(
        env.resources.executor(["verify"]).execute(),
    )


@app.command()
def delete():
    """Delete all resources in the workspace"""
    utils.print_result(
        env.resources.executor(["destroy"]).execute(),
    )


@app.command()
def update():
    """Updates current workspace to the latest version"""
    utils.print_result(
        env.resources.executor(["update"]).execute(),
    )


###################################################################
# init
###################################################################
def init():
    """Init the resources for the workspace"""
    env.add_resource(
        priority=RESOURCE_PRIORITY_ROOT,
        path=RESOURCE_ROOT,
        title="Workspace directory",
        description="The current workspace directory",
        init=[utils.makedir],
        destroy=[utils.delete_dir],
        verify=[utils.is_dir, utils.is_readable],
        tags=[RESOURCE_TAGS_AUTO_UPDATE],
    )
    env.add_resource(
        priority=RESOURCE_PRIORITY_ROOT,
        path=RESOURCE_ENV_FILE,
        title="Envirenments Variables",
        description="The env variables file",
        constructors=[utils.touch],
        init=[utils.set_to_env_all],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable, utils.is_writable],
        tags=[RESOURCE_TAGS_ENV, RESOURCE_TAGS_AUTO_UPDATE],
    )


###################################################################
# Application entry point
# Launch application if called directly
###################################################################
if __name__ == "__main__":
    dotenv.load_dotenv()
    app()
