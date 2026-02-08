# Manual skill loading policy (cross-tool)

## Goal

Keep the always-loaded rule surface small, while still applying the right domain playbooks.

**Policy**: When a domain is detected, **suggest** the relevant playbook skill(s) and **ask the user for confirmation** before loading them.

This must behave consistently across:
- OpenCode (via `opencode.json` `instructions`)
- Claude Code (via `~/.claude/` layout)

## Terminology

### Capability skills

Skills that add a new capability/tooling surface (e.g., browser automation).

- These may be **auto-loaded** only when:
  - the user explicitly requested that capability, or
  - a project policy says it is mandatory for the task.

### Playbook skills (domain guardrails)

Skills that are primarily checklists, conventions, and safety rules for a domain.

- These must be **manually confirmed** (user opt-in) before loading.

Examples (playbook skills in this repo):
- `backend-spring`
- `spring-feature`
- `python`
- `spark-pyspark`
- `pyspark-optimize`
- `external-skills`

## Rules (non-negotiable)

1) **Do not auto-load playbook skills based on heuristics/triggers.**
   - Triggers (file extensions, build files, keywords) are only signals to *suggest*.

2) **Ask for confirmation before loading any playbook skill.**
   - Ask early (before planning/edits) if the domain is clear.

3) **If the user says “no”, proceed without the skill.**
   - Follow the always-loaded core rules.
   - Do not repeatedly re-ask unless scope materially changes.

4) **If the user explicitly requests a specific skill by name**, load it without additional confirmation.

5) **Delegation must follow the same policy.**
   - Before using `delegate_task(... load_skills=[...])` with playbook skills, ask for confirmation.

## Korean confirmation templates

### Single skill

> 지금 작업이 `[DOMAIN]`(으)로 보입니다 (`[SIGNAL]`).
> `skill: [SKILL_NAME]` 를 로드해서 체크리스트/가드레일을 적용할까요?
> - 예: 로드하고 진행
> - 아니오: 로드 없이 진행

### Multiple skills

> 지금 작업이 `[DOMAIN]`(으)로 보입니다 (`[SIGNAL]`).
> 아래 스킬 중 어떤 것을 로드할까요?
> 1) `skill: [SKILL_A]`
> 2) `skill: [SKILL_B]`
> 3) 로드하지 않음

## Notes

- This policy exists to minimize context cost while keeping domain correctness available on-demand.
- Keep playbook skills short and actionable (checklists over tutorials).
