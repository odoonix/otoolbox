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

## Safety
- Never commit secrets or credentials.
- Keep connector credentials in environment/config, not source code.
