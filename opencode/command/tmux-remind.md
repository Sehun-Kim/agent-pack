---
description: Reminder: use tmux for long-running commands
---

If running a dev server/tests/build, recommend tmux for persistence + log access.

Suggested:

```bash
tmux new -s dev
tmux attach -t dev
```
