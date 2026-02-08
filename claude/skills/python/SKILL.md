---
name: python
description: Work safely in Python codebases (tooling, typing, structure, data safety).
---

## Checklist (must do)
- Follow the project's existing tooling (pytest, ruff, black, mypy, etc.).
- Prefer type hints for public functions and complex data structures.
- Keep reusable logic in `.py` modules.
- Keep notebooks thin: exploration/visualization only; extract reusable logic to modules.
- Never print secrets/env vars; for large data, sample/limit before loading everything.
