"""Supports basic operation related to workspase"""
import typer
from otoolbox import env
from otoolbox import utils


app = typer.Typer(
    pretty_exceptions_show_locals=False
)


@app.command()
def init():
    """Initialize all resources from addons into the current workspace"""
    resources = env.context.get('resources')
    resources.build()


@app.command()
def verify():
    """Verify all resources in the workspace which are created by the otoolbox."""
    # check if verification is performed by the system
    if env.context.get('pre_check', False) or env.context.get('post_check', False):
        return
    result, verified, total = utils.verify_all_resource(should_exit=False)
    if result:
        print(f"Verification fail (Verified: {verified}, Total:{total})")
    else:
        print("Success")


@app.command()
def delete():
    """Delete all resources from the workspace.
    
    This command will delete all resources from the workspace. Folder, files and
    other resources will be deleted if they are created by the otoolbox. Other
    resources will not be deleted.
    
    Some resources may not be deleted if they are not created by the otoolbox, or if
    they are not empty."""
    resources = env.context.get('resources')
    resources.destroy()


@app.command()
def info():
    """Display information about the workspace"""
    # TODO: maso, 2025: add info command
    #
    # Info command displayes information about the current workspace such as
    # - version
    # - creation time
    # - last update time
    # - acvite moduals
    #
    pass

@app.command()
def update():
    """Updates current workspace to the latest version"""
    resources = env.context.get('resources')
    resources.update()


# def init_cli(parent_parser):
#     """Init CLI to support maintainer tools
#     """
#     init_parseer = parent_parser.add_parser(
#         'init',
#         description="""
#             Tools and Utilites to help developers and maintainers. It makes simple to
#             keep dev repositories up to date.
#         """)
#     init_parseer.set_defaults(func=_init_resources)

#     init_parseer.add_argument(
#         '--odoo',
#         dest='odoo_version',
#         action='store',
#         default="18.0",
#         required=False
#     )

#     delete_parseer = parent_parser.add_parser(
#         'delete',
#         description="""
#             Delete resources.
#         """)
#     delete_parseer.set_defaults(func=_delete_resources)

#     return parent_parser


def run():
    """Run the application"""
    app()


# Launch application if called directly
if __name__ == "__main__":
    run()
