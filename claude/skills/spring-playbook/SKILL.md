---
name: spring-playbook
description: Spring umbrella playbook. Use to choose the right Spring skill and apply safe defaults.
---

# spring-playbook

Use this when working in a Spring Boot codebase (Java/Kotlin, Gradle/Maven).

## Goal

- Keep Spring work consistent, testable, and human-reviewable.
- Use the smallest change that passes tests.

## Which Spring skill to load?

1) **General Spring guardrails / reviews / architecture**
   - Load: `skill: backend-spring`
   - Use when: transactions, error handling, layering, controllers/services/repos, integration tests.

2) **Implementing a feature end-to-end (controller/service/repo + tests)**
   - Load: `skill: spring-feature`
   - Use when: adding a new endpoint/feature that needs tests.

## Defaults (apply even without loading other skills)

- Plan → Tests → Decompose (Human-first)
- For behavior changes: add/update tests (one test = one reason to fail)
- Never log/print secrets/PII
- Prefer `git worktree` for parallel tasks
