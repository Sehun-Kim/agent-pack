---
description: Use git worktree for parallel work (safe defaults)
---

# /worktree

Use `git worktree` to run tasks in parallel without constantly stashing/switching.

This agent-pack provides a small helper:

```bash
bash ~/agent-pack/scripts/git-worktree.sh --help
```

## Common flows

### Create a new worktree on a new branch

```bash
bash ~/agent-pack/scripts/git-worktree.sh new feat/my-branch
```

### Create from a specific base (e.g., origin/main)

```bash
bash ~/agent-pack/scripts/git-worktree.sh new fix/bug origin/main
```

### List worktrees

```bash
bash ~/agent-pack/scripts/git-worktree.sh list
```

### Remove a worktree (destructive)

```bash
bash ~/agent-pack/scripts/git-worktree.sh remove feat/my-branch --force
```

## Tip

Pair worktrees with tmux:

```bash
tmux new -s wt-feat
```
