"""Load general CLI and tools related to odoo"""
import sys
import importlib
import typer
import chevron


from otoolbox import workspace
from otoolbox import developer
from otoolbox import repositories
from otoolbox import env
from otoolbox import utils

from otoolbox.constants import (

    ERROR_CODE_PRE_VERIFICATION,
    ERROR_CODE_POST_VERIFICATION

)


if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "otoolbox"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError


# def init_cli():
#     """Initialize the command-line interface for the Odoo Toolbox."""
#     arg_parser = argparse.ArgumentParser(
#         prog='odoo-util',
#         description="""
#             Odoonix Toolbox is a comprehensive suite of tools designed to streamline
#             the workflows of developers and maintainers working with Odoo. It
#             simplifies tasks such as tracking changes in addons, cloning
#             repositories, managing databases, and configuring development
#             environments. With its user-friendly interface and automation
#             features, Odoonix Toolbox enables teams to maintain consistency,
#             reduce manual effort, and speed up development cycles. By integrating
#             essential functionalities into one cohesive package, it empowers
#             developers to focus on creating and maintaining high-quality Odoo
#             solutions efficiently.
#         """,
#         epilog='Developer toolbox'
#     )

#     arg_parser.add_argument(
#         "--path",
#         help="""The workspace directory, default is current directory""",
#         action="store",
#         dest="path",
#         required=False,
#         default=".")

#     arg_parser.add_argument(
#         "--verbose",
#         help="""The workspace directory, default is current directory""",
#         action="count",
#         dest="verbose",
#         required=False,
#         default=0)

#     arg_parser.add_argument(
#         "--silent",
#         help="""Do not print extra information""",
#         action="count",
#         dest="silent",
#         required=False,
#         default=0)

#     return arg_parser, arg_parser.add_subparsers()


def _load_resources(*args):
    # Example usage
    for path in args:
        # Import the package dynamically
        package = importlib.import_module(path)
        # Check if the package has an __init__ method and call it if it exists
        if hasattr(package, 'init'):
            package.init()


def run():
    """Run the application"""
    _load_resources(
        'otoolbox.addons.help',
        'otoolbox.addons.workspace',
        'otoolbox.addons.ubuntu',
        'otoolbox.addons.vscode',
        'otoolbox.addons.repositories'
    )

    def callback_common_arguments(
            odoo: str = '18.0',
            path: str = '.',
            silent: bool = False,
            pre_check: bool = False,
            post_check: bool = False,
            continue_on_exception: bool = True
    ):
        env.context.update({
            'odoo_version': odoo,
            'path': path,
            'silent': silent,
            'pre_check': pre_check,
            'post_check': post_check,
            'continue_on_exception': continue_on_exception
        })
        if not silent:
            print(chevron.render(
                template=env.resource_string("data/banner.txt"),
                data=env.context
            ))
        if pre_check:
            utils.verify_all_resource()

    def result_callback(*args, **kargs):
        if env.context.get('post_check', False):
            utils.verify_all_resource()

    # Launch the CLI application
    app = typer.Typer(
        callback=callback_common_arguments,
        result_callback=result_callback,
        pretty_exceptions_show_locals=False
    )
    app.add_typer(workspace.app, name="workspace")
    app.add_typer(repositories.app, name="repo")
    app.add_typer(developer.app, name="dev")
    app()


if __name__ == '__main__':
    run()
