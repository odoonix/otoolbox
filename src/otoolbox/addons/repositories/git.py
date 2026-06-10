import logging
import subprocess
import os
import shutil
import uuid
from pathlib import Path

from otoolbox import env
from otoolbox import utils
from otoolbox.base import Resource
from otoolbox.constants import PROCESS_SUCCESS, PROCESS_FAIL, PROCESS_EMPTY_MESSAGE
from otoolbox.addons.repositories.constants import (
    GIT_ADDRESS_HTTPS,
    GIT_ADDRESS_SSH,
    GIT_ERROR_TABLE,
    GIT_COMMAND,
)

_logger = logging.getLogger(__name__)


######################################################################################
#                                Git Utilities                                       #
#                                                                                    #
#                                                                                    #
######################################################################################


def _rais_git_error(context, error_code):
    if not error_code:
        return
    error = GIT_ERROR_TABLE.get(
        error_code,
        {
            "level": "fatal",
            "message": "Unknown GIT error for distination path {path}. Error code is {error_code}. "
            "See .otoolbox/logs.text for more information.",
        },
    )
    message = error["message"].format(error_code=error_code, **context.__dict__)
    if env.context.get("continue_on_exception"):
        _logger.error(message)
        env.errors.append(message)
    else:
        raise RuntimeError(
            error["message"].format(error_code=error_code, **context.__dict__)
        )


def _get_branch_info(context: Resource):
    cwd = env.get_workspace_path(context.path)
    result = subprocess.run(
        [GIT_COMMAND, "show-branch", "--current"],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
    )
    return str.strip(result.stdout)


def _get_branch_name(context: Resource):
    cwd = env.get_workspace_path(context.path)
    result = subprocess.run(
        [GIT_COMMAND, "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
    )
    return next(
        (line.strip() for line in result.stdout.splitlines() if line.strip()), ""
    )


def _get_repo_path(context: Resource):
    git_repository_policy = env.get_env_variable("GIT_REPOSITORIES_POLICY")
    repo_path = ""
    if git_repository_policy == "standalone":
        repo_path = env.get_workspace_path(context.path)
    else:
        git_repositories_root = env.get_env_variable("GIT_REPOSITORIES_ROOT")
        assert (
            git_repositories_root
        ), "Root path of repositories is required set GIT_REPOSITORIES_ROOT"
        repo_path = env.get_workspace_path(git_repositories_root, context.path)
    return repo_path


def _is_git_repository(repository_path):
    if not os.path.isdir(repository_path):
        return False

    git_path = os.path.join(repository_path, ".git")
    return (
        # is a main repository worktree
        os.path.isdir(git_path)
        # is a git worktree, where .git is a file containing the path to
        # the main repository
        or os.path.isfile(git_path)
    )


def _is_path_in_root(path, root_path):
    try:
        normalized_path = os.path.abspath(path)
        normalized_root = os.path.abspath(root_path)
        return os.path.commonpath([normalized_path, normalized_root]) == normalized_root
    except ValueError:
        return False


def _run_git(command, cwd):
    result = utils.call_process_safe([GIT_COMMAND, *command], cwd=cwd)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result


def _create_random_branch_name():
    return f"otoolbox_{uuid.uuid4().hex}"


def _get_branch_name_from_path(path):
    result = utils.call_process_safe(
        [GIT_COMMAND, "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=path,
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    return next(
        (line.strip() for line in result.stdout.splitlines() if line.strip()), ""
    )


def _is_git_repository_main(repository_path):
    if not os.path.isdir(repository_path):
        return False

    git_path = os.path.join(repository_path, ".git")
    if not os.path.isdir(git_path):
        return False

    try:
        result = subprocess.run(
            ["git", "-C", str(repository_path), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() == "true"
    except subprocess.CalledProcessError:
        return False


######################################################################################
#                             Resource Processors                                    #
# Resource processors are used to process resources from the workspace. The resource #
# must be a git repository.                                                          #
######################################################################################


def git_link_to_repositoires_root(context: Resource):
    # Get root path
    path_root = env.get_env_variable("GIT_REPOSITORIES_ROOT", "~/Repositories")
    path_root = os.path.abspath(os.path.expanduser(path_root))

    # git path
    repository = context.path
    repo_path = env.get_workspace_path(context.path)
    repository_root_path = os.path.join(path_root, repository)
    branch_name = (
        context.branch if context.branch else env.get_env_variable("ODOO_VERSION")
    )
    assert branch_name, "Branch name is required"

    # if repo_path is in path_root then return sucess
    c_repo_path = _get_repo_path(context)
    if (
        _is_path_in_root(c_repo_path, path_root)
        and not _is_git_repository_main(repo_path)
        and _is_git_repository_main(repository_root_path)
    ):
        return PROCESS_SUCCESS, _get_branch_name(context=context)

    if not _is_git_repository(repo_path):
        raise RuntimeError(f"Not a git repository: {repo_path}")

    if not _is_git_repository(repository_root_path):
        random_branch_name = _create_random_branch_name()
        _run_git(["checkout", "-B", random_branch_name], cwd=repo_path)

        repository_root_parent = os.path.dirname(repository_root_path)
        if not os.path.isdir(repository_root_parent):
            os.makedirs(repository_root_parent, exist_ok=True)

        shutil.move(repo_path, repository_root_path)
    else:
        root_branch_name = _get_branch_name_from_path(repository_root_path)
        if root_branch_name == branch_name:
            random_branch_name = _create_random_branch_name()
            _run_git(["checkout", "-B", random_branch_name], cwd=repository_root_path)

    shutil.rmtree(repo_path)
    _run_git(
        [
            "worktree",
            "prune",
        ],
        cwd=repository_root_path,
    )
    _run_git(
        [
            "worktree",
            "add",
            repo_path,
            f"origin/{branch_name}",
        ],
        cwd=repository_root_path,
    )

    return PROCESS_SUCCESS, _get_branch_name(context=context)


def git_worktree_create(context: Resource):
    """Create a git worktree for the given branch."""
    git_repository_policy = env.get_env_variable("GIT_REPOSITORIES_POLICY")
    assert git_repository_policy, "Policy is required"
    if git_repository_policy == "standalone":
        _logger.debug(
            "Repository policy is standalone, using single worktree for each repo"
        )
        return PROCESS_SUCCESS, _get_branch_name(context=context)

    # Load path (root repository and workspace)
    git_repositories_root = env.get_env_variable("GIT_REPOSITORIES_ROOT")
    assert git_repositories_root, "Policy is required"
    git_repository_root = env.get_workspace_path(git_repositories_root, context.path)
    context_path = env.get_workspace_path(context.path)

    # repo_path = _get_repo_path(context)
    # context_pat = env.get_workspace_path(context.path)

    if _is_git_repository(context_path):
        return PROCESS_SUCCESS, _get_branch_name(context=context)
    branch_name = (
        context.branch if context.branch else env.context.get("odoo_version", "18.0")
    )

    # Get root path
    path_root = env.get_env_variable("GIT_REPOSITORIES_ROOT", "~/Repositories")
    path_root = os.path.abspath(os.path.expanduser(path_root))

    # git path
    repository = context.path
    repository_root_path = os.path.join(path_root, repository)
    root_branch_name = _get_branch_name_from_path(repository_root_path)

    if root_branch_name == branch_name:
        random_branch_name = _create_random_branch_name()
        _run_git(["checkout", "-B", random_branch_name], cwd=repository_root_path)

    result = utils.call_process_safe(
        [
            GIT_COMMAND,
            "worktree",
            "add",
            context_path,  # repository path
            "origin/" + branch_name,
        ],
        cwd=git_repository_root,  # root repository
    )

    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, _get_branch_name(context=context)


def git_worktree_prune(context: Resource):
    """Remove a git worktree for the given branch."""
    cwd = _get_repo_path(context)
    result = utils.call_process_safe(
        [GIT_COMMAND, "worktree", "prune"],
        cwd=cwd,
    )

    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, "All prunable worktree are removed"


def git_clone(context: Resource):
    """Clone the git repository from github"""
    # Check the repository
    repo_path = _get_repo_path(context)
    if _is_git_repository(repo_path):
        _logger.debug("Repository exist")
        return PROCESS_SUCCESS, "Repository is ready, create a new worktree"

    # Clone
    folder = Path(repo_path)
    organization_path = folder.parent
    if not os.path.isdir(organization_path):
        os.makedirs(organization_path)
    result = utils.call_process_safe(
        [
            GIT_COMMAND,
            "clone",
            # Clone main branch.
            # "--branch",
            # branch_name,
            (
                GIT_ADDRESS_HTTPS
                if not env.context.get("ssh_git", True)
                else GIT_ADDRESS_SSH
            ).format(path=context.path),
        ],
        cwd=organization_path,
    )

    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, "Repository is cloned"


def git_pull(context: Resource):
    """Pull the git repository from github"""
    cwd = env.get_workspace_path(context.path)
    result = utils.call_process_safe([GIT_COMMAND, "pull"], cwd=cwd)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, _get_branch_name(context=context)


def git_checkout(context: Resource):
    """Pull the git repository from github"""
    cwd = env.get_workspace_path(context.path)
    branch_name = (
        context.branch if context.branch else env.context.get("odoo_version", "18.0")
    )
    result = utils.call_process_safe([GIT_COMMAND, "checkout", branch_name], cwd=cwd)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, "Repo is checked out"


def git_add_safe_directory(context: Resource):
    """Add repository path to global git safe.directory list."""
    repository_path = env.get_workspace_path(context.path)
    result = utils.call_process_safe(
        [
            GIT_COMMAND,
            "config",
            "--global",
            "--add",
            "safe.directory",
            repository_path,
        ],
        cwd=env.get_workspace(),
    )

    if result.returncode:
        raise RuntimeError(result.stderr)
    return PROCESS_SUCCESS, f"safe.directory added: {repository_path}"


def is_git_repository(context: Resource):
    """Check if the given path is a git repository."""
    git_dir = env.get_workspace_path(context.path)
    if _is_git_repository(git_dir):
        return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE
    return PROCESS_FAIL, "Not a git repository."


def is_repository_branch_match_with_odoo_version(context: Resource):
    """Check if the repository branch matches with the odoo version."""
    branch_name = _get_branch_name(context)
    odoo_version = env.context.get("odoo_version", "18.0")
    if branch_name == odoo_version:
        return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE
    return (
        PROCESS_FAIL,
        f"Repository branch '{branch_name}' does not match with Odoo version '{odoo_version}'.",
    )
