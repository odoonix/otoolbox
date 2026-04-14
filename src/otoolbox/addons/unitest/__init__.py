"""Support unitest addon for otoolbox.

Resources:

- conftest.py
- ODOO_TEST_FRAMEWORK_GUIDE.md
- pytest.ini


Tags: unitest

"""

import typer
import dotenv


from otoolbox import env
from otoolbox import utils
from otoolbox.constants import (
    RESOURCE_TAGS_DOCUMENTATION,
    RESOURCE_ROOT,
)
from otoolbox.addons.vscode import dev_env
from otoolbox.addons.unitest.unitest_utils import (
    add_python_testing_config,
    verify_python_testing_config,
)

###################################################################
# cli
###################################################################
app = typer.Typer()
app.__cli_name__ = "unitest"
app.__depends_on__ = ["vscode", "workspace"]


###################################################################
# init
###################################################################
def init(addon):
    """Init the resources for the workspace"""
    env.add_resource(
        path="docs/ODOO_TEST_FRAMEWORK_GUIDE.md",
        parent="docs",
        title="Guide for odoo test framework",
        description="""Guide for odoo test framework""",
        init=[
            utils.touch_file,
            utils.constructor_copy_resource(
                "addons/unitest/data/ODOO_TEST_FRAMEWORK_GUIDE.md"
            ),
        ],
        update=[
            utils.touch_file,
            utils.constructor_copy_resource(
                "addons/unitest/data/ODOO_TEST_FRAMEWORK_GUIDE.md"
            ),
        ],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
        tags=["unitest", RESOURCE_TAGS_DOCUMENTATION],
    )

    env.add_resource(
        path="conftest.py",
        parent=RESOURCE_ROOT,
        title="Conftest for odoo test framework",
        description="""Conftest for odoo test framework""",
        init=[
            utils.touch_file,
            utils.constructor_copy_resource("addons/unitest/data/conftest.py"),
        ],
        update=[
            utils.touch_file,
            utils.constructor_copy_resource("addons/unitest/data/conftest.py"),
        ],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
        tags=["unitest"],
    )

    env.add_resource(
        path="pytest.ini",
        parent=RESOURCE_ROOT,
        title="Pytest configuration for odoo test framework",
        description="""Pytest configuration for odoo test framework""",
        init=[
            utils.touch_file,
            utils.constructor_copy_resource("addons/unitest/data/pytest.ini"),
        ],
        update=[
            utils.touch_file,
            utils.constructor_copy_resource("addons/unitest/data/pytest.ini"),
        ],
        destroy=[utils.delete_file],
        verify=[utils.is_file, utils.is_readable],
        tags=["unitest"],
    )

    # Add more funciton to workspace
    env.add_resource(
        path="odoo-dev.code-workspace",
        init=[
            add_python_testing_config,
        ],
        update=[
            add_python_testing_config,
        ],
        verify=[
            verify_python_testing_config,
        ],
        tags=["unitest"],
    )

    env.add_resource(
        path="requirements.txt",
        init=[
            utils.touch_file,
            utils.constructor_add_text_line("pytest"),
            utils.constructor_add_text_line("pytest-cov"),
            dev_env.pyenv_install,
        ],
        update=[
            utils.touch_file,
            utils.constructor_add_text_line("pytest"),
            utils.constructor_add_text_line("pytest-cov"),
            dev_env.pyenv_install,
        ],
        verify=[
            utils.constructor_contains_text("pytest"),
            utils.constructor_contains_text("pytest-cov"),
        ],
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
