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