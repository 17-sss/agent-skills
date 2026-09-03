# Agent Skills

[English](README.md) | 한국어

여러 AI 코딩 에이전트에서 반복해서 사용할 워크플로를 작고 독립적인 스킬로 모아 둔 저장소입니다. 공통 도구 위에서 동작하는 에이전트 중립 스킬과 Codex의 Plan, Goal, Review, subagent 기능을 직접 활용하는 Codex 특화 스킬을 함께 관리합니다.

![Agent Skills](assets/skill-visuals/agent-skills-dino-hero.png)

> 각 스킬은 단독 설치를 기본으로 합니다. 외부 댓글 작성, push, PR 생성, 브라우저 설치처럼 사용자 환경이나 외부 상태를 바꾸는 작업은 해당 스킬의 승인 규칙을 따릅니다.

## 빠른 시작

전체 카탈로그를 보고 대화형으로 설치합니다.

```bash
npx skills add https://github.com/17-sss/agent-skills
```

선택 화면은 Codex 의존 워크플로와 공통 스킬을 구분하고, 공통 스킬은 용도나 실험적 상태에 따라 표시합니다.

- `Codex`: Codex의 native Plan, Goal, Review와 subagent 계약을 사용하는 명시 호출형 워크플로
- `Planning`: 요구사항 인터뷰와 명세 준비
- `Design`: UI 구현·개선과 기준 화면 재현
- `Git Workflow`: 커밋, PR 생성과 PR 리뷰
- `Project Memory`: 현재 작업 인수인계와 장기 프로젝트 이력
- `Experimental`: 아직 검증 중인 실험적 스킬로, 현재는 `godot-dev-loop`가 해당하며 동작과 인터페이스가 바뀔 수 있음

`Codex`를 제외한 그룹은 Codex를 포함한 여러 호환 에이전트에서 사용할 수 있는 공통 스킬입니다. `Experimental`은 성숙도 표시이며 특정 에이전트 의존성을 뜻하지 않습니다.

`skills` CLI는 현재 [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)의 명시적인 스킬 목록을 TUI 그룹 정보로 읽습니다. 그룹은 선택 화면 표시만 바꾸며 설치 디렉터리를 결정하거나 개별 스킬에 Claude Code runtime 의존성을 추가하지 않습니다. 검토한 의존성 표는 [스킬 분류와 설치](docs/skill-classification.md)에 있습니다.

`npx skills list --global`은 설치 당시 저장한 그룹명을 읽습니다. 변경된 분류가 저장소에 공개된 뒤 해당 스킬을 다시 추가하면 그룹명이 갱신됩니다. 카탈로그 수정만으로 기존 설치 목록이 바뀌지는 않습니다.

설치 대상 에이전트는 `--agent`로 별도 선택합니다. 현재 CLI에서 Codex의 프로젝트 스킬은 `.agents/skills/`, 전역 스킬은 `~/.codex/skills/`에 설치됩니다.

```bash
npx skills add https://github.com/17-sss/agent-skills --skill reviewed-plan --agent codex
npx skills add https://github.com/17-sss/agent-skills --skill reviewed-plan --agent codex --global
```

필요한 스킬 하나만 설치할 수도 있습니다.

```bash
npx skills add https://github.com/17-sss/agent-skills --skill <skill-name>
```

예를 들어 `design-loop`만 설치하려면 다음 명령을 실행합니다.

```bash
npx skills add https://github.com/17-sss/agent-skills --skill design-loop
```

설치 후 새 에이전트 작업을 시작하면 갱신된 스킬 탐색 결과를 안정적으로 사용할 수 있습니다. 실제 실행 계약은 각 `skills/<skill-name>/SKILL.md`에 있습니다.

## 한눈에 보기

| 그룹 | 호환성 | 스킬 | 이런 때 사용합니다 |
| --- | --- | --- | --- |
| Design | 공통 | [`design-loop`](skills/design-loop/SKILL.md) | UI를 실제 렌더 결과로 반복 개선할 때 |
| Experimental | 공통 | [`godot-dev-loop`](skills/godot-dev-loop/SKILL.md) | Godot 게임을 durable state, 렌더 캡처와 fresh agent iteration으로 다듬을 때 |
| Planning | 공통 | [`spec-interview`](skills/spec-interview/SKILL.md) | 구현 전에 모호한 요구사항을 한 질문씩 명확히 할 때 |
| Design | 공통 | [`visual-match`](skills/visual-match/SKILL.md) | 승인된 이미지나 URL과 구현 화면을 엄격히 맞출 때 |
| Project Memory | 공통 | [`handoff-memory`](skills/handoff-memory/SKILL.md) | 저장소나 워크스페이스의 HANDOFF를 만들고 이어갈 때 |
| Project Memory | 공통 | [`project-chronicle`](skills/project-chronicle/SKILL.md) | 저장소 근거에서 장기 프로젝트 역사를 복원하고 계속 기록할 때 |
| Git Workflow | 공통 | [`github-pr-review`](skills/github-pr-review/SKILL.md) | `gh`와 GitHub API로 PR을 검토하고 리뷰를 게시할 때 |
| Git Workflow | 공통 | [`github-pr-publish`](skills/github-pr-publish/SKILL.md) | 현재 브랜치를 안전하게 push하고 PR로 공개할 때 |
| Git Workflow | 공통 | [`commit-helper`](skills/commit-helper/SKILL.md) | 저장소 규칙과 staged diff에 맞는 커밋을 만들 때 |
| Codex | Codex 특화 | [`reviewed-plan`](skills/reviewed-plan/SKILL.md) | Planner, Architect, Critic을 거친 구현 계획이 필요할 때 |
| Codex | Codex 특화 | [`completion-loop`](skills/completion-loop/SKILL.md) | 명확한 Goal을 검증 가능한 완료까지 밀어붙일 때 |
| Codex | Codex 특화 | [`milestone-runner`](skills/milestone-runner/SKILL.md) | 큰 작업을 재시작 가능한 순차 milestone로 실행할 때 |
| Codex | Codex 특화 | [`review-gate`](skills/review-gate/SKILL.md) | 고위험 변경을 공개하거나 병합하기 전에 엄격한 두-lane gate를 실행할 때 |

## 공통 스킬

특정 에이전트의 전용 명령에 의존하지 않는 워크플로입니다. Codex에서도 사용할 수 있으며, 다른 호환 에이전트에서는 제공되는 브라우저, 셸, GitHub, 이미지 도구에 맞춰 동작합니다.

### design-loop

UI 구현을 `inspect → implement → render → review → interact → fix → verify` 루프로 다듬습니다. 데스크톱·모바일 화면, 주요 상호작용, 시각적 회귀를 실제 렌더 결과로 확인합니다. Product Design 워크플로를 사용할 수 있고 디자인 탐색이 필요한 작업이면 선택적 가속기로 사용한 뒤 같은 구현·검증 루프로 돌아옵니다.

- 기존 디자인 문서, 토큰, 컴포넌트와 저장소 실행 명령을 먼저 확인합니다.
- 브라우저나 screenshot 수단이 없으면 사용자 승인 후 격리된 Chromium fallback을 제안합니다.
- 렌더 증거 없이 시각적 완성이나 상호작용 성공을 주장하지 않습니다.
- Product Design은 선택 사항으로 유지하며, 독립 실행을 위해 설치하거나 필수 의존성으로 만들지 않습니다.

사용 예시:

```text
Use $design-loop to polish the checkout screen. Preserve behavior, inspect desktop and mobile renders, test the primary flow, and iterate on major visual issues.
```

### godot-dev-loop

> **Experimental · 실험적 스킬:** 아직 검증 중인 워크플로이며 동작과 인터페이스가 바뀔 수 있습니다.

Godot 4.x playable slice를 deterministic state entry, 실제 창을 통한 PNG 캡처, native image inspection, 저장소 소유 handoff state와 의도적으로 fresh한 agent process로 구현하고 다듬습니다.

- 자율 구현 전에 세 가지 핵심 질문으로 짧은 game brief와 실행 가능한 `docs/DESIGN.md`를 확정합니다.
- 실제 main scene을 바꾸지 않고 `DESIGN`, `STATUS`, 사용자 소유 `feedback/INBOX`와 격리된 Godot capture harness를 bootstrap합니다.
- 한 번의 명시적 import, non-headless 렌더 캡처와 새 PNG의 실제 검토가 모두 끝나야 visual success로 인정합니다.
- disposable process마다 하나의 coherent improvement만 처리하고 DESIGN 완료, blocker, 선택적 iteration 한도 또는 반복 runner failure에서 안전하게 멈춥니다.
- 생성된 Bash loop는 macOS, Linux와 호환 Unix-like 환경용입니다. Claude Code와 Codex adapter는 선택적 편의 기능이며 custom executable adapter도 지원합니다.

사용 예시:

```text
Use $godot-dev-loop to bootstrap this Godot 4 project, establish the game brief and stop criteria, prove real-window capture with an inspected PNG, and prepare bounded fresh-agent iterations. Do not launch the autonomous loop until visual QA is ready.
```

### spec-interview

구현 전에 저장소 사실을 확인하고, 사용자가 결정해야 하는 가장 중요한 질문을 한 번에 하나씩 물어 실행 가능한 요구사항 명세를 만듭니다.

- 인터뷰와 저장소 조사를 non-mutating 상태로 유지합니다.
- 도구로 확인 가능한 사실을 사용자에게 되묻지 않습니다.
- 선택 범위가 명확한 결정은 가능한 경우 agent native choice control로 보여주고, 사용할 수 없으면 같은 2~3개 선택지와 custom-answer 항목을 번호 목록으로 표시합니다.
- 답변 범위가 열린 질문에는 억지로 선택지를 만들지 않고 자유응답을 사용합니다.
- scope, non-goal, 제약과 testable completion criteria가 충분할 때 종료합니다.
- readiness gate를 통과한 뒤에도 현재 작업에 표시된 최적의 workflow만 선택적으로 추천하며, 필수화·설치·실행하지 않습니다.

사용 예시:

```text
Use $spec-interview to clarify organization-level API keys for this app. Inspect the existing model first, ask one material decision at a time, and do not implement anything yet.
```

### visual-match

승인된 screenshot, 생성 이미지 또는 live URL을 기준으로 동일한 viewport와 UI state를 반복 캡처하며 구현을 맞춥니다.

- semantic visual review를 우선하고 pixel diff는 위치를 찾는 보조 증거로만 사용합니다.
- 승인된 viewport와 state마다 anchored `visual_similarity_percent`를 계산하고, 최저 점수 `90+`와 blocking·major 차이 없음 조건을 함께 요구합니다.
- live reference는 기본적으로 읽기 전용이며 별도 승인 없이 외부 상태를 바꾸지 않습니다.
- 렌더러가 없으면 승인 기반 Chromium fallback을 제안하고, 사용할 수 없으면 수정 전에 `BLOCKED`로 종료합니다.

사용 예시:

```text
Use $visual-match to match the attached checkout screenshot at desktop and mobile viewports, preserve the purchase flow, report the lowest visual similarity score, and explain every remaining difference.
```

### handoff-memory

저장소, 여러 저장소를 포함한 워크스페이스, 또는 개별 workstream의 공유 HANDOFF 문서를 만들고 검증하고 이어갑니다.

- 저장소는 `docs/HANDOFF.md`, 워크스페이스는 `_memory/HANDOFF.md`를 기본값으로 사용합니다.
- 완료된 상태는 필요할 때 timestamp snapshot으로 보존합니다.
- 변경 가능한 프로젝트 기억을 에이전트 개인 설정 폴더가 아니라 Git으로 추적 가능한 위치에 둡니다.
- HANDOFF 관리는 독립적으로 완결하고, 압축한 내용에 장기 이력이 필요할 때만 `$project-chronicle`을 가용성 확인 및 사용자 선택 기반 후속 작업으로 제안합니다.

사용 예시:

```text
Use $handoff-memory to refresh the canonical handoff for this repository, preserve the completed milestone as a snapshot, and validate the final document.
```

### project-chronicle

Git, 저장소 문서, 현재 코드와 필요한 경우의 짧은 사용자 확인을 바탕으로 장기 프로젝트 역사를 복원하고 유지합니다.

- 기존 프로젝트의 근거를 커밋 나열이 아니라 의미 있는 기간과 workstream으로 통합합니다.
- chronicle 실행마다 가벼운 log 기록을 남기고, 장기 서사가 바뀔 때만 timeline과 상세 entry를 갱신합니다.
- 검증된 사실, 근거 있는 추정과 미확인 역사를 구분하고 현재 HANDOFF 상태와 역사적 배경을 분리합니다.
- 기존 HANDOFF는 선택적인 시점별 근거로만 사용하며, 역사를 복원하거나 유지하기 위해 `handoff-memory`를 요구하지 않습니다.

사용 예시:

```text
Use $project-chronicle to reconstruct this repository's history from Git and current docs, group repeated work into explicit periods, and mark any rationale that cannot be verified.
```

### github-pr-review

`gh`, 로컬 Git, 테스트와 GitHub API를 이용해 공개·비공개 PR을 검토하고 사용자 계정으로 리뷰를 게시합니다.

- PR URL, `owner/repo#123`, PR 번호와 현재 브랜치 PR을 지원합니다.
- 인증 계정과 접근 범위를 확인하고 토큰은 출력하지 않습니다.
- 기본적으로 findings를 먼저 작성하고, 승인되었거나 즉시 게시가 명시된 경우에만 외부 리뷰를 남깁니다.

사용 예시:

```text
Use $github-pr-review to review https://github.com/owner/repo/pull/123. Draft the findings first and do not post the review until I approve it.
```

### github-pr-publish

로컬 브랜치를 점검하고 필요한 push와 GitHub PR 생성을 안전한 순서로 수행합니다.

- 기본값은 preview이며 명시적 승인 없이 push나 PR 생성을 하지 않습니다.
- private repository, 조직 SSO, 권한 부족과 remote mismatch를 구분해 진단합니다.
- unsafe fork, force push, detached HEAD와 잘못된 remote를 차단합니다.

사용 예시:

```text
Use $github-pr-publish to preflight the current branch and prepare a draft PR. Show the planned push and PR content before publishing anything.
```

### commit-helper

저장소 안의 명시적 규칙, 최근 커밋 이력과 staged diff를 확인해 그 저장소에 맞는 커밋 제목과 본문을 작성합니다.

- `명시적 저장소 규칙 → 최근 이력 → 보수적 fallback` 순서로 판단합니다.
- staged 변경만으로 커밋 의미와 scope를 결정합니다.
- 사용자가 커밋을 요청하면 안전한 argv 기반 helper로 로컬 커밋까지 완료합니다.

사용 예시:

```text
Use $commit-helper to inspect this repository's commit rules and staged changes, then create the local commit. Do not push.
```

## Codex 특화 워크플로

아래 4개 스킬은 완료 gate를 충족하기 위해 Codex Goal, 격리된 Codex 실행, native review 또는 subagent 계약을 직접 요구합니다. 모두 explicit-only이며 다른 카탈로그 스킬을 필수로 요구하지 않습니다.

### reviewed-plan

저장소 근거를 바탕으로 구현 계획을 만들고 Planner, Architect, Critic 순서의 독립적인 read-only gate를 통과시킵니다.

- 계획 중에는 파일을 수정하거나 패키지를 설치하지 않습니다.
- Architect 승인 후에만 Critic 검토를 진행합니다.
- 최종 handoff에 대상 파일, symbol, 위험, 대안과 검증 명령을 포함합니다.
- 같은 revision이 승인된 뒤에도 사용 가능한 execution workflow만 선택적으로 추천하며, 필수화·설치·실행하지 않습니다.

사용 예시:

```text
/plan $reviewed-plan Plan a backward-compatible migration from local session state to server-managed sessions. Keep the workspace read-only and return the reviewed implementation handoff.
```

### completion-loop

범위가 고정된 명확한 Codex Goal을 조사, 구현, 위험도별 검증, 실패 진단과 집중 수정 루프로 완료합니다.

- 편집 전에 목표, 범위, non-goal, 배포 대상, acceptance criteria, 증거, 위험도와 승인된 시스템을 고정합니다.
- 완료 계약 밖의 리뷰 관찰은 목표를 확장하지 않고 deferred로 분류합니다.
- evidence ledger로 검증 중복을 제거하고 blocker 수정 뒤에는 focused rereview만 실행합니다.
- 핵심 아키텍처 변경이 기록된 경우를 제외하면 최초 전체 리뷰와 최종 전체 검증은 각각 한 번만 실행합니다.

사용 예시:

```text
/goal Fix the reproducible cache invalidation regression for the local service, preserve public behavior, treat deployment automation as a non-goal, pass the existing tests and typecheck, and review the final diff. Use $completion-loop.
```

### milestone-runner

큰 목표를 순차적이고 독립적으로 검증 가능한 milestone으로 나누고 `.agent-workflows/`에 durable state와 evidence ledger를 남깁니다.

- 한 번에 하나의 milestone만 실행하고 stale revision이나 순서 위반을 거부합니다.
- 중단 후에도 저장소의 plan과 hash-chained ledger를 검증해 이어갈 수 있습니다.
- 모든 milestone, 최종 검증, 독립 review와 native Goal reconciliation이 완료되어야 종료합니다.

사용 예시:

```text
Use $milestone-runner to migrate the authentication flow in three ordered stages, checkpoint each stage with tests, and finish only after final verification and an independent review.
```

상태 helper의 전체 명령 계약은 [Goal state CLI reference](skills/milestone-runner/references/goal-state-cli.md)에 있습니다.

### review-gate

현재 변경, 파일, commit, branch 또는 이미 읽을 수 있는 PR target을 PR 생성·병합 전 최종 readiness gate로 correctness와 architecture 두 lane에서 독립 검토합니다. 일상적이거나 가벼운 검토에는 native `/review`를 사용합니다.

- staged, unstaged와 untracked 변경을 sensitivity-screened snapshot으로 고정하고 원본 target fingerprint는 parent context에만 유지합니다.
- credential 값은 reviewer packet에서 제외하며, redaction으로 핵심 증거가 사라지면 `INCONCLUSIVE`를 반환합니다.
- 두 lane을 tool-enforced read-only sandbox에서 병렬 실행합니다.
- prioritized findings와 `APPROVE`, `COMMENT`, `REQUEST_CHANGES`, `INCONCLUSIVE` 중 하나의 판정을 반환합니다.

사용 예시:

```text
Use $review-gate as the final pre-PR gate for this high-risk change. Keep the worktree unchanged and return independent correctness and architecture verdicts.
```

## 사용 원칙

- 스킬 하나만 설치해도 해당 핵심 워크플로가 동작해야 합니다.
- 선택적 workflow handoff는 추천일 뿐입니다. 현재 작업의 available-skill inventory에 표시된 downstream workflow만 언급하며, inventory 또는 최적의 스킬을 사용할 수 없으면 아무것도 제안하지 않습니다.
- 공통 스킬은 각자의 invocation policy를 따르며, 명확한 재현을 원하면 예시처럼 `$skill-name`을 직접 지정합니다.
- Codex 특화 4개와 제어가 중요한 공통 `spec-interview`, `visual-match`, `godot-dev-loop`는 `allow_implicit_invocation: false`이며 명시적으로 호출합니다.
- optional plugin이나 도구가 없으면 저장소 기본 도구와 안전한 fallback을 우선합니다.
- 외부 게시, push, 환경 설치와 destructive action은 스킬 호출만으로 승인된 것으로 보지 않습니다.

## 유지보수와 검증

관리 대상 6개 workflow 스킬의 소스 snapshot, native capability mapping, 업데이트 주기와 forward-test 절차는 [workflow skill maintenance](docs/native-workflow-skills-maintenance.md)에 정리되어 있습니다.

두 스크립트의 역할은 다음과 같습니다.

- `skills/milestone-runner/scripts/goal_state.py`: `milestone-runner` 하나의 durable repository state만 관리합니다.
- `scripts/check-native-workflow-skills.py`: 관리 대상 6개 패키지와 로컬 유지보수 대상 `godot-dev-loop`의 구조, 독립성, metadata, native capability와 TUI 그룹을 검사합니다. source drift는 기존 관리 대상 6개에만 적용하며, `handoff-memory`와 `project-chronicle`에 선언된 sibling-reference 경계도 함께 검증합니다.

### Workflow checker modes

| 명령 | 네트워크 | 용도 |
| --- | --- | --- |
| `python3 scripts/check-native-workflow-skills.py` | 없음 | package, metadata, link, 독립성, state root와 catalog 검사 |
| `python3 scripts/check-native-workflow-skills.py --require-validator` | 없음 | 공식 `skill-creator` validator와 PyYAML 가능한 Python을 필수화 |
| `python3 scripts/check-native-workflow-skills.py --check-upstream` | 사용 | 기록된 source commit과 현재 upstream fingerprint 비교 |
| `python3 scripts/check-native-workflow-skills.py --check-codex-docs` | 사용 | 현재 Codex manual에서 기록된 native capability 확인 |

전체 acceptance check:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/check-native-workflow-skills.py --check-upstream --check-codex-docs --require-validator
```

자동 검증만으로 실제 동작을 모두 증명할 수는 없습니다. 복잡한 계약을 바꾼 뒤에는 유지보수 문서의 격리된 forward-test matrix도 함께 실행합니다.

## 저장소 구조

```text
agent-skills/
├── .claude-plugin/
│   └── marketplace.json  # skills CLI의 용도, runtime, 실험적 상태 표시 그룹
├── skills/          # 하나의 디렉터리마다 독립 설치 가능한 스킬 하나
├── scripts/         # 여러 패키지 계약과 source drift를 검사하는 유지보수 도구
├── tests/           # package와 workflow contract 회귀 테스트
├── docs/            # native capability mapping과 forward-test 기록
└── assets/          # 루트 문서에서 사용하는 이미지
```

각 스킬 패키지는 필요에 따라 다음 파일을 가집니다.

| 경로 | 역할 |
| --- | --- |
| `SKILL.md` | 에이전트가 실행하는 핵심 계약 |
| `agents/openai.yaml` | Codex UI 표시 이름, 설명과 기본 prompt |
| `metadata.json` | 카탈로그 metadata와 참고 문서 |
| `references/` | 필요할 때만 읽는 상세 계약과 rubric |
| `scripts/` | 반복적이고 결정적으로 실행해야 하는 package-local helper |
| `README.md`, `AGENTS.md` | 기존 package에서 별도 문서나 편집 지침이 실제로 필요한 경우만 유지 |

새 스킬을 추가하거나 기존 계약을 바꿀 때는 `SKILL.md`, metadata, root catalog, `README.md`, `README.ko.md`와 관련 테스트를 함께 갱신하고 구조 변경 후 validator를 실행합니다.
