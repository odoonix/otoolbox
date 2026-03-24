import os

from otoolbox import env
from otoolbox.base import Resource
from otoolbox.constants import (
	PROCESS_EMPTY_MESSAGE,
	PROCESS_SUCCESS,
    PROCESS_FAIL,
	PROCESS_WAR,
	RESOURCE_TAGS_GIT,
	STEP_VERIFY,
)


def is_copilot_configured(context: Resource):
	"""Check if repository has .copilot-instructions.md."""
	file_path = env.get_workspace_path(context.path, ".copilot-instructions.md")
	if not os.path.isfile(file_path):
		return PROCESS_WAR, (
			f"File {file_path} doesn't exist or isn't readable"
		)
	if not os.access(file_path, os.R_OK):
		return PROCESS_FAIL, f"File {file_path} isn't readable"
	return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def init_verification_process():
	"""Attach copilot verification processor to all git resources."""
	repo_list = env.resources.filter(lambda resource: resource.has_tag(RESOURCE_TAGS_GIT))
	for resource in repo_list:
		resource.add_processor(
			process=is_copilot_configured,
			step=STEP_VERIFY,
			title="Verify copilot settings",
		)


def load_copilot_configuration_resource():
	"""Load repository-level copilot instruction files as resources."""
	repo_list = env.resources.filter(lambda resource: resource.has_tag(RESOURCE_TAGS_GIT))
	for resource in repo_list:
		file_relative_path = f"{resource.path}/.copilot-instructions.md"
		file_absolute_path = env.get_workspace_path(file_relative_path)
		if not os.path.isfile(file_absolute_path):
			continue

		env.add_resource(
			path=file_relative_path,
			parent=resource.path,
			title=f"Copilot instructions for {resource.path}",
			description="Repository-level copilot instructions.",
			verify=[],
			tags=["copilot", "instructions", "repository", resource.path],
		)

