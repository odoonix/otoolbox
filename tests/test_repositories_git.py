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
