**Language:** [**한국어**](mcp-setup-guide.md) | [English](../en/mcp-setup-guide.md)

# MCP 설정 가이드

> **[README](../../README.ko.md)** | **[사용 가이드](how-to-use.md)** | **[면책조항](disclaimer.md)**

이 가이드는 `legal-research-agent`가 실제로 의존하는 MCP(Model Context
Protocol) 설정을 다룹니다. 에이전트는 MCP가 없어도 graceful하게 degrade
하도록 설계되어 있습니다 — [Degradation Behavior](#degradation-behavior) 참고.

## Korean Law MCP Server

`korean-law` MCP 서버는 Korean Open Law API(law.go.kr)를 백엔드로 60개+ 의
네이티브 도구를 제공합니다 (법률, 시행령, 부령, 법원 결정, 행정청 해석,
심판원 결정, chain-research 워크플로우 등). 한국법 1차 자료의 통제 경로이며,
`general` 모드의 한국 부분과 `game_regulation` 모드의 한국 부분에 사용됩니다.

에이전트는 이 도구들을 `mcp__claude_ai_Korean-law__*` 네임스페이스로
호출합니다. 이는 Claude.ai 계정에 등록된 MCP 서버를 surface하는 방식입니다.

### 등록 경로 두 가지

| 경로 | 적합한 경우 | 설정 방법 |
|:---|:---|:---|
| Claude.ai-managed | Claude.ai 계정으로 Claude Code 스탠드얼론 사용 | Claude.ai integrations 패널에서 `korean-law` 서버 추가; 에이전트가 자동으로 `mcp__claude_ai_Korean-law__*` 도구를 인식 |
| Self-hosted via `.mcp.json` | 망분리 / 자체 호스팅 / 오케스트레이터 통합 | 리포 루트에 `.mcp.json`을 두고 upstream `korean-law-mcp` 패키지 지정 |

본 리포지토리는 개인용 `.mcp.json`을 커밋하지 않습니다. 권장 경로는 Claude.ai
integration입니다.

## Configuration

### Claude.ai-managed (권장)

1. Claude.ai integrations(연동) 패널을 엽니다.
2. **Korean Law** MCP 서버를 추가합니다.
3. 요청 시 Open Law API OC 키로 인증합니다. OC 키는 <https://open.law.go.kr/>
   (무료 가입)에 등록한 이메일 ID의 local-part입니다.
4. Claude Code를 재시작해 MCP 연결을 깨끗이 잡습니다.

에이전트는 다음 도구를 인식합니다:
`mcp__claude_ai_Korean-law__search_law`,
`mcp__claude_ai_Korean-law__get_law_text`,
`mcp__claude_ai_Korean-law__chain_full_research` 등.

### Self-hosted 대안

Claude.ai-managed 경로 없이 동일 도구 셋이 필요하다면 리포 루트에 `.mcp.json`을
둡니다:

```json
{
  "mcpServers": {
    "korean-law": {
      "command": "npx",
      "args": ["-y", "korean-law-mcp@latest"],
      "env": {
        "LAW_OC": "your_openlaw_oc"
      }
    }
  }
}
```

`your_openlaw_oc`는 본인 OC 키로 로컬에서만 교체. 개인 식별자를 커밋하지
마십시오. Self-hosted 시 도구는 다른 네임스페이스로 노출됩니다(예:
`mcp__korean-law__search_law`); `.claude/settings.json`의 allowlist를 그에
맞게 수정해야 합니다.

## Verification

설정 후 연결 확인:

1. Claude Code 재시작.
2. 새 세션에서 한국법 질문을 합니다. 에이전트가 `mcp__claude_ai_Korean-law__*`
   도구를 호출해야 합니다 (도구 호출 로그에서 확인).
3. 또는 로컬 프리플라이트 실행:

   ```bash
   python3 scripts/run-local-checks.py
   ```

   프리플라이트는 MCP 도구를 호출하지 않습니다 (오프라인 동작 필요). 다만
   `scripts/check-claude-conventions.py`로 settings allowlist 형식을
   검증합니다.

## Degradation Behavior

`korean-law` MCP 서버를 사용할 수 없을 때, 에이전트는 한국법 1차 자료를
날조하지 않고 gracefully degrade 합니다:

| 조건 | 에이전트 동작 |
|:---|:---|
| MCP 정상 | 법률·시행령·결정·체인 워크플로우에 MCP 사용 |
| MCP 사용 불가 | `WebSearch`/`WebFetch`로 `law.go.kr`·`supremecourt.go.kr` 폴백; confidence 하향; `mcp_unavailable` 기록 |
| 본질적 제한 | `source_access` 타입의 `coverage_gaps` 항목 추가 (구체적 설명 포함) |
| 한국 1차 자료 커버리지 결정적으로 부족 | `error`를 `mcp_unavailable` 또는 `partial_sources`로 설정; 2차 자료만으로 high-confidence 결론 금지 |

어휘와 규칙은 `skills/source-collection.md`(Korean Law Strategy)와
`skills/output-contract.md`(Error Vocabulary)에 정의되어 있습니다.

## Troubleshooting

| 증상 | 원인 가능성 | 해결 |
|:---|:---|:---|
| `mcp__claude_ai_Korean-law__*` 도구 안 보임 | MCP 미등록 또는 세션 재시작 안 됨 | Claude.ai integrations에 재등록; Claude Code 재시작 |
| MCP에서 `401`/`403` | OC 키 누락 또는 무효 | OC 키 재입력; <https://open.law.go.kr/>에서 검증 |
| 한국법 호출마다 권한 프롬프트 | `.claude/settings.json` allowlist에 네임스페이스 누락 | `mcp__claude_ai_Korean-law__*` 존재 여부 확인; self-hosted라면 prefix 갱신 |
| chain 워크플로우 타임아웃 | 백엔드 API 스로틀링 | 재시도; chain 호출은 병렬 실행되어 일시 스로틀링은 정상 |
| MCP 정상인데 `mcp_unavailable` 기록 | Claude.ai-managed와 self-hosted prefix 불일치 | 에이전트가 실제 호출하는 prefix와 allowlist 일치 확인 |

## Other MCP Servers

`legal-research-agent`는 다른 MCP 서버를 필수로 요구하지 않습니다.
vendored [`citation-auditor`](../../citation_auditor/) 스킬은 verifier
서브에이전트가 가능 시 MCP 도구를 호출할 수 있으나, 결정론적 스모크
(`scripts/check-citation-auditor-smoke.py`)는 MCP 의존성이 없습니다.

### Optional MCP Servers (있으면 자동 활용)

필수는 아니지만, 등록되어 있으면 에이전트가 사용합니다:

| MCP 서버 | 도구 prefix | 용도 | 상태 |
|:---|:---|:---|:---|
| `markitdown` | `mcp__markitdown__convert_to_markdown` | PDF / DOCX / PPTX / XLSX / HTML → 마크다운, source ingestion에 활용 | 권장; `.claude/settings.json`에 allowlist 추가됨 |
| `eur-lex` (커뮤니티) | `mcp__eur-lex__*` (등록 시) | EUR-Lex SOAP/REST → 통합본·시행일자 | Plug-in 패턴; 현재 에이전트는 `WebFetch`로 `eur-lex.europa.eu` 직접 호출 |
| `us-law` (커뮤니티) | `mcp__us-law__*` 등 | Congress.gov, eCFR, Federal Register, CourtListener | Plug-in 패턴; 2026-05 기준 널리 deploy되지 않음 |

**Plug-in 패턴.** Claude.ai integrations 패널 또는 `.mcp.json`에 새 MCP
서버를 추가할 때, `.claude/settings.json`의 `permissions.allow` 목록에
도구 prefix를 함께 추가합니다:

```json
{
  "permissions": {
    "allow": [
      "mcp__claude_ai_Korean-law__*",
      "mcp__markitdown__*",
      "mcp__eur-lex__*"
    ]
  }
}
```

에이전트의 source-collection 스킬(`skills/source-collection.md`)은 MCP
서버가 있을 때 `WebFetch`보다 MCP-backed 검색을 우선합니다. 한국 1차
법령은 전용 Korean Law strategy가 적용되며, 다른 관할은 README에 화이트리스트된
공식 포털에 대한 `WebSearch` / `WebFetch`로 폴백합니다.

### MCP 서버를 추가하면 안 되는 경우

- 구독 게이트 도구(예: 상용 법률 AI 플랫폼)는 모든 팀원이 좌석을 가질 때만
  가치가 있습니다. 그렇지 않으면 사용자마다 결과가 달라집니다.
- 범용 웹검색 MCP(`tavily`, `brave`)는 법률 리서치에서는 `WebSearch` /
  `WebFetch`와 대부분 중복입니다. 특정 이유(rate limit, 지역 차단 등)가
  있을 때만 추가하십시오.

스탠드얼론 산출물 워크플로우(DOCX 렌더링, citation audit 시퀀싱, 매니페스트
검증)는 [`docs/standalone-workflow.md`](../standalone-workflow.md) 참고.
