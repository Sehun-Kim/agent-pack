---
description: Warn-only push safety checklist (review diff + confirm branch/remote + tests reminder)
---

# /push-safe

Goal: reduce push mistakes without blocking.

## Checklist

1) Confirm branch + remote
- Run:
  - `git status`
  - `git branch --show-current`
  - `git remote -v`

2) Review changes
- Run:
  - `git diff`
  - `git diff --staged`

3) Remind verification
- Ask: “Which verification command(s) should we run for this repo?”
- Suggest based on stack:
  - TS: `npm test` or `pnpm test`, plus `npx tsc --noEmit`
  - Python: `pytest`
  - Gradle: `./gradlew test`

4) Common footguns
- Any `console.log` / debug code left?
- Any likely secrets added?
