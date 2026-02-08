---
description: Warn-only push safety checklist (review diff + confirm branch/remote + tests reminder)
---

Before pushing, do a quick, warn-only safety pass.

1) Ask permission, then run:
- `git status`
- `git branch --show-current`
- `git remote -v`

2) Ask permission, then run:
- `git diff`
- `git diff --staged`

3) Remind verification:
- Ask the user which command(s) to run (tests/typecheck/build). Suggest based on stack.

4) Warnings to call out:
- debug logs (`console.log`, prints)
- likely secrets patterns
