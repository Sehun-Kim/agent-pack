---
description: Reminder: use tmux for long-running commands
---

# /tmux-remind

If you're about to run long commands (dev server/tests/build), tmux keeps logs + lets you detach.

Suggested:

```bash
tmux new -s dev
```

In another terminal:

```bash
tmux attach -t dev
```
