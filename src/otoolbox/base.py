import os
import sys

from otoolbox.constants import (
    RESOURCE_PRIORITY_DEFAULT
)


class WorkspaceResource():
    def __init__(
        self,
        path,
        parent=None,
        title=None,
        description=None,
        constructors=None,
        destructors=None,
        validators=None,
        updates=None,
        tags=None,
        priority=RESOURCE_PRIORITY_DEFAULT,
        visible=True,
    ):
        self.path = path
        self.parent = parent
        self.title = title
        self.description = description if description else []
        self.constructors = constructors if constructors else []
        self.destructors = destructors if destructors else []
        self.validators = validators if validators else []
        self.tags = tags if tags else []
        self.updates = updates if updates else []
        self.priority = priority
        self.visible = visible,

        # internals
        self.validation_errors = {}
        self.is_valied = False

    def build(self, **kargs):
        """Launch all build function"""
        for constructor in self.constructors:
            result = constructor(context=self, **kargs)
            yield result, constructor

    def destroy(self, **kargs):
        """Launch all destroy function"""
        for destructor in self.destructors:
            result = destructor(context=self, **kargs)
            yield result, destructor

    def verify(self, **kargs):
        """Launch all verifiy function"""
        for validator in self.validators:
            result = validator(context=self, **kargs)
            yield result, validator

    def update(self, **kargs):
        """Launch all updates function"""
        for update in self.updates:
            result = update(context=self, **kargs)
            yield result, update

    def get_validators_len(self):
        """Return the number of validators"""
        return len(self.validators)

    def set_validator_failed(self, validator, exception):
        self.validation_errors[validator] = exception

    def clean_validator_failer(self):
        self.validation_errors.clear()

    def has_tag(self, *args):
        """Check if it has any tags from arguments.

        # git or github
        flag = resource.has_tag('git', 'github')

        """
        for arg in args:
            if arg in self.tags:
                return True


class WorkspaceResourceGroup(WorkspaceResource):
    """Group of resources

    If there are many resources that are related to each other, it is possible to group them in a group.
    """

    def __init__(self,
                 path,
                 resources=None,
                 root=None,
                 **kargs):
        super().__init__(path, **kargs)
        self.resources = resources if resources else []
        self.validators_len = 0
        self.root = root

        # remove all non needed attributes
        self.validators = []
        self.updates = []
        self.constructors = []
        self.destructors = []

    def append(self, resource: WorkspaceResource):
        """Appends new resource to the group"""
        if self.root:
            raise RuntimeError("Imposible to modifie virtual resource")
        self.resources.append(resource)
        self.resources = sorted(self.resources, key=lambda x: x.priority, reverse=True)
        self.priority = self.resources[0].priority
        self.title = self.resources[0].title
        self.description = self.resources[0].description
        self.visible = self.resources[0].visible
        self.validators_len += resource.get_validators_len()

    def get(self, path, default=False):
        """Gets resources"""
        for resource in self.resources:
            if resource.path == path:
                return resource
        return default

    def build(self, **kargs):
        for resource in self.resources:
            result = resource.build(**kargs)
            yield result, resource
        result = super().build(**kargs)
        yield result, self

    def destroy(self, **kargs):
        for resource in self.resources:
            result = resource.destroy(**kargs)
            yield result, resource
        result = super().destroy(**kargs)
        yield result, self

    def verify(self, **kargs):
        for resource in self.resources:
            result = resource.verify(**kargs)
            yield result, resource
        result = super().verify(**kargs)
        yield result, self

    def update(self, **kargs):
        for resource in self.resources:
            updates = resource.update(**kargs)
            yield updates, resource
        updates = super().update(**kargs)
        yield updates, self

    def get_validators_len(self) -> int:
        return self.validators_len

    def has_tag(self, *args):
        for resource in self.resources:
            if resource.has_tag(*args):
                return True
        return super().has_tag(*args)

    def filter(self, filter_function):
        resources = list(filter(filter_function, self.resources))
        return WorkspaceResourceGroup(self.path, root=self, resources=resources)
