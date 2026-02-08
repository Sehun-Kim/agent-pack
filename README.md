# agent-pack

백엔드/데이터 개발자가 **터미널 기반 AI 코딩 에이전트(OpenCode, Claude Code 호환 레이아웃)** 를
여러 머신에서 **같은 규칙/스킬/정책**으로 쓰기 위한 “Source of Truth” 레포입니다.

이 레포는 프로젝트 코드가 아니라, 에이전트가 따라야 할 **전역 규칙(헌법/룰/스킬)** 과
OpenCode가 이를 읽도록 하는 **설치(심볼릭 링크 + 엔트리포인트 생성)** 를 제공합니다.

---

## 핵심 아키텍처 (한 장 요약)

**1) Source of Truth = 이 레포(Git으로 버전 관리)**

- 규칙/스킬: `claude/` 아래에 저장
- OpenCode 설정: `opencode/` 아래에 저장
- 외부 스킬 메타데이터(옵션): `skill-sources/` 아래에 저장

**2) 설치 스크립트가 “표준 위치”로 연결**

`scripts/install.sh` 가 아래 경로에 심볼릭 링크(또는 파일 생성)를 수행합니다.

- OpenCode 전역 설정: `~/.config/opencode/`
- Claude 호환 레이아웃: `~/.claude/`

**3) 런타임에는 OpenCode/Claude가 표준 위치를 읽는다**

- OpenCode는 `~/.config/opencode/opencode.json` 을 읽고,
  그 안의 `instructions`로 `~/.config/opencode/AGENTS.md` + `~/.claude/**` 를 로드하도록 구성됩니다.

---

## 디렉토리 구조

```text
agent-pack/
├── README.md
├── scripts/
│   └── install.sh                 # 설치(링크/엔트리포인트 생성)
├── opencode/
│   ├── opencode.jsonc             # OpenCode 전역 설정(install.sh가 링크)
│   ├── oh-my-opencode.jsonc        # oh-my-opencode 전역 설정(install.sh가 링크)
│   └── command/                    # OpenCode 슬래시 커맨드(예: /tokenscope)
├── claude/
│   ├── CLAUDE.md                   # 전역 헌법
│   ├── rules/                      # 세부 규칙(모듈)
│   ├── skills/                     # 반복 작업 스킬(레시피)
│   ├── commands/                   # Claude Code 슬래시 커맨드(레시피)
│   └── hooks/                      # Claude Code hooks 템플릿 (warn-only)
└── skill-sources/                  # (옵션) 외부 스킬 “메타데이터만”
```

---

## 설치 전 준비물

- macOS/Linux (Bash + 심볼릭 링크 사용)
- `git`
- OpenCode CLI: `opencode` 커맨드가 PATH에 있어야 함 *(agent-pack이 OpenCode 자체를 설치하진 않습니다)*
- (권장) Node.js + npm
  - TokenScope 토크나이저 vendor 의존성을 `install.sh`가 준비할 때 사용 (TokenScope를 안 쓰면 없어도 됨)

---

## 설치 방법 (최초 1회)

> 기본 경로는 `~/agent-pack` 을 가정합니다. 다른 위치에 둘 수도 있지만,
> **심볼릭 링크가 절대경로를 물기 때문에** 레포 위치를 바꾸면 `install.sh`를 다시 실행해야 합니다.

```bash
git clone <this-repo> ~/agent-pack
chmod +x ~/agent-pack/scripts/install.sh
~/agent-pack/scripts/install.sh
```

### install.sh가 하는 일 (정확히)

`scripts/install.sh`는 기존 파일이 있으면 `*.bak.<timestamp>`로 백업한 뒤 연결합니다.

1) OpenCode 설정 연결

- `agent-pack/opencode/opencode.jsonc` → `~/.config/opencode/opencode.json`
- `agent-pack/opencode/oh-my-opencode.jsonc` → `~/.config/opencode/oh-my-opencode.json`
- `agent-pack/opencode/command/` → `~/.config/opencode/command/` *(디렉토리 전체를 백업 후 교체)*

추가로, OpenCode에서 Claude Code hooks에 가까운 UX를 내기 위해:
- `agent-pack/opencode/plugins/agent-pack-reminders.js` → `~/.config/opencode/plugins/agent-pack-reminders.js`
  - `git commit/push`, 빌드/테스트 실행 전 tmux/preflight/worktree 리마인더를 **시스템 프롬프트에 주입**합니다(warn-only).

2) 외부 스킬 소스(메타데이터) 연결(옵션)

- `agent-pack/skill-sources/` → `~/.config/opencode/skill-sources/`

2-1) 외부 스킬 설치(글로벌; 기본)

- `skill-sources/global.lock.json`에 pin+sha256로 고정된 스킬을
  `~/.config/opencode/skills/`로 설치합니다.
  (설치/해시 검증/기본 보안 스캔은 `scripts/skills_install.py`)

2-1) Superpowers 기본 설치(OpenCode)

- `obra/superpowers` 를 `~/.config/opencode/superpowers/` 에 설치하고,
  `~/.config/opencode/plugins/superpowers.js` 및 `~/.config/opencode/skills/superpowers/` 를 연결합니다.
- 보안상 **commit pin + sha256 검증**을 수행하며, 실패 시 이 단계만 스킵합니다.

3) OpenCode 규칙 엔트리포인트 생성

- `~/.config/opencode/AGENTS.md` *(install.sh가 생성하는 일반 파일)*
  - 여기에는 `agent-pack/claude/CLAUDE.md`, `agent-pack/claude/rules/*`, `agent-pack/claude/skills/`가 나열됩니다.

4) Claude 호환 레이아웃 연결

- `agent-pack/claude/CLAUDE.md` → `~/.claude/CLAUDE.md`
- `agent-pack/claude/rules/` → `~/.claude/rules/`
- `agent-pack/claude/skills/` → `~/.claude/skills/`
- `agent-pack/claude/commands/` → `~/.claude/commands/`
- `agent-pack/claude/hooks/` → `~/.claude/hooks/`

추가로, Claude Code hooks를 바로 쓸 수 있도록:
- `~/.claude/settings.json` 이 없으면 install.sh가 **warn-only hooks 설정 파일을 생성**합니다.
- 이미 `~/.claude/settings.json` 이 있으면 **절대 덮어쓰지 않고**, 수동 merge 안내만 출력합니다.

5) 외부 스킬 캐시 디렉토리 생성

- `~/.claude/skills-external/` *(캐시; Git에 커밋하지 않는 영역)*

6) (옵션) TokenScope vendor 토크나이저 준비

- `~/.config/opencode/plugin/vendor/node_modules/...`
- npm이 있으면 필요한 패키지를 vendor에 설치하고, 없으면 Node.js/npm 설치 후 재실행을 안내합니다.

---

## 설치 후 확인(체크리스트)

```bash
ls -l ~/.config/opencode/opencode.json
ls -l ~/.config/opencode/oh-my-opencode.json
ls -l ~/.config/opencode/command

ls -l ~/.claude/CLAUDE.md
ls -l ~/.claude/rules
ls -l ~/.claude/skills

sed -n '1,80p' ~/.config/opencode/AGENTS.md
```

---

## OpenCode / Claude Code 호환성

### OpenCode

- `~/.config/opencode/opencode.json`(= 이 레포의 `opencode/opencode.jsonc` 링크)이
  `instructions`로 아래를 읽도록 구성되어 있습니다.
  - `~/.config/opencode/AGENTS.md`
  - `~/.claude/CLAUDE.md`
  - `~/.claude/rules/**/*.md`
- 즉, **규칙/스킬의 Source of Truth는 `claude/`이고**, OpenCode는 이를 그대로 로드합니다.

### Claude Code (또는 Claude 계열 툴)

- 규칙/스킬을 `CLAUDE.md + rules/ + skills/` 레이아웃으로 유지하고,
  설치 시 `~/.claude/`로 연결합니다.
- Claude Code가 `~/.claude` 레이아웃을 지원한다면 **별도 변환 없이 재사용**할 수 있습니다.
  (지원 범위가 다르다면, 최소한 동일한 파일/구조를 기반으로 옮겨갈 수 있도록 설계되어 있습니다.)

---

## 사용 방법

```bash
cd <프로젝트 디렉토리>
opencode
```

### (권장) 세션 컨텍스트 파일

긴 작업/하위 에이전트 위임 시 컨텍스트 유실을 줄이려면, 프로젝트에 아래 파일을 두고(로컬 갱신), 에이전트가 읽고 업데이트하도록 운영합니다.

- `./.agent/session/CONTEXT.md` (gitignore 권장)

표준 규칙/템플릿은 `claude/rules/05-session-context.md` 를 따릅니다.

초기 권한 설정은 안전 우선으로 되어 있습니다 (`edit: ask`, `bash: ask`).

### (옵션, 권장) Warn-only 자동화 (hooks/commands)

hackathon 스타일 워크플로우에서 효과가 큰 "경고용 가드"를 제공합니다.

- Claude Code:
  - hooks 템플릿: `~/.claude/hooks/hooks.json`
  - 커맨드: `~/.claude/commands/` (예: `/preflight`, `/push-safe`, `/verify`)
- OpenCode:
  - 커맨드: `~/.config/opencode/command/` (예: `/preflight`, `/push-safe`, `/verify`)

기본 정책은 **차단 없이 경고만** 합니다. 자세한 내용은 `claude/rules/06-automation-warn-hooks.md` 참고.

#### 무엇을 “직접 호출”하고, 무엇을 “자동으로 뜨게” 하나?

**직접 호출(두 툴 공통, 권장 루틴)**

- 긴 실행(서버/빌드/테스트) 전: `/tmux-remind`
- 커밋/푸시 전: `/preflight`
- 푸시 직전 체크: `/push-safe`
- 시크릿 의심/검토: `/secrets-remind`
- 디버그 로그 정리: `/debuglog-remind`
- 무엇을 검증해야 할지 정리: `/verify`
- 병렬 작업(여러 이슈 동시 처리): `/worktree`

**자동(Claude Code만: hooks 기반, warn-only)**

- 긴 커맨드 실행 전 tmux 리마인드
- `git push` 실행 전 리마인드
- 파일 편집 후 `console.log`/시크릿 패턴 경고
- `git switch -c` / `git checkout -b` 시 worktree 권장 경고
- 턴 종료 시 `/preflight` 리마인드

OpenCode는 Claude Code hooks를 실행하지 않으므로, OpenCode에서는 위 슬래시 커맨드를 **필요할 때 직접 호출**하는 방식이 기본입니다.

### (옵션, 권장) git worktree로 병렬 작업

여러 작업을 동시에 굴릴 때는 branch switching/stash 대신 `git worktree`를 권장합니다.

- helper: `~/agent-pack/scripts/git-worktree.sh`
- 커맨드: OpenCode `/worktree`, Claude Code `/worktree`

### 프로젝트별 오버라이드 (필요할 때만)

- oh-my-opencode 설정 오버라이드: `<project>/.opencode/oh-my-opencode.json`
- 외부 스킬 소스 오버라이드: `<project>/.opencode/skill-sources.json` (schema는 `skill-sources/README.md` 참고)

---

## 업데이트/유지보수

일반적으로는 `~/agent-pack`에서 `git pull`만 해도 됩니다.
(심볼릭 링크는 “파일 경로”를 가리키므로 레포 위치가 그대로면 자동 반영)

### AGENTS.md refresh (룰/스킬 파일을 추가/삭제했을 때)

`~/.config/opencode/AGENTS.md`는 **생성 파일**이라,
`claude/rules/*.md`에 파일을 새로 추가/삭제한 경우에는 목록을 갱신하려면 refresh가 필요합니다.

```bash
bash ~/agent-pack/scripts/refresh-agents.sh
```

OpenCode에서는 설치 후 `/refresh-agents` 커맨드로도 실행할 수 있습니다.

`install.sh`를 다시 실행해야 하는 경우:

- 새로운 PC에서 처음 설치
- `~/agent-pack`의 위치를 바꿈(심볼릭 링크 경로가 바뀜)
- `scripts/install.sh` 자체를 수정
- `opencode/` 설정 경로/구조 변경
- TokenScope vendor 의존성이 깨졌거나 Node.js/npm 설치 후 vendor를 준비해야 할 때

재설치:

```bash
~/agent-pack/scripts/install.sh
```

---

## (옵션) TokenScope

OpenCode 세션 토큰/비용을 보고 싶으면 `/tokenscope`, `/tokenscope-ko`를 사용합니다.

- 커맨드 정의: `opencode/command/`
- 플러그인: `opencode/opencode.jsonc`의 `plugin` 항목
- 참고: https://github.com/ramtinJ95/opencode-tokenscope

---

## (옵션) 외부 스킬

외부 스킬은 **메타데이터만 Git에** 두고, 실제 스킬 본문은 로컬 캐시에 저장하는 방식을 권장합니다.

- 메타데이터: `skill-sources/` (자세한 스키마: `skill-sources/README.md`)
- 정책/운영: `claude/skills/external-skills/SKILL.md`

---

## 주의사항

- 이 레포에는 **비밀 정보(API 키, 토큰, .env 등)를 절대 커밋하지 않습니다.**
- 전역 규칙은 보수적으로 유지하고, 프로젝트별 특이 사항은 프로젝트 로컬 규칙으로 처리하는 것을 권장합니다.
