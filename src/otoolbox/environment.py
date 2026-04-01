"""Envirnement fo the sysetm"""

# Standard
import os
import sys

# 3th party
from importlib.resources import files
from rich.console import Console

# Odoo toolbox
from otoolbox.base import Resource, ResourceSet
from otoolbox.constants import MANIFEST_NAMES


class Environment:
    """Environment for the system"""

    def __init__(self):
        self.context = {
            "author": "Odoonix",
            "email": "info@odoonix.com",
            "website": "https://odoonix.com",
            "github": "https://githubs.com/odoonix",
        }
        self.resources = ResourceSet()
        self.errors = []
        self.console = Console()

    def resource_string(
        self,
        resource_name: str,
        package_name: str = "otoolbox",
        encoding: str = "utf-8",
    ):
        """Load resource"""
        text = files(package_name).joinpath(resource_name).read_text(encoding=encoding)
        return text

    def resource_stream(self, resource_name: str, package_name: str = "otoolbox"):
        """Load resource"""
        # return pkg_resources.resource_stream(package_name, resource_name)
        return files(package_name).joinpath(resource_name).open("rb")

    def get_workspace(self):
        """Get the workspace"""
        return self.context.get("path", ".")

    def get_workspace_path(self, *path):
        """Gets subfolder/file with in workspace"""
        assert path, "Path is requried"
        return os.path.join(self.get_workspace(), *path)

    #################################################################################
    # Resource
    #################################################################################
    def add_resource(self, **kargs):
        """Add a resource to the workspace"""
        kargs.update({"env": self})
        resource = self.resources.get(kargs.get("path"))
        if not resource:
            resource = Resource(**kargs)
            self.resources.add(resource)
        else:
            resource.extend(**kargs)
        return sys.modules[__name__]

    def is_addons_path(self, resource):
        assert isinstance(resource, Resource)
        path = self.get_workspace_path(resource.path)
        if not os.path.isdir(path):
            return False
        for f in os.listdir(path):
            modpath = os.path.join(path, f)
            if os.path.isdir(modpath):

                def hasfile(filename):
                    return os.path.isfile(os.path.join(modpath, filename))

                if hasfile("__init__.py") and any(
                    hasfile(mname) for mname in MANIFEST_NAMES
                ):
                    return True
        return False


# Create the environment
env = Environment()
