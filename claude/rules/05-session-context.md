# Session Context File (Project-local, Git-ignored)

## Intent

Long sessions and subagent delegation can cause context drift/loss. To make work reproducible across tools (OpenCode, Oh-My-OpenCode, Claude Code, etc.), maintain a **single project-local session context file** that any agent can read/update.

This is **not** a replacement for global rules (`CLAUDE.md`, `rules/`, `skills/`). This is **per-session state** (current goal, decisions, progress, key findings).

## Standard paths (in the project repo)

- Session context (runtime, git-ignored):
  - `./.agent/session/CONTEXT.md`
- Optional archive (runtime, git-ignored):
  - `./.agent/session/archive/YYYYMMDD-HHMM-<slug>.md`

Notes:
- Keep this under the project root so any tool can access it.
- Treat it as **ephemeral runtime state**.

## Project .gitignore (recommended)

Add this to the **project** `.gitignore`:

```gitignore
.agent/session/*
!.agent/session/.gitkeep
```

Optionally commit an empty placeholder file:

- `./.agent/session/.gitkeep`

## Mandatory operating rules

### 1) Read-first

At the start of any non-trivial work:
- If `./.agent/session/CONTEXT.md` exists, **read it first** and follow its current decisions/constraints.
- If it does not exist, create it using the template below.

### 2) Update cadence

Update `CONTEXT.md` when any of the following happens:
- A decision is made (design choice, tradeoff, constraint)
- A scope change occurs
- A subagent returns results
- You discover a key file location / command / reproduction step
- You hand off work (pause/stop)

Additionally, for multi-turn / long-context work:
- At the end of each turn, update the **Rolling Summary** with a compressed recap:
  - Problem (now)
  - Solution snapshot
  - Next step

### 3) Keep it small (token safety)

- Prefer **bullet summaries**, not raw logs.
- Avoid pasting full stack traces; keep only the top error line and the relevant file/line.
- Hard cap guidance: ~200 lines. If it grows, compress:
  - Maintain a short **Rolling Summary** at the top
  - Move older details into `archive/` (1 file per checkpoint)

If you track tokens per work unit ("one plan"):
- Record only the **summary numbers** (e.g., total tokens/cost) per plan.
- Do NOT paste the full TokenScope output.

### 4) Security

Never write secrets into `CONTEXT.md`:
- API keys, tokens, cookies
- `.env` contents
- internal credentials or personal data

If sensitive info is required to reproduce:
- reference the **name** of the secret (e.g., `DATABASE_URL`) but not the value.

### 5) On-demand loading (skills / rule files)

When you load a domain skill or read a rule file on-demand:
- Record **what** was loaded (skill name or file path) and **why** (trigger) in `CONTEXT.md`.
- Do NOT paste the full loaded content; keep only the constraints/checklist items that matter.

## Subagent interoperability rule

When delegating work to subagents:
- Ensure the subagent prompt includes:
  - current Goal
  - known Constraints
  - key file paths / commands
  - what to write back (short summary)
- After results return, update `CONTEXT.md` with:
  - conclusions
  - evidence (file paths, commands)
  - risks/open questions
  - task identifiers (e.g., task_id / session_id) if available

This makes the workflow portable even if subagents are stateless.

## Copy-paste template: `./.agent/session/CONTEXT.md`

```md
# Session Context

## Rolling Summary (keep <= 10 lines)
- 

## Goal
- 

## Constraints (must-not-break)
- 

## Decisions (with rationale)
- 

## Progress
- [ ] 

## Key Findings (paths, commands, facts)
- 

## Subagent Outputs (summaries only)
- 

## Open Questions / Next Steps
- 
```
