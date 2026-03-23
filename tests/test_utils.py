from types import SimpleNamespace

from otoolbox import env
from otoolbox import utils


class DummyResource:
    def __init__(self, name, priority):
        self.name = name
        self.priority = priority

    def __str__(self):
        return self.name


def test_print_result_skips_empty_generators_and_prints_non_empty(monkeypatch):
    printed_messages = []
    monkeypatch.setitem(env.context, "silent", False)
    monkeypatch.setattr(env.console, "print", printed_messages.append)

    empty_executor = SimpleNamespace(resource=DummyResource("empty", 100))
    non_empty_executor = SimpleNamespace(resource=DummyResource("filled", 200))

    def empty_processors():
        if False:
            yield None

    def non_empty_processors():
        yield ("ok", "done", "git_pull")

    utils.print_result(
        [
            (empty_processors(), empty_executor),
            (non_empty_processors(), non_empty_executor),
        ]
    )

    assert printed_messages == [
        "\nfilled (1, 200)",
        "[ok] git_pull (done)",
    ]


def test_print_result_consumes_generators_in_silent_mode(monkeypatch):
    consumed = []
    printed_messages = []
    monkeypatch.setitem(env.context, "silent", True)
    monkeypatch.setattr(env.console, "print", printed_messages.append)

    executor = SimpleNamespace(resource=DummyResource("filled", 100))

    def processors():
        consumed.append("ran")
        yield ("ok", "done", "git_pull")

    utils.print_result([(processors(), executor)])

    assert consumed == ["ran"]
    assert printed_messages == []