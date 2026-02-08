# skill-sources

Global + project override manifests for external skills.

This folder is intentionally **metadata-only**:

- Manifests / locks are committed
- Downloaded skill contents are cached locally and NOT committed

## Schema (v1)

### `global.sources.json`

```json
{
  "version": 1,
  "policy": {
    "allowlistDomains": ["github.com", "skills.sh", "raw.githubusercontent.com"],
    "mode": "allowlist"
  },
  "sources": [
    {
      "id": "skills-sh",
      "type": "skills_sh",
      "url": "https://skills.sh"
    }
  ]
}
```

### Project override: `.opencode/skill-sources.json`

Same schema, but:

- `policy.allowlistDomains` must be a subset of global
- every `sources[*].url` domain must be globally allowed

### Locks

Locks are intentionally simple and tool-agnostic.

```json
{
  "version": 1,
  "skills": [
    {
      "name": "some-skill",
      "sourceId": "skills-sh",
      "ref": "vercel-labs/agent-skills@<40-hex-commit>",
      "sha256": "<required>"
    }
  ]
}
```

## Validation

Validate project manifests and locks against global policy:

```bash
python3 scripts/skills_validate.py \
  --global skill-sources/global.sources.json \
  --project /path/to/project/.opencode/skill-sources.json \
  --project-lock /path/to/project/.opencode/skills.lock.json \
  --require-lock
```
