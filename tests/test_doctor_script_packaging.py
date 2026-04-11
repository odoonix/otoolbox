from configparser import ConfigParser
from pathlib import Path
import importlib.util


def test_setup_cfg_platforms_include_windows_and_linux():
    repo_root = Path(__file__).resolve().parents[1]
    setup_cfg_path = repo_root / "setup.cfg"

    parser = ConfigParser()
    parser.read(setup_cfg_path)

    platforms_value = parser.get("metadata", "platforms")
    platforms = [item.strip().lower() for item in platforms_value.split(",")]

    assert "linux" in platforms
    assert "windows" in platforms


def test_setup_py_selects_platform_specific_script():
    repo_root = Path(__file__).resolve().parents[1]
    setup_py_path = repo_root / "setup.py"

    spec = importlib.util.spec_from_file_location("otoolbox_setup", setup_py_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    selected_scripts = module._platform_scripts()
    assert selected_scripts in (
        ["bin/otoolbox-doctor"],
        ["bin/otoolbox-doctor.bat"],
    )


def test_otoolbox_doctor_script_content_and_shebang():
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "bin" / "otoolbox-doctor"

    assert script_path.is_file()

    content = script_path.read_text(encoding="utf-8")
    assert content.startswith("#!/usr/bin/env bash\n")
    assert "otoolbox run verify" in content


def test_otoolbox_doctor_bat_exists_and_contains_command():
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "bin" / "otoolbox-doctor.bat"

    assert script_path.is_file()

    content = script_path.read_text(encoding="utf-8")
    assert content.startswith("@echo off")
    assert "otoolbox run verify" in content
