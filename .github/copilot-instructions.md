# Copilot Instructions — otoolbox

## Purpose

`otoolbox` is a utility tool to maintain Odoo **development environments** and **production source code**.
It manages a collection of *resources* (git repositories, config files, VS Code workspaces, addons, etc.)
through a structured lifecycle with well-defined processes at each step.

---

## Core Architecture

### Environment

`Environment` (see `src/otoolbox/environment.py`) is the top-level container.
- Holds a `ResourceSet` — the collection of all resources loaded for the current run.
- Provides `context` (author, organisation metadata) passed into processes.
- Entry point for all CLI commands.

### Resource

`Resource` (see `src/otoolbox/base.py`) is the fundamental unit of the system.
- Represents a single managed entity: a git repo, a config file, a workspace, a VS Code extension, etc.
- Has a `path` (unique key), `tags` list, `priority`, `parent`, and lifecycle processors.
- Is identified and filtered by its `tags`.

### Resource Lifecycle

Every resource moves through a fixed set of steps (defined in `src/otoolbox/constants.py`):

| Step       | Constant       | Meaning                                     |
|------------|----------------|---------------------------------------------|
| `init`     | `STEP_INIT`    | Initialise / create the resource            |
| `build`    | `STEP_BUILD`   | Build or clone the resource                 |
| `verify`   | `STEP_VERIFY`  | Verify the resource is healthy              |
| `update`   | `STEP_UPDATE`  | Update / synchronise the resource           |
| `destroy`  | `STEP_DESTROY` | Remove or tear down the resource            |

### ResourceProcessor

`ResourceProcessor` (see `src/otoolbox/base.py`) wraps a single callable *process function*.
- Bound to one `Resource` and one `step`.
- When executed, calls `process(context=resource, **kargs)`.
- Returns a `(result, message)` tuple where result is `PROCESS_SUCCESS`, `PROCESS_FAIL`, or `PROCESS_WAR`.

### ResourceExecutor / ResourceSetExecutor

- `ResourceExecutor` runs all processors of a resource for a given set of steps, in registration order.
- `ResourceSetExecutor` runs all executors in the set, sorted by `resource.priority` (highest first).

---

## Process Function Contract

Every process function **must** follow this signature:

```python
def my_process(context: Resource, **kargs) -> tuple[str, str]:
    """Brief description of what this process does."""
    # context is the Resource being processed
    # return (result_constant, human_readable_message)
    return PROCESS_SUCCESS, ""
```

Result constants (import from `otoolbox.constants`):
- `PROCESS_SUCCESS` — step completed successfully.
- `PROCESS_FAIL` — step failed; execution continues but the failure is logged.
- `PROCESS_WAR` — step completed with a warning.

---

## Tags and Filtering

- Resources declare `tags` (a list of strings). `path` is always added as a tag.
- Standard tag constants are in `otoolbox.constants` (`RESOURCE_TAGS_GIT`, `RESOURCE_TAGS_ENV`, etc.).
- CLI commands accept `--tags` to filter which resources are processed.
- Use `resource.has_tags(*tags)` to check tag membership (all tags must match).

---

## Adding a New Resource Type

1. Subclass `Resource` in the appropriate addon package under `src/otoolbox/addons/`.
2. Register processors with `resource.add_processor(process_fn, step=STEP_BUILD, title="...")`.
3. Add the resource to the environment's `ResourceSet` via an addon `__init__.py` setup hook.
4. Tag the resource appropriately so CLI filters work correctly.

## Adding a New Process

1. Define the process function with the contract above.
2. Register it on the target resource at the right step.
3. Keep each process function focused on a single responsibility.
4. Do not raise exceptions for expected failures — return `PROCESS_FAIL` with a descriptive message.

---

## Addon Structure

Each addon lives under `src/otoolbox/addons/<name>/` and follows this layout:

```
<name>/
    __init__.py        # registers resources / processors into the environment
    config.py          # addon-specific configuration constants
    constants.py       # addon-specific string/value constants
    <name>_utils.py    # utility helpers (no side effects at import time)
    data/              # static data files (templates, CSVs, JSON, etc.)
    README.rst         # human-readable addon description
```

---

## Code Style

- Follow PEP 8. Maximum line length 100 characters.
- Imports order: Python standard library → third-party → `otoolbox` modules → current addon.
- Use `logging.getLogger(__name__)` — never `print()` for operational output; use `rich` console for user-facing output.
- Constants belong in `otoolbox/constants.py` (global) or `<addon>/constants.py` (addon-scoped).
- Do not add logic to `__init__.py` beyond registration calls.

---

## Testing

- Tests live in `tests/` at the repo root.
- Use `pytest`. Run with: `source .venv/bin/activate && python -m pytest tests/`
- Each test file mirrors a source module: `test_<module>.py`.
- Process functions should be unit-testable by calling them directly with a mock `Resource` context.
- Use `PROCESS_SUCCESS`/`PROCESS_FAIL` assertions — do not assert on message strings unless necessary.
