from types import SimpleNamespace

from otoolbox.addons import _sort_addons_by_dependencies


def test_sort_addons_by_dependencies_orders_dependency_first(monkeypatch):
    module_map = {
        "otoolbox.addons.unitest": SimpleNamespace(
            app=SimpleNamespace(__cli_name__="unitest", __depends_on__=["vscode"])
        ),
        "otoolbox.addons.vscode": SimpleNamespace(
            app=SimpleNamespace(__cli_name__="vscode")
        ),
        "otoolbox.addons.repositories": SimpleNamespace(
            app=SimpleNamespace(__cli_name__="repo")
        ),
    }

    monkeypatch.setattr(
        "otoolbox.addons.import_module", lambda module_name: module_map[module_name]
    )

    ordered = _sort_addons_by_dependencies(
        [
            "otoolbox.addons.unitest",
            "otoolbox.addons.repositories",
            "otoolbox.addons.vscode",
        ]
    )

    assert ordered == [
        "otoolbox.addons.vscode",
        "otoolbox.addons.unitest",
        "otoolbox.addons.repositories",
    ]


def test_sort_addons_by_dependencies_ignores_missing_dependencies(monkeypatch):
    module_map = {
        "otoolbox.addons.copilot": SimpleNamespace(
            app=SimpleNamespace(__cli_name__="copilot", __depends_on__=["missing-addon"])
        ),
        "otoolbox.addons.vscode": SimpleNamespace(
            app=SimpleNamespace(__cli_name__="vscode")
        ),
    }

    monkeypatch.setattr(
        "otoolbox.addons.import_module", lambda module_name: module_map[module_name]
    )

    ordered = _sort_addons_by_dependencies(
        [
            "otoolbox.addons.copilot",
            "otoolbox.addons.vscode",
        ]
    )

    assert ordered == [
        "otoolbox.addons.copilot",
        "otoolbox.addons.vscode",
    ]