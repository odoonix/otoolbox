# Copilot instructions for this workspace

## Purpose
- This document is the workspace-level policy for development with Copilot.
- It is written for both day-to-day implementation and team training/onboarding.

## Audience
- Developers working in this mono-repo.
- AI assistants generating or reviewing code in this workspace.

## Rule precedence (important)
- Apply rules in this order:
  1. Nearest repo-local `.copilot-instructions.md`
  2. This workspace file: `.github/copilot-instructions.md`
  3. Referenced topic docs under `docs/`
- In conflicts, the most specific (nearest repo-local) rule wins.

## Topic map (split docs)
- Keep this file short and stable; put detailed policies in topic docs.
- `docs/00-file-and-folders.md` → structure of files and folders in the repo, including addons, connectors, and config.
- `docs/01-global-style.md` → global coding behavior, scope control, safety.
- `docs/02-odoo-patterns.md` → Odoo 19 patterns, addon boundaries, connector conventions.
- `docs/03-testing-and-validation.md` → test strategy, environment, and validation flow.
- `docs/04-security-and-secrets.md` → secret handling and integration safety checks.
- `docs/05-oca-contributing-reference.md` → OCA-friendly contribution rules for module design, tests, PRs, and reviews.
- `docs/06-odoo-test-framework-guid.md` → Odoo test framework concepts, tags, and execution flow.
- `docs/07-odoonix-guidline.md` → repo-level Odoonix development conventions.
- `docs/08-copilot-instructions-guideline.md` → how to evolve, review, and keep Copilot instructions maintainable.
- `docs/09-team-playbook.md` → one-page daily workflow for development, validation, review, and onboarding.

## Repo-local Copilot instructions
- Some git repositories in this workspace include a local `.copilot-instructions.md` file.
- When working inside such repositories, always apply both workspace and repo-local rules.
- Example currently present: `odoonix/connector/.copilot-instructions.md`.

## How to use topic docs in prompts
- For focused tasks, explicitly reference topic files in prompts, for example:
  - "Follow `docs/02-odoo-patterns.md` for this connector change."
  - "Apply `docs/03-testing-and-validation.md` before finalizing."
  - "Review this change with `docs/05-oca-contributing-reference.md` before opening PR."

## Team training usage
- Use this file as the entrypoint and learning map.
- For onboarding sessions, walk through the topic docs in this order:
  1. `docs/00-file-and-folders.md`
  2. `docs/01-global-style.md`
  3. `docs/02-odoo-patterns.md`
  4. `docs/03-testing-and-validation.md`
  5. `docs/05-oca-contributing-reference.md`
- Keep examples and exercises in topic docs, not in this root file.

## Repo map (what matters first)
- This is a mono-repo that combines upstream Odoo, OCA repos, and company repos.
- Main code families:
  - `odoo/` → upstream framework and official addons (`odoo/odoo/odoo-bin`, `odoo/odoo/addons/*`).
  - `oca/` → community addons grouped per repo (`oca/connector`, `oca/server-tools`, `oca/web`, etc.).
  - `odoonix/` + `moonsunsoft/` → company modules (connectors, CRM, verticals).
- The effective addons-path is long and centrally defined in `odools.toml` and `odoo-dev.code-workspace`.

## Preferred change boundaries
- Implement business features in `odoonix/*` or `oca/*` modules first.
- Avoid editing upstream `odoo/odoo` unless explicitly requested or no module-level extension is viable.
- Keep module boundaries clean: model/view/security/data changes stay inside the target addon.

## High-value architecture patterns
- Connectors are a primary integration domain: see `odoonix/connector/*` and `oca/connector/*`.
- Typical connector families include `connector_base`, `connector_shopify`, `connector_xero`, `connector_wordpress`.
- Reuse sibling connector patterns before introducing new abstractions.

## Dev/test workflows used here
- Python interpreter is workspace-local: `${workspaceFolder}/.venv/bin/python`.
- Main server entrypoint: `odoo/odoo/odoo-bin`.
- Typical update run (adapt DB/module):
  - `.venv/bin/python odoo/odoo/odoo-bin --db_host localhost --db_user odoo --db_password odoo --database odoo19-run --addons-path <paths> --update connector_shopify --dev all --with-demo`
- VS Code includes Otoolbox tasks in `odoo-dev.code-workspace`:
  - `otoolbox run update --tags git`
  - `otoolbox repo add <url>` / `otoolbox repo remove <url>`
  - `otoolbox run init --tags odoo-dev.code-workspace`
- Debug/test launch presets (`Odoo Run`, `Odoo Test`) are in `odoo-dev.code-workspace`.

## Module conventions to follow
- Standard addon layout: `__manifest__.py`, `models/`, `views/`, `security/`, optional `controllers/`.
- Module license and dependencies are declared per addon in `__manifest__.py` (do not assume repo-wide license).
- Many repos include `checklog-odoo.cfg`, `eslint.config.cjs`, `prettier.config.cjs`; preserve them.
- Python/test deps are often local to each repo (`requirements.txt`, `test-requirements.txt`, `pyproject.toml`).

## Practical agent tips for this workspace
- Root `requirements.txt` is empty; install dependencies from the repo/module you modify.
- `python.analysis` search excludes `**/moonsunsoft/**` in workspace settings; use direct file paths when needed.
- For module-specific behavior, read the nearest addon/repo `README.md` before coding.
- Never commit secrets used by connectors; keep credentials in environment/config.
