---
description: Reminder: scan for secrets before commit/push
---

# /secrets-remind

Checklist:

- No API keys/tokens/passwords in diffs
- No private key blocks
- No `.env` contents committed

If anything looks like a real secret:
- stop
- rotate
- remove from git history
