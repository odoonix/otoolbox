from types import SimpleNamespace

import pytest

from otoolbox import env
from otoolbox.constants import PROCESS_SUCCESS
from otoolbox.addons.repositories import git


def test_git_add_safe_directory_executes_expected_command(monkeypatch, tmp_path):
    monkeypatch.setitem(env.context, "path", str(tmp_path))
    context = SimpleNamespace(path="moonsunsoft/payment")
    calls = {}

    def fake_call_process_safe(command, cwd=None, **kwargs):
        calls["command"] = command
        calls["cwd"] = cwd
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(git.utils, "call_process_safe", fake_call_process_safe)

    result, message = git.git_add_safe_directory(context)

    expected_path = str(tmp_path / "moonsunsoft" / "payment")
    assert calls["command"] == [
        "git",
        "config",
        "--global",
        "--add",
        "safe.directory",
        expected_path,
    ]
    assert calls["cwd"] == str(tmp_path)
    assert result == PROCESS_SUCCESS
    assert expected_path in message


def test_git_add_safe_directory_raises_on_error(monkeypatch, tmp_path):
    monkeypatch.setitem(env.context, "path", str(tmp_path))
    context = SimpleNamespace(path="moonsunsoft/payment")

    monkeypatch.setattr(
        git.utils,
        "call_process_safe",
        lambda *args, **kwargs: SimpleNamespace(returncode=1, stderr="boom"),
    )

    with pytest.raises(RuntimeError, match="boom"):
        git.git_add_safe_directory(context)


def test_get_branch_name_uses_abbrev_ref_and_returns_clean_output(
    monkeypatch, tmp_path
):
    monkeypatch.setitem(env.context, "path", str(tmp_path))
    context = SimpleNamespace(path="moonsunsoft/payment")
    calls = {}

    def fake_subprocess_run(command, capture_output, text, cwd, check):
        calls["command"] = command
        calls["cwd"] = cwd
        return SimpleNamespace(returncode=0, stdout="17.0\n", stderr="")

    monkeypatch.setattr(git.subprocess, "run", fake_subprocess_run)

    branch_name = git._get_branch_name(context)

    assert calls["command"] == ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    assert calls["cwd"] == str(tmp_path / "moonsunsoft" / "payment")
    assert branch_name == "17.0"


def test_git_link_to_repositories_root_noop_when_workspace_is_worktree(
    monkeypatch, tmp_path
):
    monkeypatch.setitem(env.context, "path", str(tmp_path))
    context = SimpleNamespace(path="moonsunsoft/payment", branch="17.0")

    workspace_repo_path = str(tmp_path / "moonsunsoft" / "payment")
    root_base = str(tmp_path / "central")
    root_repo_path = str(tmp_path / "central" / "moonsunsoft" / "payment")

    monkeypatch.setattr(git, "_use_multi_worktree", lambda: True)
    monkeypatch.setattr(
        env,
        "get_env_variable",
        lambda name, default=None: (
            root_base
            if name == "GIT_REPOSITORIES_ROOT"
            else ("17.0" if name == "ODOO_VERSION" else default)
        ),
    )
    monkeypatch.setattr(
        git, "_is_git_worktree", lambda path: path == workspace_repo_path
    )
    monkeypatch.setattr(
        git, "_is_git_repository_main", lambda path: path == root_repo_path
    )
    monkeypatch.setattr(git, "_get_branch_name", lambda context: "17.0")

    run_git_calls = []
    monkeypatch.setattr(
        git,
        "_run_git",
        lambda command, cwd: run_git_calls.append((command, cwd)),
    )

    result, message = git.git_link_to_repositoires_root(context)

    assert result == PROCESS_SUCCESS
    assert message == "17.0"
    assert run_git_calls == []


def test_git_link_to_repositories_root_creates_worktree_when_missing(
    monkeypatch, tmp_path
):
    monkeypatch.setitem(env.context, "path", str(tmp_path))
    context = SimpleNamespace(path="moonsunsoft/payment", branch="17.0")

    workspace_repo_path = str(tmp_path / "moonsunsoft" / "payment")
    root_base = str(tmp_path / "central")
    root_repo_path = str(tmp_path / "central" / "moonsunsoft" / "payment")

    monkeypatch.setattr(git, "_use_multi_worktree", lambda: True)
    monkeypatch.setattr(
        env,
        "get_env_variable",
        lambda name, default=None: (
            root_base
            if name == "GIT_REPOSITORIES_ROOT"
            else ("17.0" if name == "ODOO_VERSION" else default)
        ),
    )
    monkeypatch.setattr(git, "_is_git_worktree", lambda path: False)
    monkeypatch.setattr(
        git,
        "_is_git_repository_main",
        lambda path: path == root_repo_path,
    )
    monkeypatch.setattr(
        git,
        "_is_git_repository",
        lambda path: path == root_repo_path,
    )
    monkeypatch.setattr(git, "_get_branch_name_from_path", lambda path: "main")
    monkeypatch.setattr(git, "_get_branch_name", lambda context: "17.0")

    run_git_calls = []

    def fake_run_git(command, cwd):
        run_git_calls.append((command, cwd))
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(git, "_run_git", fake_run_git)

    result, message = git.git_link_to_repositoires_root(context)

    assert result == PROCESS_SUCCESS
    assert message == "17.0"
    assert run_git_calls == [
        (["worktree", "prune"], root_repo_path),
        (["worktree", "add", workspace_repo_path, "origin/17.0"], root_repo_path),
    ]
