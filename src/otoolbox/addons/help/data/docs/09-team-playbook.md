# Team Playbook (Daily Development)

این سند یک مسیر سریع و عملی برای توسعه روزمره در این workspace است.

## 1) Start of Day (5-10 min)
- Pull latest changes for related repositories.
- Confirm task scope (module, repo, expected output).
- Identify which instruction files apply:
  - Workspace: `/.github/copilot-instructions.md`
  - Repo-local: nearest `/.copilot-instructions.md` (if present)
  - Topic docs: `docs/*.md`

## 2) Implementation Flow
- Keep change scope minimal and addon-focused.
- Prefer `odoonix/*` or `oca/*` extension points before upstream edits.
- Reuse existing patterns in sibling addons.
- Avoid unrelated refactors in the same change.

## 3) Validation Flow
- Run the most targeted checks first (changed files/module).
- Add/update tests for behavior changes and bug fixes.
- Use deterministic tests (no dynamic dates, no live external API calls).
- Expand to broader checks only after local/module checks pass.

## 4) Documentation Flow
- Update docs when behavior/config/API changes.
- Keep PR notes concise: why, what changed, how tested.
- Do not manually edit generated README files.

## 5) Security Flow
- Never commit secrets, keys, or credentials.
- Keep integration secrets in environment/config.
- Sanitize examples and logs in docs/PR descriptions.

## 6) Review Flow
- One logical change per PR.
- Ensure module boundaries are respected.
- Verify checklist before requesting review.

## 7) PR Checklist
- [ ] Scope is clear and limited to requested behavior.
- [ ] Manifest and dependencies are correct.
- [ ] Tests are added/updated and relevant checks pass.
- [ ] No secret or sensitive data in diff.
- [ ] Docs updated where needed.
- [ ] PR description includes why/what/how-tested.

## 8) Copilot Prompt Templates
- `Follow docs/02-odoo-patterns.md and docs/03-testing-and-validation.md for this task.`
- `Review this diff against docs/05-oca-contributing-reference.md before PR.`
- `Apply repo-local .copilot-instructions.md and keep changes addon-scoped.`

## 9) Escalation Rules
- If a requested change conflicts with current architecture, propose an alternative before coding.
- If tests fail for unrelated reasons, report separately and avoid mixing unrelated fixes.
- If policy conflict exists, apply rule precedence:
  1. Repo-local `.copilot-instructions.md`
  2. Workspace `.github/copilot-instructions.md`
  3. Topic docs under `docs/`
