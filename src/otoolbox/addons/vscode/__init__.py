"""Adds resources to manage repositories

Resources:
- .otoolbox/repositoires.json

"""
from otoolbox import env
from otoolbox import utils


###################################################################
# init
###################################################################
def init():
    """Init the resources for the workspace
    """
    (env
        .add_resource(
            path="./odoo-{}.code-workspace".format(
                env.context.get("odoo_version", "18.0")),
            title="List of managed repositories",
            description="""Adding, removing, and updating repositories in the workspace is done through this file""",
            constructors=[
                utils.constructor_copy_resource("addons/vscode/data/workspace.json")
            ],
            destructors=[
                utils.delete_file
            ],
            validators=[
                utils.is_file,
                utils.is_readable
            ]
        )
     )
