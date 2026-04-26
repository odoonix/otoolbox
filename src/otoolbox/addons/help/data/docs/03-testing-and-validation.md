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

## Validation Sequence (Required)
1. Run focused lint for touched files first, for example:
  - `pre-commit run ruff --files <file1> <file2> ...`
2. Run focused tests for the changed module/feature.
3. Run broad validation only after focused checks pass:
  - `pre-commit run -a`
4. If behavior is intentionally changed, update tests to match new semantics in the same patch.

## Common Failure Prevention
- Wrap long strings/docstrings early to avoid `E501` churn.
- Prefer helper extraction in tests/builders when complexity approaches limits (`C901`).
- Treat static-analysis import misses in Odoo tests as environment/indexing issues unless runtime checks fail.

## Useful Workspace Commands
- `otoolbox run update --tags git`
- `otoolbox run init --tags odoo-dev.code-workspace`

## Practical Notes
- Root `requirements.txt` is empty; install dependencies from the repo/addon being changed.
- If `python.analysis` excludes some folders, use direct file paths when searching.
