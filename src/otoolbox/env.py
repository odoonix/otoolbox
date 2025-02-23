"""Envirnement fo the sysetm"""

# Standard
import os
import sys

# 3th party
import pkg_resources

# Odoo toolbox
from otoolbox.base import (
    WorkspaceResource,
    WorkspaceResourceGroup
)
from otoolbox.constants import (
    RESOURCE_PREFIX_VIRTUAL
)

VERSION = "0.1.0"
context = {
    'version': VERSION,
    'author': "Odoonix",
    'email': "info@odoonix.com",
    'website': "https://odoonix.com",
    'github': "https://githubs.com/odoonix",
    'resources': WorkspaceResourceGroup(
        path=RESOURCE_PREFIX_VIRTUAL,
        title="Root Resource",
        visible=False,
    )
}

# list of errors and warnings
errors = []


def resource_string(resource_name: str, packag_name: str = "otoolbox", encoding: str = "utf-8"):
    """Load resource"""
    return pkg_resources.resource_string(packag_name, resource_name).decode(encoding)


def resource_stream(resource_name: str, packag_name: str = "otoolbox"):
    """Load resource"""
    return pkg_resources.resource_stream(packag_name, resource_name)


def get_workspace():
    """Get the workspace"""
    return context.get("path", ".")


def get_workspace_path(path):
    """Gets subfolder/file with in workspace"""
    return os.path.join(get_workspace(), path)


#################################################################################
# Resource
#################################################################################
def add_resource(**kargs):
    """Add a resource to the workspace"""
    resource = WorkspaceResource(**kargs)
    path = kargs.get('path')
    group = context['resources'].get(path)
    if not group:
        group = WorkspaceResourceGroup(**kargs)
    group.append(resource)
    context['resources'].append(group)
    return sys.modules[__name__]
