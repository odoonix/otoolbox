import json

from otoolbox import env
from otoolbox.addons.repositories.config import _load_repository_list
from otoolbox.addons.repositories.constants import REPOSITORIES_PATH


def test_load_repository_list_adds_git_repositories_from_workspace(tmp_path, monkeypatch):
    monkeypatch.setitem(env.context, "path", str(tmp_path))
    monkeypatch.setitem(env.context, "odoo_version", "17.0")
    monkeypatch.setattr(
        "otoolbox.addons.repositories.config.env.resource_string",
        lambda *args, **kwargs: json.dumps(
            [{"organization": "oca", "repository": "server-ux"}]
        ),
    )

    (tmp_path / "oca" / "server-ux" / ".git").mkdir(parents=True)
    (tmp_path / "custom" / "my-repo" / ".git").mkdir(parents=True)

    repo_list = _load_repository_list()

    assert repo_list == [
        {
            "organization": "oca",
            "repository": "server-ux",
            "is_existe": True,
            "has_mirror": False,
        },
        {
            "organization": "custom",
            "repository": "my-repo",
            "is_existe": True,
            "has_mirror": False,
        },
    ]


def test_load_repository_list_does_not_duplicate_workspace_repositories(tmp_path, monkeypatch):
    monkeypatch.setitem(env.context, "path", str(tmp_path))

    repositories_path = tmp_path / REPOSITORIES_PATH
    repositories_path.write_text(
        json.dumps(
            [
                {"organization": "oca", "repository": "server-ux"},
                {"organization": "partner", "repository": "partner-repo"},
            ]
        ),
        encoding="utf8",
    )

    (tmp_path / "oca" / "server-ux" / ".git").mkdir(parents=True)
    (tmp_path / "custom" / "my-repo" / ".git").mkdir(parents=True)

    repo_list = _load_repository_list()

    assert repo_list == [
        {
            "organization": "oca",
            "repository": "server-ux",
            "is_existe": True,
            "has_mirror": False,
        },
        {
            "organization": "partner",
            "repository": "partner-repo",
            "is_existe": False,
            "has_mirror": False,
        },
        {
            "organization": "custom",
            "repository": "my-repo",
            "is_existe": True,
            "has_mirror": False,
        },
    ]


def test_load_repository_list_toml_has_higher_priority_than_json(tmp_path, monkeypatch):
    monkeypatch.setitem(env.context, "path", str(tmp_path))

    repositories_path = tmp_path / REPOSITORIES_PATH
    repositories_path.write_text(
        json.dumps(
            [
                {
                    "organization": "oca",
                    "repository": "server-ux",
                    "branch": "17.0",
                    "title": "from-json",
                }
            ]
        ),
        encoding="utf8",
    )

    repo_path = tmp_path / "oca" / "server-ux"
    (repo_path / ".git").mkdir(parents=True)
    (repo_path / "otoolbox.toml").write_text(
        """
[repository]
branch = "18.0"
title = "from-toml"
website = "https://example.com/repo"
""".strip(),
        encoding="utf8",
    )

    repo_list = _load_repository_list()

    assert repo_list == [
        {
            "organization": "oca",
            "repository": "server-ux",
            "branch": "18.0",
            "title": "from-toml",
            "website": "https://example.com/repo",
            "is_existe": True,
            "has_mirror": False,
        }
    ]


def test_load_repository_list_sets_mirror_flags_from_toml(tmp_path, monkeypatch):
    monkeypatch.setitem(env.context, "path", str(tmp_path))

    repositories_path = tmp_path / REPOSITORIES_PATH
    repositories_path.write_text(
        json.dumps([
            {"organization": "moonsunsoft", "repository": "cnp", "branch": "17.0"}
        ]),
        encoding="utf8",
    )

    repo_path = tmp_path / "moonsunsoft" / "cnp"
    (repo_path / ".git").mkdir(parents=True)
    (repo_path / "otoolbox.toml").write_text(
        """
[[mirror]]
repository = "cnp"
organization = "odoonix"
branch = "17.0"

[[mirror]]
repository = "cnp-second"
organization = "other-org"
""".strip(),
        encoding="utf8",
    )

    repo_list = _load_repository_list()

    assert repo_list == [
        {
            "organization": "moonsunsoft",
            "repository": "cnp",
            "branch": "17.0",
            "enable_in_runtime": False,
            "is_shielded": True,
            "linked_shielded_repository": "cnp",
            "linked_shielded_organization": "odoonix",
            "linked_shielded_repo": "cnp",
            "is_existe": True,
            "has_mirror": True,
            "mirror": [
                {
                    "repository": "cnp",
                    "organization": "odoonix",
                    "branch": "17.0",
                },
                {
                    "repository": "cnp-second",
                    "organization": "other-org",
                },
            ],
        }
    ]