# Global Style & Working Rules

## Scope
- Prefer minimal, targeted changes.
- Keep behavior backward compatible unless the task explicitly asks otherwise.
- Preserve existing code style and repository conventions.

## Change Discipline
- Fix root cause, not symptoms.
- Avoid unrelated refactors in the same patch.
- Do not change upstream files when an addon-level extension is possible.

## Communication
- State assumptions when environment/config is uncertain.
- Use concise summaries of what changed and why.
- Reference exact file paths and symbols in explanations.

## Language
- Write code, comments, docstrings, and test descriptions in English by default.
- Use non-English text only when the request explicitly requires it.

## Python & Test Lint Baseline (Ruff)
- Keep line length within `88` characters (`E501`).
- Use union syntax in `isinstance`: `isinstance(x, A | B)` (`UP038`).
- Avoid ambiguous one-letter names (`E741`).
- Prefix intentionally unused loop variables with `_` (`B007`).
- Remove unused local assignments (`F841`).
- Extract helpers when function complexity grows near thresholds (`C901`).

## Safety
- Never commit secrets or credentials.
- Keep connector credentials in environment/config, not source code.
