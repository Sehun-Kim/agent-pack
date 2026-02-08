# agent-pack Claude Code hooks (warn-only)

This folder ships a **warn-only** hooks preset inspired by the hackathon workflow thread.

## What it does

- Reminds to use **tmux** for long-running commands
- Reminds to review before **git push**
- Warns if `console.log(...)` appears in JS/TS files after edits
- Warns on **likely secret patterns** after edits
- Adds an end-of-turn reminder to run a preflight checklist

## How Claude Code loads hooks

Claude Code reads hooks from your `~/.claude/settings.json`.

This repo provides `claude/hooks/hooks.json` in Claude Code settings format:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "hooks": {
    "PreToolUse": [ ... ],
    "PostToolUse": [ ... ],
    "Stop": [ ... ]
  }
}
```

## Installation behavior (agent-pack)

- `scripts/install.sh` links this folder to: `~/.claude/hooks`
- If `~/.claude/settings.json` does **not** exist, install.sh will create it with these hooks enabled.
- If `~/.claude/settings.json` already exists, install.sh will **not** modify it; you should merge the `hooks` block manually.

## Notes

- These hooks are **warnings only** (no blocking), but they do run small Node one-liners to print warnings / scan edited file contents.
- Secret detection is heuristic and can false-positive.
