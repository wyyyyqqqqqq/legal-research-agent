**Language:** [**한국어**](disclaimer.md) | [English](../en/disclaimer.md)

# Disclaimer (면책조항)

> **[README](../../README.ko.md)** | **[사용 가이드](how-to-use.md)** | **[MCP 설정 가이드](mcp-setup-guide.md)**

## Personal Project

본 프로젝트는 개인 독립 프로젝트입니다. 어떤 로펌·고용주·조직의 후원이나
공인을 받지 않습니다. 이 리포지토리의 모든 의견·설계 결정·콘텐츠는
전적으로 프로젝트 관리자의 것입니다.

## Not Legal Advice

이 리포지토리에 포함된 어떤 것도 — 리서치 기록물, 모드형 산출물(executive
brief, comparative matrix, enforcement and case-law, black-letter
commentary), 법률 의견서형 노트, DOCX 렌더 산출물, 그 외 에이전트가
생성한 모든 출력물을 포함해 — **법률 자문에 해당하지 않습니다.** 산출물은
정보 제공 및 보조 용도일 뿐입니다. 자격 있는 법률 자문의 대체물로 의존하지
마십시오.

## AI Limitations

본 프로젝트는 대규모 언어 모델(Claude)에 기반합니다. LLM은 **할루시네이션**,
**사실 오류**, **부정확한 법률 분석**을 생성할 수 있고 실제로 합니다.
산출물에 다음과 같은 오류가 발생할 수 있습니다:

- **법적 권위 날조 (fabricate)** — 존재하지 않는 법령, 시행령, 판례,
  행정청 가이드를 인용;
- **법 진술 오류 (misstate the law)** — 폐지되거나 변경되거나 잘못
  해석된 규칙을 현행으로 제시;
- **관할 혼동 (conflate jurisdictions)** — 한 국가/주/규제기관의 규칙을
  엉뚱한 곳에 귀속;
- **핵심 쟁점 누락 (omit material issues)** — 관련 규제, 예외, 진행 중인
  개정안을 식별 못함;
- **소스 위계 오분류 (misclassify source hierarchy)** — 비구속적 가이드,
  블로그 코멘터리, 2차 요약을 1차 법적 권위로 취급;
- **인용 위조 (invent citations)** — 그럴듯해 보이지만 완전히 허구인
  사건명, 사건번호, 법령 참조, 조문 제목을 생성.

본 에이전트는 내장된 안전장치를 갖추고 있습니다 — `skills/trust-boundary.md`,
`skills/source-collection.md`의 source-layer 최소요건,
`skills/source-grading.md`, `skills/claim-spot-check.md`의 소스 세탁 가드,
`skills/claim-verification-loop.md`, `skills/currentness-check.md`,
`skills/quality-check.md`, 그리고 스탠드얼론 `/audit` citation auditor —
그러나 **이 안전장치들은 오류 위험을 줄일 뿐 제거하지 않습니다.** 자격 있는
사람이 모든 산출물을 의존·실행 전에 반드시 검토·검증해야 합니다. 에이전트는
보조하고, 사람이 결정합니다.

## Data Handling

본 에이전트는 LLM API 호출을 수행하므로, 리서치 질문과 수집된 소스 텍스트가
모델 제공자(Anthropic)에 전송됩니다. 표준 상용 약관 하에서 API 요청 라이프
사이클을 넘어 외부 서버에 데이터가 저장되지 않습니다.

비밀·특권 정보가 포함된 매터에 본 도구를 사용할 경우:

- 데이터 처리 약관이 적합한 상용 API 키를 사용;
- 최신 약관은 [Anthropic의 데이터 사용 정책](https://www.anthropic.com/policies)에서
  확인;
- 민감한 자료를 어떤 AI 도구에든 처리하기 전에 소속 조직의 보안·컴플라이언스
  요건을 확인.

에이전트의 MCP·웹 페치 표면 또한 설정된 서버(예: `korean-law` MCP 서버,
`WebFetch`, `WebSearch`)에 질의를 전송합니다. 민감한 질의는 그에 맞춰
취급하십시오.

## No Warranty

본 소프트웨어는 명시적·묵시적 어떤 종류의 보증 없이 "있는 그대로(as is)"
제공됩니다. 전체 약관은 [Apache License 2.0](../../LICENSE)에서 확인하십시오.
저자는 본 소프트웨어 또는 그 산출물의 사용으로 인해 발생한 손해에 대해
어떠한 책임도 지지 않습니다.

## Scope of Responsibility

저자는 다음에 대해 책임지지 않습니다:

- 에이전트 산출물에 기반해 내려진 결정;
- 생성된 콘텐츠에 대한 의존으로 인한 손실, 법적 결과, 손해;
- 산출물의 정확성, 완전성, 특정 목적 적합성;
- API 키, MCP 서버, 네트워크 설정 오구성 또는 사용자 오류로 인한 데이터
  노출.

**본 프로젝트를 사용함으로써, 귀하는 이 면책조항을 읽고 이해했음을 인정합니다.**
