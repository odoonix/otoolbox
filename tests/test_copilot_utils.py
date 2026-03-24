from types import SimpleNamespace
from importlib import import_module

from otoolbox import env
from otoolbox.constants import PROCESS_SUCCESS, PROCESS_FAIL, STEP_VERIFY

copilot_utils = import_module("otoolbox.addons.copilot.utils")


def test_is_copilot_configured_success(tmp_path, monkeypatch):
    monkeypatch.setitem(env.context, "path", str(tmp_path))
    context = SimpleNamespace(path="odoonix/payment")
    target_file = tmp_path / "odoonix" / "payment" / ".copilot-instructions.md"
    target_file.parent.mkdir(parents=True)
    target_file.write_text("ok", encoding="utf8")

    result, message = copilot_utils.is_copilot_configured(context)

    assert result == PROCESS_SUCCESS
    assert message == ""


def test_is_copilot_configured_missing_file_returns_fail(tmp_path, monkeypatch):
    monkeypatch.setitem(env.context, "path", str(tmp_path))
    context = SimpleNamespace(path="odoonix/payment")

    result, message = copilot_utils.is_copilot_configured(context)

    assert result == PROCESS_FAIL
    assert ".copilot-instructions.md" in message


def test_init_verification_process_adds_verify_processor(monkeypatch):
    calls = []

    class FakeResource:
        def __init__(self, is_git):
            self.is_git = is_git

        def has_tag(self, *tags):
            return self.is_git and "git" in tags

        def add_processor(self, **kwargs):
            calls.append(kwargs)

    resources = [FakeResource(is_git=True), FakeResource(is_git=False)]

    class FakeResourceSet:
        def filter(self, predicate):
            return [resource for resource in resources if predicate(resource)]

    monkeypatch.setattr(env, "resources", FakeResourceSet())

    copilot_utils.init_verification_process()

    assert len(calls) == 1
    assert calls[0]["process"] == copilot_utils.is_copilot_configured
    assert calls[0]["step"] == STEP_VERIFY
    assert calls[0]["title"] == "Verify copilot settings"


def test_load_copilot_configuration_resource_adds_existing_files(
    tmp_path, monkeypatch
):
    monkeypatch.setitem(env.context, "path", str(tmp_path))
    added_resources = []

    class FakeResource:
        def __init__(self, path, is_git):
            self.path = path
            self.is_git = is_git

        def has_tag(self, *tags):
            return self.is_git and "git" in tags

    resources = [
        FakeResource("odoonix/payment", True),
        FakeResource("odoonix/website", True),
        FakeResource("odoonix/not-git", False),
    ]

    class FakeResourceSet:
        def filter(self, predicate):
            return [resource for resource in resources if predicate(resource)]

    monkeypatch.setattr(env, "resources", FakeResourceSet())
    monkeypatch.setattr(env, "add_resource", lambda **kwargs: added_resources.append(kwargs))

    existing_file = tmp_path / "odoonix" / "payment" / ".copilot-instructions.md"
    existing_file.parent.mkdir(parents=True)
    existing_file.write_text("ok", encoding="utf8")

    copilot_utils.load_copilot_configuration_resource()

    assert len(added_resources) == 1
    assert added_resources[0]["path"] == "odoonix/payment/.copilot-instructions.md"
    assert added_resources[0]["parent"] == "odoonix/payment"