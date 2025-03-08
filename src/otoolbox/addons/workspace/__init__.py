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
    resources = env.context.get("resources")
    resources.build()


@app.command()
def verify():
    """Verify all resources in the workspace"""
    # check if verification is performed by the system
    if env.context.get("pre_check", False) or env.context.get("post_check", False):
        return
    result, verified, total = utils.verify_all_resource(should_exit=False)
    if result:
        print(f"Verification fail (Verified: {verified}, Total:{total})")
    else:
        print("Success")


@app.command()
def delete():
    resources = env.context.get("resources")
    resources.destroy()


@app.command()
def update():
    """Updates current workspace to the latest version"""
    resources = env.context.get("resources")
    resources.update()


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
        constructors=[utils.makedir],
        destructors=[utils.delete_dir],
        validators=[utils.is_dir, utils.is_readable],
        tags=[RESOURCE_TAGS_AUTO_UPDATE],
    )
    env.add_resource(
        priority=RESOURCE_PRIORITY_ROOT,
        path=RESOURCE_ENV_FILE,
        title="Envirenments Variables",
        description="The environment variables file",
        constructors=[utils.touch],
        updates=[utils.set_to_env_all],
        destructors=[utils.delete_file],
        validators=[utils.is_file, utils.is_readable, utils.is_writable],
        tags=[RESOURCE_TAGS_ENV, RESOURCE_TAGS_AUTO_UPDATE],
    )


###################################################################
# Application entry point
# Launch application if called directly
###################################################################
if __name__ == "__main__":
    dotenv.load_dotenv()
    app()
