---
description: Warn-only preflight checklist before commit/push (status/diff/tests/format/secrets/debug logs)
---

Run a warn-only preflight.

1) Ask permission, then run:
- `git status`
- `git diff`
- `git diff --staged`

2) Summarize warnings:
- leftover debug logs
- likely secrets

3) Ask which verification applies for this repo (pick one set):
- TS/Node: `npm test` + `npx tsc --noEmit` + prettier/eslint if present
- Python: `pytest` + `ruff check .`
- Spring/Gradle: `./gradlew test`

4) If `./.agent/session/CONTEXT.md` exists, remind to record the commands + results.
