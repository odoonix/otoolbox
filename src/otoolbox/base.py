import os
import sys

from otoolbox.constants import RESOURCE_PRIORITY_DEFAULT

STEP_INIT = "init"
STEP_BUILD = "build"
STEP_DESTROY = "destroy"
STEP_VERIFY = "verify"
STEP_UPDATE = "update"
STEPS = [STEP_INIT, STEP_BUILD, STEP_DESTROY, STEP_VERIFY, STEP_UPDATE]


class WorkspaceResourceExecutor:
    def __init__(self, resource, steps):
        self.resource = resource
        self.steps = steps

    def execute(self, **kargs):
        for result, message, processor in self.resource.run_processors(self.steps, **kargs):
            yield result, message, processor

    def __eq__(self, other):
        return self.resource == other.resource

    def __ne__(self, other):
        return self.resource != other.resource

    def __gt__(self, other):
        return self.resource.priority > other.resource.priority

    def __lt__(self, other):
        return self.resource.priority < other.resource.priority

    def __str__(self):
        return f"WorkspaceResourceExecutor({self.resource.path}, {self.steps})"


class WorkspaceResourceSetExecutor:
    def __init__(self, executors=None, resources=None, steps=[]):
        self.executors = []

        if resources is not None:
            self.executors = [WorkspaceResourceExecutor(
                resource, steps) for resource in resources]

        if executors is not None:
            self.executors = self.executors + executors

    def execute(self, **kargs):
        for executor in self.executors:
            yield executor.execute(**kargs)

    def __add__(self, other):
        if isinstance(other, WorkspaceResourceSetExecutor):
            combiled_executors = []
            for executor in self.executors:
                if executor in other.executors:
                    executor_other = other.executors[other.executors.index(executor)]
                    combiled_executors.append(executor + executor_other)
                else:
                    combiled_executors.append(executor)
            for executor in other.executors:
                if executor not in self.executors:
                    combiled_executors.append(executor)

            return WorkspaceResourceSetExecutor(
                executors=combiled_executors
            )

        raise TypeError("Can only add WorkspaceResourceSetExecutor")


class WorkspaceResourceProcessor:
    """Processor for workspace resource

    This class is used to define a processor for a workspace resource.
    It is used to define a process that will be executed on the resource.
    It can be used to build, destroy, verify or update the resource.

    Each process executed on a resource at a specific step.
    The step can be used to define the order of execution of the processors.
    The steps are:
    - init: Initialization of the resource
    - build: Build the resource
    - destroy: Destroy the resource
    - verify: Verify the resource
    - update: Update the resource
    """

    def __init__(self, resource, process, step=STEP_INIT, title=None, description=None):
        self.title = title
        self.description = description

        self.step = step

        self.resource = resource
        self.process = process

    def run(self, **kargs):
        """Process the resource"""
        result, message = self.process(context=self.resource, **kargs)
        return result, message


class WorkspaceResource:
    def __init__(
        self,
        **kargs,
    ):
        # Relations&ID
        self.path = kargs.get("path")
        self.parent = kargs.get("parent", None)
        self.origin_extensions = []
        self.priority = RESOURCE_PRIORITY_DEFAULT
        self.visible = True
        self.description = ""
        self.tags = []
        self.title = self.path
        self.processors = []
        self.extend(**kargs)

    def extend(self, **kargs):
        """Extends the resource"""

        # Check path and parent
        path = kargs.get("path")
        if path != self.path:
            raise RuntimeError("Imposible to modifie path")
        parent = kargs.get("parent", None)
        if parent != self.parent:
            raise RuntimeError("Imposible to modifie parent")

        self.origin_extensions.append(kargs)
        self._update_properties()
        # Functions
        for step in STEPS:
            if step in kargs:
                self.add_processor(kargs[step], step=step)

    def _update_properties(self):
        self.origin_extensions = sorted(
            self.origin_extensions,
            key=lambda x: x.get("priority", RESOURCE_PRIORITY_DEFAULT),
            reverse=True,
        )
        self.priority = min(
            [
                extension.get("priority", RESOURCE_PRIORITY_DEFAULT)
                for extension in self.origin_extensions
            ]
        )
        self.visible = any(
            [extension.get("visible", True) for extension in self.origin_extensions]
        )
        self.description = "\n".join(
            [extension.get("description", "") for extension in self.origin_extensions]
        )
        self.tags = [
            tag
            for extension in self.origin_extensions
            for tag in extension.get("tags", [])
        ]
        self.title = self.origin_extensions[0].get("title", self.path)

    def add_processor(self, process, **kargs):
        """Add a processor to the resource"""
        self.processors.append(WorkspaceResourceProcessor(self, process, **kargs))

    def get_processors(self, steps):
        """Get processors by step"""
        processors = []
        for processor in self.processors:
            if processor.step in steps:
                processors.append(processor)
        return processors

    def run_processors(self, steps, **kargs):
        """Run processors by step"""
        for processor in self.get_processors(steps):
            result, message = processor.run(context=self, **kargs)
            yield result, message, processor

    def build(self, **kargs):
        """Launch all build function"""
        return self.run_processors(["build"], **kargs)

    def destroy(self, **kargs):
        """Launch all destroy function"""
        return self.run_processors(["build"], **kargs)

    def verify(self, **kargs):
        """Launch all verifiy function"""
        return self.run_processors(["build"], **kargs)

    def update(self, **kargs):
        """Launch all updates function"""
        return self.run_processors(["build"], **kargs)

    def has_tag(self, *args):
        """Check if it has any tags from arguments.

        # git or github
        flag = resource.has_tag('git', 'github')

        """
        for arg in args:
            if arg in self.tags:
                return True
        return False


class WorkspaceResourceSet:
    def __init__(self, resources=[], parent=None):
        self.parent = parent
        self.resources = resources

    def add(self, resource: WorkspaceResource):
        self.resources.append(resource)

    def get(self, path, default=False):
        for resource in self.resources:
            if resource.path == path:
                return resource
        return default

    def filter(self, filter_function):
        resources = list(filter(filter_function, self.resources))
        return WorkspaceResourceSet(resources=resources, parent=self)

    def executor(self, steps):
        return WorkspaceResourceSetExecutor(resources=self, steps=steps)

    def __iter__(self):
        for resource in self.resources:
            yield resource
