# Testing & Validation

## Environment
- Workspace Python: `${workspaceFolder}/.venv/bin/python`.
- Main server entrypoint: `odoo/odoo/odoo-bin`.
- Effective addons path is defined centrally in:
  - `odools.toml`
  - `odoo-dev.code-workspace`

## Test Strategy
- Start with focused checks for changed files/modules.
- Prefer module-specific Odoo test runs before broader regression runs.
- Run formatting/linting only on relevant scope where possible.

## Useful Workspace Commands
- `otoolbox run update --tags git`
- `otoolbox run init --tags odoo-dev.code-workspace`

## Practical Notes
- Root `requirements.txt` is empty; install dependencies from the repo/addon being changed.
- If `python.analysis` excludes some folders, use direct file paths when searching.
