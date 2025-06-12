import os
import sys
from typing import List
import logging
import chevron

from otoolbox.constants import (
    RESOURCE_PRIORITY_DEFAULT,
    STEPS,
    STEP_INIT,
    PROCESS_FAIL,
)


_logger = logging.getLogger(__name__)


class ResourceExecutor:
    def __init__(self, resource, steps):
        self.resource = resource
        self.steps = steps

    def execute(self, **kargs):
        """Run processors by step"""
        processors = self.resource.get_processors(self.steps)
        for processor in processors:
            try:
                result, message = processor.run(**kargs)
            except Exception as ex:
                result = PROCESS_FAIL
                message = str(ex)
                _logger.error(
                    "Fail to execute the resource process %s, on the resource %s",
                    processor,
                    self.resource,
                )
            if result == PROCESS_FAIL:
                _logger.error(
                    "%s :process %s on the resource %s",
                    message,
                    processor,
                    self.resource,
                )
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
        return f"ResourceExecutor({self.resource.path}, {self.steps})"

    def __add__(self, other):
        if not isinstance(other, ResourceExecutor) or self.resource != other.resource:
            raise TypeError(f"Impossible to add {type(self)} to {type(other)}")
        return ResourceExecutor(self.resource, self.steps + other.steps)


class ResourceSetExecutor:
    def __init__(self, executors=None, resources=None, steps=[]):
        self.executors = []

        if resources is not None:
            self.executors = [
                ResourceExecutor(resource, steps) for resource in resources
            ]

        if executors is not None:
            self.executors = self.executors + executors

    def execute(self, **kargs):
        self.executors.sort(reverse=True, key=lambda x: x.resource.priority)
        for executor in self.executors:
            yield executor.execute(**kargs), executor

    def __add__(self, other):
        if isinstance(other, ResourceSetExecutor):
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

            return ResourceSetExecutor(executors=combiled_executors)

        raise TypeError("Can only add ResourceSetExecutor")


class ResourceProcessor:
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

    def __str__(self):
        return self.process.__name__


class Resource:
    """A resource of the working directory"""

    def __init__(self, **kargs):
        # Relations&ID
        self.path = kargs.get("path")
        self.parent = kargs.get("parent", None)
        self.branch = kargs.get("branch", None)
        self.origin_extensions = []
        self.priority = RESOURCE_PRIORITY_DEFAULT
        self.visible = True
        self.description = ""
        self.tags = [self.path]
        self.title = self.path
        self.processors = []
        self.env = kargs.get("env")
        self.enable_in_runtime = kargs.get("enable_in_runtime", True)
        self.is_shielded = kargs.get("is_shielded", False)
        self.linked_shielded_repo = kargs.get("linked_shielded_repo", None)
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
                processors = kargs[step]
                for processor in processors:
                    self.add_processor(processor, step=step)

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
        self.tags.append(self.path)
        self.title = self.origin_extensions[0].get("title", self.path)

    def add_processor(self, process, **kargs):
        """Add a processor to the resource"""
        self.processors.append(ResourceProcessor(self, process, **kargs))

    def get_processors(self, steps):
        """Get processors by step"""
        processors = []
        for processor in self.processors:
            if processor.step in steps:
                processors.append(processor)
        return processors

    def has_tag(self, *args):
        """Check if it has any tags from arguments.

        # git or github
        flag = resource.has_tag('git', 'github')

        """
        if not len(args):
            return True

        for arg in args:
            if arg in self.tags:
                return True
        return False

    def get_abs_path(self):
        """Gets abs path of the current resource"""
        return self.env.get_workspace_path(self.path)

    def __str__(self):
        template = (
            "{{#parent}}{{parent}} > {{/parent}}{{path}}[{{#tags}}{{.}},{{/tags}}]"
        )
        return chevron.render(template=template, data=self)


class ResourceSet:
    """A resource set"""

    def __init__(self, resources=None, parent=None):
        """Crates new instance of the resource set"""
        self.parent = parent
        self.resources = resources if isinstance(resources, List) else []
        self._update()

    def add(self, resource: Resource):
        """Adds new resource into the set"""
        self.resources.append(resource)
        self._update()
        return self

    def _update(self):
        self.resources = sorted(
            self.resources,
            key=lambda x: x.priority,
            reverse=False,
        )

    def get(self, path, default=False):
        """Find resource with the path"""
        for resource in self.resources:
            if resource.path == path:
                return resource
        return default

    def filter(self, filter_function):
        """Filter and create new instance of set"""
        resources = list(filter(filter_function, self.resources))
        return ResourceSet(resources=resources, parent=self)

    def executor(self, steps):
        """Create a new executor for steps"""
        return ResourceSetExecutor(resources=self, steps=steps)

    def __iter__(self):
        for resource in self.resources:
            yield resource

    def __add__(self, other):
        if isinstance(other, Resource):
            return self.add(other)

        if isinstance(other, ResourceSet):
            return ResourceSet(resources=self.resources + other.resources)

        raise NotImplementedError(
            f"Impossible to add {type(other)} to {type(ResourceSet)}"
        )

    def __sub__(self, other):
        if isinstance(other, ResourceSet):
            return ResourceSet(resources=list(set(self.resources) - set(other.resources)))
        raise NotImplementedError(
            f"Subtraction is not supportd for {type(other)} to {type(ResourceSet)}"
        )

    def __getitem__(self, indices):
        """Find resource with the path"""
        if isinstance(indices, str):
            for resource in self.resources:
                if resource.path == indices:
                    return resource
        else:
            return self.resources[indices]
        return None
