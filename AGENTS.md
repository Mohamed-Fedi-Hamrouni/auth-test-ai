# AuthTest AI — Codex project instructions

## Project purpose

AuthTest AI is a secure authentication web application whose main deliverable
is a complete automated testing strategy using Pytest and Robot Framework.

AI features assist test generation and failure analysis, but never replace
deterministic tests or human review.

## Repository architecture

- `frontend/`: Angular application.
- `backend/`: Flask API and PostgreSQL persistence.
- `robot-tests/`: API, UI, database, security, smoke and regression suites.
- `ai-testing/`: Robot result parsing, redaction, providers and AI reports.
- `docs/`: requirements, architecture, testing, security and delivery evidence.
- `infra/`: Prometheus, Grafana and infrastructure configuration.

## Mandatory workflow

- Read the relevant documentation before editing.
- Run `git status` before starting.
- Inspect existing code and tests before proposing changes.
- State a short plan before implementing.
- Implement only the requested scope.
- Run all relevant tests after modifications.
- Report exact commands and actual results.
- Never claim that a command passed when it was not executed.
- Do not commit, push, create tags or open pull requests unless explicitly asked.
- Do not use `git reset --hard`.
- Do not delete Docker volumes or databases.
- Do not perform destructive migrations.
- Do not modify unrelated files.

## Security

- Never store or print plaintext passwords.
- Never expose JWTs, cookies, CSRF tokens or API keys.
- Never add real secrets to `.env.example`, logs, fixtures or documentation.
- Passwords must be securely hashed.
- Authentication errors must not reveal whether a user exists.
- Authentication tokens must not be stored in browser localStorage or sessionStorage.
- AI input must be redacted before any external request.
- External AI calls must remain disabled in CI by default.

## Testing

- Every behavior change requires an appropriate test.
- Backend business logic uses Pytest.
- API, UI, database and security flows use Robot Framework.
- Use stable `data-testid` locators for UI automation.
- Do not use arbitrary sleeps in UI tests.
- Do not hide failures with permissive exception handling.
- AI unavailability must not change a Robot Framework test result.
- AI-generated test drafts require human review before becoming official tests.

## Code conventions

- Code, identifiers and technical comments must be in English.
- Internship and user documentation may be written in French.
- Python public functions should use type hints.
- TypeScript must remain in strict mode.
- Prefer small components and services with explicit responsibilities.
- Do not add a production dependency without explaining its purpose.
- Update documentation and traceability when behavior changes.

## Expected final report

At the end of each task, provide:

- summary;
- files changed;
- commands executed;
- test results;
- limitations or unresolved issues;
- next recommended step;
- `git diff --stat`.

