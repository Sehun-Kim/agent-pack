---
description: Reminder: scan for secrets before commit/push
---

Warn-only secrets reminder:
- No API keys/tokens/passwords in diffs
- No private key blocks
- No .env contents committed

If a real secret is present: stop, rotate, scrub history.
