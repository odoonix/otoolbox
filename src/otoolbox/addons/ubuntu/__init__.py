"""Support tools to init and config Ubuntu workspace

Resources:
- .bin
"""

import os
import dotenv

import typer
from typing_extensions import Annotated

import otoolbox
from otoolbox import env
from otoolbox import utils
from otoolbox.constants import RESOURCE_PRIORITY_DEFAULT


LINUX_SCRIPTS = [
    "bulk-common",
    "bulk-add-repos",
    "bulk-clone-al",
    "bulk-commit",
    "bulk-init-tests",
    "bulk-pre-commit",
    "bulk-pull",
    "bulk-push-shielded",
    "bulk-push",
    "bulk-repo-init",
    "bulk-sync-shielded",
    "customer-common",
    "customer-config",
    "customer-init",
    "customer-update-submodule",
    "ubuntu-install-apps",
    "ubuntu-office-conf",
]

PIPX_APPLICATIONS = [
    "copier",
    "pre-commit",
]


###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "ubuntu"


@app.command(name="install")
def install():
    env.console.print("Run ./ubuntu-install-apps.sh in terminal.")



@app.command(name="init")
def init():
    env.console.print("Update working directory to the current workspace.")
    otoolbox.command_run(
        steps=["init", "update", "verify"],
        tags=["ubuntu"],
        ssh_auth=True,
    )

###################################################################
# init
###################################################################


def init():
    """Init the resources for the workspace"""
    env.add_resource(
        priority=RESOURCE_PRIORITY_DEFAULT,
        path=".venv/bin",
        title="Workspace binary tools directory",
        description="All binary tools related to the current workspace are located in this folder",
        destroy=[],
        init=[utils.makedir],
        verify=[utils.is_dir, utils.is_readable],
        tags=["ubuntu", "folder", ".venv/bin"],
    )


    for script in LINUX_SCRIPTS:
        env.add_resource(
            priority=RESOURCE_PRIORITY_DEFAULT,
            path=f".venv/bin/{script}",
            title=f"Ubuntu utility script {script}",
            description="Install all required application in ubuntu.",
            init=[
                utils.constructor_copy_resource(f"addons/ubuntu/bin/{script}"),
                utils.chmod_executable,
                utils.touch_file,
            ],
            updat=[
                utils.constructor_copy_resource(f"addons/ubuntu/{script}"),
                utils.chmod_executable,
                utils.touch_file,
            ],
            destroy=[utils.delete_file],
            verify=[utils.is_file, utils.is_executable],
            tags=["ubuntu", "tools", script],
        )

    for app in PIPX_APPLICATIONS:
        env.add_resource(
            priority=RESOURCE_PRIORITY_DEFAULT,
            path=f"application://{app}",
            title=f"{app} tool",
            description=f"{app} tool installed via pipx",
            init=[utils.pipx_install, utils.pipx_ensurepath],
            update=[utils.pipx_update, utils.pipx_ensurepath],
            destroy=[utils.pipx_remove],
            verify=[utils.pipx_is_install, utils.pipx_ensurepath],
            tags=["ubuntu", "tools", app],
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
