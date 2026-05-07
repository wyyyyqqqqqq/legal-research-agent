**Language:** [**한국어**](how-to-use.md) | [English](../en/how-to-use.md)

# 사용 가이드 | Legal Research Agent

> **[README](../../README.ko.md)** | **[면책조항](disclaimer.md)** | **[MCP 설정 가이드](mcp-setup-guide.md)** | **[Citation Audit 사양](../citation-audit.md)**

이 가이드는 `legal-research-agent`를 처음 실행하는 절차를 안내합니다.
에이전트는 Claude Code 세션 내에서 동작하며, 두 개의 계약 파일(오케스트레이터
호환)과 (선택적) 모드형 산출물을 생성합니다.

## Prerequisites

| 요구사항 | 설명 |
|:---|:---|
| **Claude Code** | [CLI](https://claude.ai/code) 설치 및 인증 |
| **Python 3.11+** | 검증 스크립트는 표준 라이브러리만; 렌더러는 `marko`, `pydantic`, `python-docx` 필요 (`pyproject.toml` 참고) |
| **`korean-law` MCP 서버** | 선택사항이지만 한국 1차 자료 커버리지에 강력 권장. [MCP 설정 가이드](mcp-setup-guide.md) 참고 |
| **네트워크** | `WebFetch` / `WebSearch` 폴백에 필요; 로컬 프리플라이트에는 불필요 |

## Quick Start

1. Claude Code에서 프로젝트 디렉터리를 엽니다:

   ```bash
   cd legal-research-agent
   claude
   ```

2. 자연어로(영어 또는 한국어) 리서치 질문을 합니다. 에이전트가 `CLAUDE.md`를
   읽고 리서치 모드를 선택해 8단계 워크플로우를 실행합니다.

3. (선택) 명시적 호출에는 `/research` 슬래시 커맨드를 사용:

   ```text
   /research <관할 또는 주제> <질문 본문> [mode=<output_mode>]
   ```

4. 에이전트는 오케스트레이터가 지정한 `output_dir`(스탠드얼론에서는 작업
   디렉터리)에 두 개의 계약 파일을 작성합니다:

   - `legal-research-agent-result.md` — 정식 9-section 리서치 기록
   - `legal-research-agent-meta.json` — 오케스트레이터 호환 메타데이터

5. 폴리쉬된 산출물(executive brief, comparative matrix 등)을 요청한 경우
   `deliverables/` 아래에 모드형 파일도 작성하고
   `standalone-deliverable-manifest.json`을 갱신합니다. [`docs/standalone-workflow.md`](../standalone-workflow.md)
   참고.

## Personal Configuration

표준 사용을 반복할 때, `/onboard` 슬래시 커맨드가 기본 스코프(산업,
법 영역, 관할, 언어, 선호 출력 모드)를 `user-config.json`으로 캡처해
모든 세션이 동일 default를 재사용하게 합니다. 마법사는 개인 식별 정보를
수집하지 않습니다 — preferences만 저장합니다.

```text
/onboard
```

마법사는 5개 질문 + 선택적 6번째 질문:

1. **산업** — `game`, `fintech`, `healthcare`, `platform`,
   `e_commerce`, `media`, `other` 중 하나.
2. **법 영역 포커스** — `general`, `regulatory`, `contract`,
   `consumer_protection`, `intellectual_property`, `employment`,
   `privacy`, `tax`, `competition`, `other` 중 multi-select.
3. **주 관할** — ISO 국가 코드 (또는 `EU` / `UK` 단축) 1개 이상.
4. **부 관할** — 선택사항.
5. **출력 선호** — `output_mode` + 패키징 + 언어를 한 번에 묶는 단축
   번들.
6. *(선택)* 시작 지식 디렉터리를 지금 구축할까? — `yes`이면 마법사가
   [`docs/knowledge-construction-recipe.md`](../knowledge-construction-recipe.md)의
   recipe를 실행해 `knowledge/<industry>-<area>/`를 생성합니다 (regulator
   map, source map, issue taxonomy, library index). 디렉터리는
   `[GENERATED — REQUIRES HUMAN REVIEW]` 게이트 상태로 시작하며,
   사용자가 `/review-knowledge`로 게이트 해제하기 전까지 trusted로
   취급되지 않습니다.

전체 스키마는
[`templates/user-config.example.json`](../../templates/user-config.example.json)
에 있고,
[`scripts/check-user-config.py`](../../scripts/check-user-config.py)
validator가 로컬 프리플라이트에서 자동 실행됩니다.

### 설정 교체 또는 갱신

```text
/onboard --reset             # 명시적 확인 후 전체 재실행
/onboard --build-knowledge   # 지식 디렉터리만 재구축
/onboard --skip-knowledge    # 지식 미터치, preference만 갱신
```

### 생성된 지식 디렉터리 검토

마법사가 지식 디렉터리를 만들면(질문 6 = `yes`), 모든 `.md` 파일이
`[GENERATED — REQUIRES HUMAN REVIEW]`로 시작합니다. 내용을 검토하고
(필요 시) 편집한 후 게이트 해제:

```text
/review-knowledge knowledge/<industry>-<area>/
```

슬래시 커맨드가 `scripts/check-generated-knowledge.py`로 디렉터리
구조를 검증하고, 배너를 `[VERIFIED]`로 교체하며,
`user-config.json`의 해당 entry를 갱신합니다.

### 우선순위

| 실행 방식 | Primary | Fallback |
|:---|:---|:---|
| 표준 사용 | `user-config.json` defaults | 명시적 per-question 오버라이드가 이김 |
| 서브에이전트 디스패치 | 오케스트레이터 분류 | 오케스트레이터가 지정하지 않은 필드만 `user-config.json`이 채움 |

### 프라이버시와 파일 위치

`user-config.json`은 프로젝트 루트에 있고, gitignored 처리되어 있어
사용자 머신에만 존재합니다. `knowledge/<industry>-<area>/` 생성 디렉터리도
기본 gitignored 처리되어 있고, 검토 완료된 지식을 의도적으로 공유할 때만
ignore list에서 제거합니다.

마법사는 이름·소속·자격증을 수집하지 않습니다. preferences(산업, 관할,
출력 모드, 언어)만 저장합니다.

## Research Modes

에이전트는 오케스트레이터 분류, `/research` 인자, 또는 자체 분류에 따라
4가지 리서치 모드 중 하나를 선택합니다:

| 모드 | 사용 시점 |
|:---|:---|
| `general` | 더 좁은 전문가가 필요 없는 일반 법률 질문 |
| `game_regulation` | 게임 퍼블리싱, 확률형 아이템, 등급분류, 가상자산, 플랫폼 컴플라이언스, 청소년 보호 |
| `game_plus_general` | 게임산업 질문에 별개의 비-게임 법률 쟁점이 함께 있는 경우 |
| `fallback` | 모호한 질문, 출처 커버리지 부족, 또는 범위 외 |

라우팅 규칙과 자체 분류 로직은 `skills/classify-research-mode.md`와 `CLAUDE.md`에
정의되어 있습니다.

## Output Modes

출력 모드는 **산출물의 구조**를 결정합니다 — **콘텐츠 도메인**을 라우팅하는
research mode와는 독립입니다. 4가지 명명된 모드는 전신 `general-legal-research`의
Mode A/B/C/D를 미러하며, 5번째 `canonical` 슬러그는 오케스트레이터 호환의
9-section 메모를 보존합니다.

| 슬러그 | 라벨 | 적합한 경우 |
|:---|:---|:---|
| `executive_brief` | Executive Brief (Mode A) | 의사결정자, C-suite |
| `comparative_matrix` | Comparative Matrix (Mode B) | 다관할 컴플라이언스 |
| `enforcement_case_law` | Enforcement and Case Law (Mode C) | 소송, 집행 전략 |
| `black_letter_commentary` | Black-letter and Commentary (Mode D) | 법령 deep dive |
| `canonical` *(기본)* | Canonical research memo | 오케스트레이터 호환 기록 |

선택 규칙과 슬러그→템플릿 매핑은
[`knowledge/output-modes/mode-index.md`](../../knowledge/output-modes/mode-index.md)에
있습니다. 각 비-canonical 모드는
[`templates/output-modes/`](../../templates/output-modes/)의 템플릿과
[`knowledge/output-modes/counter-analysis-checklist.md`](../../knowledge/output-modes/counter-analysis-checklist.md)의
counter-analysis 디시플린을 동반합니다.

## Packaging Modes

패키징은 **출력 형식** 축이며 출력 모드와 직교합니다. 한 실행은 하나의
패키징 슬러그를 선택합니다:

| 모드 | 사용 시점 |
|:---|:---|
| `standalone_markdown` | 기본 폴리쉬 메모 또는 의견서형 노트 |
| `handoff_packet` | 다운스트림 legal-writing 에이전트가 작성을 이어받을 때 |
| `docx_ready_markdown` | Word-ready 소스 또는 바이너리 DOCX 요청 시 |

출력 모드와 패키징 모드를 결합해 5 × 3 = 15가지 산출물 조합이 가능합니다.
기본값은
[`knowledge/output-modes/mode-index.md`](../../knowledge/output-modes/mode-index.md)에
기록되어 있습니다.

## Citation Audit

에이전트는 vendored [`citation-auditor`](../../citation_auditor/) 스킬과
관할별 verifier 패밀리를 포함합니다. Citation audit는 두 컨텍스트에서
동작합니다:

| 컨텍스트 | 트리거 | 동작 |
|:---|:---|:---|
| 스탠드얼론 `/audit` | 임의 마크다운/DOCX 파일에 수동 호출 | 마크다운엔 인라인 어노테이션; DOCX엔 `*.audit.md`/`*.audit.json` 사이드카 |
| 스탠드얼론 산출물 워크플로우 | 외부/클라이언트 대상 스탠드얼론 산출물 | 매니페스트에 audit 폴드; `live_passed` / `deterministic_smoke` / `not_run_session_unavailable` 명시 기록 |

전체 정식 사양은 [`docs/citation-audit.md`](../citation-audit.md)에 있습니다.

## Local-Only vs MCP-Connected

| 모드 | 동작 | 미동작 |
|:---|:---|:---|
| Local-only | 모든 `scripts/` validator와 테스트; 화이트리스트된 법률 포털에 대한 `WebSearch`/`WebFetch`; 스탠드얼론 포매터; 모드 템플릿 렌더링 | 한국 1차 자료 MCP 도구 셋; 라이브 verifier 디스패치 |
| MCP-connected | `mcp__claude_ai_Korean-law__*` 도구(법률, 시행령, 결정, chain-research) 포함 전체 워크플로우 | Claude.ai integrations 또는 `.mcp.json` 등록 필요 — [MCP 설정 가이드](mcp-setup-guide.md) 참고 |

MCP 없이는 에이전트가 `coverage_gaps`에 `mcp_unavailable`을 기록하고 confidence를
낮춥니다 — 추측해서 1차 법령을 채우지 않습니다. 한국 1차 법령은 MCP 갭을 메우려고
날조하지 않습니다.

## Tips

- **관할을 명확히 지정.** 국가·주·규제기관을 명시할 때 에이전트가 가장 좋은
  결과를 냅니다.
- **선호하는 출력 모드가 있으면 명시.** "KR vs JP에 대한 비교 매트릭스로 줘"
  또는 "`executive_brief`로" 둘 다 동작합니다.
- **`.docx`는 정말 필요할 때만.** DOCX 렌더링은 `scripts/render-docx.py`의
  MVP입니다; 네이티브 각주, 변경 추적, 코멘트, 복잡한 페이지 레이아웃은
  의도적으로 약속하지 않습니다.
- **`coverage_gaps` 항목 주의.** 리서치 실행의 한계를 표시한 것이므로
  클라이언트용 사본에서 부드럽게 지워서는 안 됩니다.
- **모든 산출물 검토.** 이는 리서치 도구이지 법률 판단의 대체물이 아닙니다.
  [면책조항](disclaimer.md) 참고.

## Local Preflight

27개 validator를 1초 미만에 모두 실행:

```bash
python3 scripts/run-local-checks.py
python3 scripts/run-local-checks.py --report
```

프리플라이트는 MCP나 네트워크를 호출하지 않습니다. fixtures, contracts,
frontmatter, output-mode 템플릿, prompt-footprint, 그리고 결정론적 citation-audit
스모크를 검증합니다. 전체 목록은 프로젝트 README 참고.
