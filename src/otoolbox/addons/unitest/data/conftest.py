"""Pytest bridge for Odoo addons under `odoonix`.

Each test method is discovered via AST (no module imports) and exposed as a
separate pytest.Item nested under a Collector per class:

  OdooAddonTestFile (file.py)
    OdooAddonTestClass (ClassName)
      OdooAddonTestItem (method_name)

This matches VS Code's expected node-id format:
  file.py::ClassName::method_name

Execution is delegated to odoo-bin per method via
  --test-tags /addon:ClassName.method_name
Failure detection reads odoo-bin stdout/stderr.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
from pathlib import Path

import pytest
try:
    import dotenv
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    dotenv = None



# ---------------------------------------------------------------------------
#  Environment and configuration
# ---------------------------------------------------------------------------
def _load_env_variable(key, default=None):
    value = os.environ.get(key, default)
    if value is None:
        return default
    if isinstance(default, list):
        value = [item.strip() for item in value.split(",") if item.strip()]
    return value



ROOT = Path(__file__).resolve().parent
if dotenv:
    dotenv.load_dotenv(ROOT / ".env", override=True)

TARGET_REPOSITORIES = _load_env_variable("TARGET_REPOSITORIES", default=["odoonix"])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_odoonix_test_file(path: Path) -> bool:
    return (
        path.suffix == ".py"
        and path.name.startswith("test_")
        and "tests" in path.parts
        and any(repo in path.parts for repo in TARGET_REPOSITORIES)
    )


def _addon_from_test_path(path: Path) -> str:
    parts = list(path.parts)
    tests_index = parts.index("tests")
    if tests_index == 0:
        raise ValueError(f"Invalid test path: {path}")
    return parts[tests_index - 1]


def _parse_test_classes(filepath: Path) -> dict[str, list[str]]:
    """Return {ClassName: [method_name, ...]} without importing the module."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return {}
    result: dict[str, list[str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [
                item.name
                for item in node.body
                if isinstance(item, ast.FunctionDef) and item.name.startswith("test_")
            ]
            if methods:
                result[node.name] = methods
    return result


def _discover_addons_roots() -> str:
    def is_addons_dir(path: Path) -> bool:
        if not path.exists() or not path.is_dir():
            return False
        for child in path.iterdir():
            if child.is_dir() and (child / "__manifest__.py").exists():
                return True
        return False

    roots = [
        ROOT / "odoo" / "odoo" / "addons",
        ROOT / "odoo" / "design-themes",
    ]
    for top in (ROOT / "odoonix", ROOT / "moonsunsoft", ROOT / "oca"):
        if not top.exists():
            continue
        for child in sorted(top.iterdir()):
            if child.is_dir() and not child.name.startswith((".", "__")):
                roots.append(child)

    unique_existing: list[str] = []
    seen: set[str] = set()
    for path in roots:
        key = str(path)
        if key not in seen and is_addons_dir(path):
            seen.add(key)
            unique_existing.append(key)
    return ",".join(unique_existing)


def _check_odoo_test_output(stdout: str, stderr: str) -> bool:
    """Compatibility wrapper: parse output and return fail/pass flag."""
    parsed = _parse_odoo_test_output(stdout, stderr)
    summary = parsed.get("summary")
    if summary:
        return summary["failed"] > 0 or summary["errors"] > 0
    combined = stdout + "\n" + stderr
    if re.search(r"\bFAILED\b", combined):
        return True
    if re.search(r"^\s*(FAIL|ERROR)\s*:", combined, re.MULTILINE):
        return True
    return "AssertionError" in combined


_SUMMARY_RE = re.compile(
    r"odoo\.tests\.result:\s+(?P<failed>\d+)\s+failed,\s+"
    r"(?P<errors>\d+)\s+error\(s\)\s+of\s+(?P<total>\d+)\s+tests"
)
_START_RE = re.compile(
    r"odoo\.addons\.(?P<module>[\w\.]+):\s+Starting\s+"
    r"(?P<test>[A-Za-z_][\w]*\.[A-Za-z_][\w]*)\s*\.\.\."
)
_ISSUE_RE = re.compile(
    r"odoo\.addons\.(?P<module>[\w\.]+):\s+"
    r"(?P<kind>FAIL|ERROR):\s+(?P<test>[A-Za-z_][\w]*\.[A-Za-z_][\w]*)"
)
_LOG_LINE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3}\s+")


def _parse_odoo_test_output(stdout: str, stderr: str) -> dict:
    """Parse Odoo test logs and extract summary, starts, and failures/errors."""
    combined = (stdout or "") + "\n" + (stderr or "")
    lines = combined.splitlines()

    summary = None
    started_tests = []
    issues = []
    error_lines = []

    idx = 0
    while idx < len(lines):
        line = lines[idx]

        if " ERROR " in line:
            error_lines.append(line)

        if summary is None:
            summary_match = _SUMMARY_RE.search(line)
            if summary_match:
                summary = {
                    "failed": int(summary_match.group("failed")),
                    "errors": int(summary_match.group("errors")),
                    "total": int(summary_match.group("total")),
                    "line": line,
                }

        start_match = _START_RE.search(line)
        if start_match:
            started_tests.append(
                {
                    "module": start_match.group("module"),
                    "test": start_match.group("test"),
                    "line": line,
                }
            )

        issue_match = _ISSUE_RE.search(line)
        if issue_match:
            block = [line]
            cursor = idx + 1
            while cursor < len(lines):
                next_line = lines[cursor]
                if _LOG_LINE_RE.match(next_line) and (
                    _START_RE.search(next_line)
                    or _ISSUE_RE.search(next_line)
                    or _SUMMARY_RE.search(next_line)
                ):
                    break
                block.append(next_line)
                cursor += 1

            issues.append(
                {
                    "kind": issue_match.group("kind"),
                    "module": issue_match.group("module"),
                    "test": issue_match.group("test"),
                    "block": "\n".join(block).strip(),
                }
            )
            idx = cursor
            continue

        idx += 1

    return {
        "summary": summary,
        "started_tests": started_tests,
        "issues": issues,
        "error_lines": error_lines,
        "raw": combined,
    }


# ---------------------------------------------------------------------------
# Pytest collector / items
# ---------------------------------------------------------------------------

class OdooAddonTestItem(pytest.Item):
    """One Odoo test method, executed via odoo-bin."""

    def __init__(self, *, class_name: str, method_name: str, **kwargs):
        super().__init__(**kwargs)
        self.class_name = class_name
        self.method_name = method_name

    def runtest(self) -> None:
        addon_name = _addon_from_test_path(Path(str(self.path)))

        odoo_bin = Path(os.environ.get("ODOO_BIN", str(ROOT / "odoo" / "odoo" / "odoo-bin")))
        db_name = os.environ.get("ODOO_TEST_DB", "test_odoonix")
        db_host = os.environ.get("ODOO_DB_HOST", "localhost")
        db_user = os.environ.get("ODOO_DB_USER", "odoo")
        db_password = os.environ.get("ODOO_DB_PASSWORD", "odoo")
        addons_path = os.environ.get("ODOO_ADDONS_PATH", _discover_addons_roots())
        http_port = os.environ.get("ODOO_HTTP_PORT", str(20000 + (os.getpid() % 20000)))

        test_tag = f"/{addon_name}:{self.class_name}.{self.method_name}"

        # Set random name for DB to avoid conflicts, but allow overriding via env var for debugging.
        db_name = f"{db_name}_{os.getpid()}" if "ODOO_TEST_DB" not in os.environ else db_name

        # Delete test db if exists to ensure a clean slate (odoo-bin doesn't always do this with --stop-after-init)
        subprocess.run(
            [
                str(odoo_bin),
                "db",
                "drop",
                db_name,
                "--db_host", db_host,
                "--db_user", db_user,
                "--db_password", db_password,
                "--force",
            ],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            check=False,
        )

        cmd = [
            str(odoo_bin),
            "--test-enable",
            "--stop-after-init",
            "-d", db_name,
            "--db_host", db_host,
            "--db_user", db_user,
            "--db_password", db_password,
            "--http-port", http_port,
            "--addons-path", addons_path,
            "--init", addon_name,
            "--test-tags", test_tag,
        ]

        result = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, check=False)

        parsed = _parse_odoo_test_output(result.stdout, result.stderr)
        summary = parsed.get("summary")
        if summary:
            failed = (
                result.returncode != 0
                or summary["total"] == 0
                or summary["failed"] > 0
                or summary["errors"] > 0
            )
        else:
            failed = result.returncode != 0 or _check_odoo_test_output(result.stdout, result.stderr)

        if failed:
            summary_text = summary["line"] if summary else "summary not found in output"
            started = parsed.get("started_tests", [])
            issues = parsed.get("issues", [])
            error_lines = parsed.get("error_lines", [])

            started_text = "\n".join(
                f"- {item['module']} :: {item['test']}"
                for item in started
            ) or "- none"

            issues_text = "\n\n".join(
                f"[{item['kind']}] {item['module']} :: {item['test']}\n{item['block']}"
                for item in issues
            ) or "none"

            error_lines_text = "\n".join(error_lines[-30:]) or "none"

            raise AssertionError(
                f"FAILED: {test_tag}\n"
                f"Command: {' '.join(cmd)}\n\n"
                f"Summary:\n{summary_text}\n\n"
                f"Started tests:\n{started_text}\n\n"
                f"Detected FAIL/ERROR blocks:\n{issues_text}\n\n"
                f"ERROR log lines (tail):\n{error_lines_text}\n\n"
                f"--- stdout ---\n{result.stdout[-10000:]}\n\n"
                f"--- stderr ---\n{result.stderr[-10000:]}"
            )

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, AssertionError):
            return str(excinfo.value)
        return super().repr_failure(excinfo)

    def reportinfo(self):
        return self.path, 0, f"{self.class_name}::{self.method_name}"


class OdooAddonTestClass(pytest.Collector):
    """Groups test methods under their class name — needed for VS Code node-id resolution."""

    def __init__(self, *, class_name: str, method_names: list[str], **kwargs):
        super().__init__(**kwargs)
        self.class_name = class_name
        self.method_names = method_names

    def collect(self):
        for method_name in self.method_names:
            yield OdooAddonTestItem.from_parent(
                self,
                name=method_name,
                class_name=self.class_name,
                method_name=method_name,
            )


class OdooAddonTestFile(pytest.File):
    """Collects all test classes/methods from an Odoo test file via AST."""

    def collect(self):
        path = Path(str(self.path))
        classes = _parse_test_classes(path)
        if not classes:
            # Fallback: no test classes found — expose file as single item
            yield OdooAddonTestItem.from_parent(
                self, name=path.name, class_name="", method_name=""
            )
            return
        for class_name, method_names in classes.items():
            yield OdooAddonTestClass.from_parent(
                self,
                name=class_name,
                class_name=class_name,
                method_names=method_names,
            )


def pytest_collect_file(file_path: Path, parent):
    path = Path(str(file_path))
    if _is_odoonix_test_file(path):
        return OdooAddonTestFile.from_parent(parent, path=path)
    return None


def pytest_configure(config):
    print("✓ Custom Odoo collector enabled (odoonix/tests only)")
