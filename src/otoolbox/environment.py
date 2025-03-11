"""Envirnement fo the sysetm"""

# Standard
import os
import sys

# 3th party
import pkg_resources
from rich.console import Console

# Odoo toolbox
from otoolbox.base import Resource, ResourceSet


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
        self, resource_name: str, packag_name: str = "otoolbox", encoding: str = "utf-8"
    ):
        """Load resource"""
        return pkg_resources.resource_string(packag_name, resource_name).decode(
            encoding
        )

    def resource_stream(self, resource_name: str, packag_name: str = "otoolbox"):
        """Load resource"""
        return pkg_resources.resource_stream(packag_name, resource_name)

    def get_workspace(self):
        """Get the workspace"""
        return self.context.get("path", ".")

    def get_workspace_path(self, path):
        """Gets subfolder/file with in workspace"""
        return os.path.join(self.get_workspace(), path)

    #################################################################################
    # Resource
    #################################################################################
    def add_resource(self, **kargs):
        """Add a resource to the workspace"""
        kargs.update({
            'env': self
        })
        resource = self.resources.get(kargs.get("path"))
        if not resource:
            resource = Resource(**kargs)
            self.resources.add(resource)
        else:
            resource.extend(**kargs)
        return sys.modules[__name__]


# Create the environment
env = Environment()
