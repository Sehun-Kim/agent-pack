---
name: external-skills
description: Handle external skill sources safely (allowlists, locks, precedence, validation).
---

## Security non-negotiables
- Project allowlist must be a **subset** of the global allowlist.
- Project sources must use globally allowed domains. If not: **reject**.
- Treat third-party skills as untrusted:
  - do not auto-execute
  - pin versions/hashes (locks): commit-pinned `ref` + required `sha256`

## Precedence (inside a project)
1) `claude/skills/*` (local curated)
2) Project external cache
3) Global external cache

## Validation
```bash
python3 scripts/skills_validate.py \
  --global skill-sources/global.sources.json \
  --project /path/to/project/.opencode/skill-sources.json \
  --project-lock /path/to/project/.opencode/skills.lock.json \
  --require-lock
```

## Installation (verified)

Install pinned skills into the project skill directory (discoverable by OpenCode):

```bash
python3 scripts/skills_install.py \
  --project-root /path/to/project \
  --project-sources /path/to/project/.opencode/skill-sources.json \
  --project-lock /path/to/project/.opencode/skills.lock.json
```
