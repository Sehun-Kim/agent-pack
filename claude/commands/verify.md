---
description: Warn-only verification reminder (tests/build/typecheck) for TS/Python/Spring
---

# /verify

Goal: pick and run the minimal verification for the current change.

## Step 1: Identify stack (ask if unclear)
- TS/Node / Python / Spring/Gradle

## Step 2: Choose a minimal verification set
- TS/Node (typical):
  - `npm test` (or `pnpm test` / `yarn test`)
  - `npx tsc --noEmit`
- Python (typical):
  - `pytest`
  - `ruff check .`
- Spring/Gradle (typical):
  - `./gradlew test`

## Step 3: Record evidence
- Capture:
  - command(s)
  - exit code
  - any failing test summary lines
