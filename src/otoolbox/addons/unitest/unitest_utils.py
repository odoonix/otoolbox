import os


from otoolbox.base import Resource
from otoolbox import env
import json
from otoolbox.constants import (
    PROCESS_SUCCESS,
    PROCESS_FAIL,
    PROCESS_EMPTY_MESSAGE,
)


def add_python_testing_config(context: Resource):
    """This function check configuration in VSCode workspace setting file and
    enable python testing if not enabled. It also add some default configuration for pytest.
    """
    file_path = env.get_workspace_path(context.path)
    assert os.path.isfile(
        file_path
    ), f"File {file_path} doesn't exist or isn't readable"

    # Hre is a jeson configuration for pytest.
    # Must check if there is in the file_path and if not add it.
    #
    # "python.testing.pytestEnabled": true,
    # "python.testing.pytestArgs": [
    #     "--tb=short",
    #     "-v"
    # ],
    # "python.testing.unittestEnabled": false,
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            config = json.load(f)
        except Exception:
            config = {}

    # Remove nested python.testing.pytestEnabled if exists
    settings = config.get("settings", {})
    if isinstance(settings.get("python"), dict) and isinstance(
        settings["python"].get("testing"), dict
    ):
        settings["python"]["testing"].pop("pytestEnabled", None)
        settings["python"]["testing"].pop("pytestArgs", None)
        settings["python"]["testing"].pop("unittestEnabled", None)

    # Set top-level keys
    settings["python.testing.pytestEnabled"] = True
    settings["python.testing.pytestArgs"] = ["--tb=short", "-v"]
    settings["python.testing.unittestEnabled"] = False

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

    return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE


def verify_python_testing_config(context: Resource):
    """This function check configuration in VSCode workspace setting file and return success
    if python testing is enabled and configured correctly for pytest, otherwise return fail.
    """
    file_path = env.get_workspace_path(context.path)
    assert os.path.isfile(
        file_path
    ), f"File {file_path} doesn't exist or isn't readable"

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            config = json.load(f)
        except Exception:
            return PROCESS_FAIL, "Invalid JSON format in workspace configuration."

    settings = config.get("settings", {})
    pytest_enabled = settings.get("python.testing.pytestEnabled")
    pytest_args = settings.get("python.testing.pytestArgs")
    unittest_enabled = settings.get("python.testing.unittestEnabled")

    if (
        pytest_enabled is True
        and pytest_args == ["--tb=short", "-v"]
        and unittest_enabled is False
    ):
        return PROCESS_SUCCESS, PROCESS_EMPTY_MESSAGE
    else:
        return (
            PROCESS_FAIL,
            "Python testing configuration is not set correctly. Please run the init process to set it up.",
        )
