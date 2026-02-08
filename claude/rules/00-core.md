# Core Rules (Agent Stability & Safety)

## Prime Directive: Plan → Tests → Decompose (Human-first)
- All development starts with a plan, is validated by tests, and stays decomposed into small units.
- Plan before editing: define scope, responsibility boundaries, and expected inputs/outputs.
- Derive test units from the plan **before** implementation (tests are a design artifact, not an afterthought).
- Keep tests minimal: one behavior per test; one clear reason to fail.
- Keep code aligned to test units. If change impact becomes hard to predict, split/extract until it is.
- Any behavior change must update tests (fix existing tests + add new ones). If tests don’t change, explicitly justify why.

## Planning First (Mandatory)
- For any non-trivial change, explicitly propose a plan before editing.
- The plan must include:
  - acceptance criteria (what “done” means, edge cases)
  - problem decomposition: break the requirement into small, ordered problem units (prefer 3–7)
  - a small-step breakdown (3–7 steps): each step should be independently reviewable + verifiable
  - solution decomposition: map each step to concrete code units (classes/functions/modules) and responsibilities
  - expected inputs/outputs (APIs, data shapes, side-effects)
  - files/classes to be modified
  - what will NOT be modified
  - verification strategy (tests or commands; ideally mapped to steps)

## Testing Requirement (Mandatory)
- For behavior changes, **test code** is required (add/update automated tests).
- Derive tests from the plan. If you can’t describe a test, the design is incomplete.
- Prefer the smallest test unit: one test should fail for one clear reason.
- The plan must state which test file(s)/case(s) will be added/updated and the exact command(s) to run.
- If adding/updating tests is not feasible, stop and ask the user for approval before proceeding.
- If behavior changed but tests didn’t, treat it as suspicious; either add/adjust tests or explain why tests are unaffected.

## Design Rationale (Mandatory)
- After implementing changes, always explain:
  - why this approach was chosen
  - which alternatives were considered (if any)
  - why they were rejected
- Keep explanations concise and technical.

## Change Scope Control
- Prefer the smallest possible change that satisfies requirements.
- Never mix refactoring with feature changes unless explicitly requested.
- If the required change seems large, stop and propose decomposition first.

## Parallel Work (Recommended)
- For parallel tasks (multiple features/bugs in flight), prefer `git worktree` over frequent branch switching.
- Keep each worktree scoped to one change and verify independently.

## Context Preservation
- Avoid modifying large files or classes (>300 lines) in a single step.
- If a class/module has multiple responsibilities:
  - propose extraction or separation before adding more logic
  - or explicitly justify why adding logic is acceptable

## Token & Context Safety
- Assume the agent may lose context in very large files or diffs.
- Prefer:
  - multiple small commits/diffs
  - focused changes per class or module
- If a change risks context loss, pause and ask for confirmation.

### Token Efficiency Principles (progressive disclosure)
- Treat tokens as a memory budget: avoid wide reads (entire repos, huge logs) unless required.
- Prefer deterministic, versioned scripts for repeated/critical logic (formatting, validation, generation) over re-explaining it in prompts.
- If a domain playbook skill seems relevant, **suggest it and ask for user confirmation** before loading it.
- If domain is ambiguous: ask up to **2** clarifying questions, then proceed.

### On-demand skill routing (default)

These are **suggested** playbook skills by domain. Per `rules/07-manual-skill-loading.md`, ask the user for confirmation before loading.

- Spring/Java/Kotlin backend work → suggest `backend-spring`
- Spring umbrella routing → suggest `spring-playbook`
- Python work → suggest `python`
- Spark/PySpark work → suggest `spark-pyspark`
- External skill sources / allowlists / locks → suggest `external-skills`

Trigger signals (cheap, deterministic): if any appear in the user request or target file paths, **suggest** the skill before planning/executing and ask for confirmation.
- `backend-spring`: `pom.xml`, `build.gradle*`, `src/main/java`, `src/main/kotlin`, `*.java`, `*.kt`, `@SpringBootApplication`, `@RestController`, `@Transactional`
- `python`: `*.py`, `pyproject.toml`, `requirements.txt`, `pytest`, `ruff`, `black`, `mypy`
- `spark-pyspark`: `pyspark`, `SparkSession`, `spark-submit`, `spark.sql`, `delta`
- `external-skills`: `skill-sources/`, `.opencode/skill-sources.json`, `.opencode/skills.lock.json`, `skills_validate.py`

## Communication (user questions)
- When asking the user for a decision/confirmation, ask in **Korean**. Keep code identifiers/commands in their original form.

## Output Requirements
- Always summarize:
  - what changed
  - why it changed
  - how to verify it

### Long-context recap (to prevent forgetting)
- For multi-turn / long-context work, include a compressed recap at the end of each turn:
  - **Problem (now)**: 1 line
  - **Solution snapshot**: 1–2 lines
  - **Next step**: 1 line
- Keep it short; do not paste raw logs.
