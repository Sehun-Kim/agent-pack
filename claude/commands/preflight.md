---
description: Warn-only preflight checklist before you commit/push (status/diff/tests/format/secrets/debug logs)
---

# /preflight

Goal: do a fast, **warn-only** preflight before commit/push.

## Checklist (do in order)

1) Git state
- Run:
  - `git status`
  - `git diff`
  - `git diff --staged`

2) Debug logs
- Scan for obvious debug prints (`console.log`, `print(`, `logger.debug`, etc.) in changed files.

3) Secrets
- Ensure no tokens/keys/passwords were added.
- If a secret might be exposed: stop, rotate, and scrub history.

4) Format/lint (pick what exists in this repo)
- TS/Node: `npx prettier -c .` / `npm test` / `npx tsc -p tsconfig.json --noEmit`
- Python: `ruff check .` / `ruff format --check .` / `pytest`
- Spring/Gradle: `./gradlew test` (and `./gradlew spotlessCheck` if configured)

5) Evidence
- If a session context file exists (`./.agent/session/CONTEXT.md`), record:
  - what you ran
  - results
  - any follow-ups

## Output format

- Report as:
  - ✅ OK
  - ⚠️ Warning (actionable)
  - ❓ Unknown (needs user input)
