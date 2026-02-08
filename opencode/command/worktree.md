---
description: Use git worktree for parallel work (safe defaults)
---

Use `git worktree` to run tasks in parallel without constantly stashing/switching.

agent-pack helper:

1) Ask permission, then run:

```bash
bash ~/agent-pack/scripts/git-worktree.sh --help
```

2) Common flows:

```bash
bash ~/agent-pack/scripts/git-worktree.sh new feat/my-branch
bash ~/agent-pack/scripts/git-worktree.sh new fix/bug origin/main
bash ~/agent-pack/scripts/git-worktree.sh list
bash ~/agent-pack/scripts/git-worktree.sh remove feat/my-branch --force
```

Tip: pair with tmux (`/tmux-remind`).
