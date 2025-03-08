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
            constructor(context=self, **kargs)

    def destroy(self, **kargs):
        """Launch all destroy function"""
        for destructor in self.destructors:
            destructor(context=self, **kargs)

    def verify(self, continue_on_exception: bool = True, **kargs) -> int:
        """Launch all verifiy function"""
        verified = 0
        for validator in self.validators:
            try:
                validator(context=self, **kargs)
                verified += 1
            except BaseException as ex:
                if not continue_on_exception:
                    raise ex
                self.set_validator_failed(validator, ex)
        self.is_valied = verified == len(self.validators)
        return verified

    def update(self, **kargs):
        """Launch all updates function"""
        for update in self.updates:
            result = update(context=self, **kargs)
            yield result, update

    def get_validators_len(self):
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
            resource.build(**kargs)
        super().build(**kargs)

    def destroy(self, **kargs):
        for resource in self.resources:
            resource.destroy(**kargs)
        super().destroy(**kargs)

    def verify(self, **kargs):
        verified = 0
        for resource in self.resources:
            verified += resource.verify(**kargs)
        verified += super().verify(**kargs)
        return verified

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
