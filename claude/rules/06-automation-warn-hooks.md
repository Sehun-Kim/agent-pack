# Automation (Warn-only hooks + preflight commands)

## Intent

Borrow hackathon-proven ergonomics (hooks/commands) **without blocking** actions.

Automation in this repo is **warn-only**:
- Never hard-block a command (no forced exits)
- Prefer reminders and short checklists

## Supported surfaces

### Claude Code

- Hooks live under: `~/.claude/settings.json` (user-level)
- agent-pack ships templates at: `~/.claude/hooks/hooks.json`
- agent-pack also links commands at: `~/.claude/commands/*`

Expected behavior:
- PreToolUse: tmux + push reminders
- PostToolUse: warn on console.log / likely secrets
- Stop: end-of-turn reminder to run `/preflight`

### OpenCode

- Commands live at: `~/.config/opencode/command/*`
- Use these for the same warn-only flows:
  - `/preflight`
  - `/push-safe`
  - `/verify`
  - `/tmux-remind`
  - `/secrets-remind`
  - `/debuglog-remind`

## Operating rules

- Treat hook output as **warnings**:
  - If a warning indicates a real secret: stop and escalate (rotate + remove + scrub history)
  - If a warning is a false positive: note it and continue
- For non-trivial changes, keep following `00-core.md`:
  - plan first
  - include verification strategy
- Prefer recording evidence in `./.agent/session/CONTEXT.md` when present.
