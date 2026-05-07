# Citation Audit Canonical Spec

**Status:** canonical project spec for citation audit behavior in
`legal-research-agent`.

**Scope:** standalone `/audit` invocation, standalone deliverable
workflow, mode-shaped deliverable handling, sidecar artifacts, format
support matrix, and Korean-law MCP degradation.

This document is the single source of truth for citation audit
behavior. Runtime prompts and public docs link here instead of
restating the full procedure.

---

## Invocation Contexts

| Context | Trigger | Behavior |
|:---|:---|:---|
| Standalone `/audit <file.md\|file.docx>` | User explicitly runs the slash command from `.claude/commands/audit.md` | Per-file citation audit producing inline annotations (Markdown) or sidecar reports (DOCX). Does not modify the canonical research record. |
| Standalone deliverable workflow | External or client-facing standalone deliverable produced via `skills/legal-writing-formatter.md` | Audit folded into `standalone-deliverable-manifest.json` per `docs/standalone-workflow.md`. Status recorded as `live_passed`, `deterministic_smoke`, `live_failed`, `not_required`, or `not_run_session_unavailable`. |

The vendored `citation-auditor` skill at
[`.claude/skills/citation-auditor/SKILL.md`](../.claude/skills/citation-auditor/SKILL.md)
is the engine. The Python package at
[`citation_auditor/`](../citation_auditor/) provides the
prepare / chunk / aggregate / render / report pipeline.

Verifier subagents under
[`.claude/skills/verifiers/`](../.claude/skills/verifiers/) cover
Korean law (`korean-law`), US law (`us-law`), UK law (`uk-law`),
EU law (`eu-law`), scholarly sources (`scholarly`), Wikipedia
(`wikipedia`), and the catch-all (`general-web`).

---

## Output Artifacts

| Artifact | Required when | Purpose |
|:---|:---|:---|
| Inline annotated Markdown | `/audit` on a Markdown file | Per-claim verdict badges and rationales rendered in place |
| `<file>.audit.md` | `/audit` on a DOCX file | Sidecar Markdown report containing per-claim verdicts |
| `<file>.audit.json` | `/audit` on a DOCX file | Machine-readable per-claim verdict aggregate |
| `<file>.audit-source.md` | `/audit` on a DOCX file | Markdown extraction used as the audit input |
| `<file>.source-map.json` | `/audit` on a DOCX file | Maps Markdown extraction offsets back to DOCX paragraphs |
| Manifest `audit` block | Standalone deliverable workflow | `audit.required`, `audit.status`, `audit.claim`, optional path to the per-deliverable audit JSON |

The standalone deliverable workflow does not produce a separate
audit Markdown sidecar by default — the audit is folded into the
manifest. See [`docs/standalone-workflow.md`](standalone-workflow.md)
for the manifest schema.

---

## Format Support Matrix

| Final format | Integration level | Required behavior |
|:---|:---|:---|
| `.md` | Full inline integration | Audit annotations rendered in place; the body of the Markdown is preserved |
| `.docx` | Full sidecar integration | `<file>.audit.md` and `<file>.audit.json` written next to the DOCX; the original DOCX is never modified |
| Other (`.pdf`, `.html`, `.txt`) | Unsupported as final format | The agent does not generate these directly; convert from `.md` first, then `/audit` the Markdown |

DOCX rendering uses `scripts/render-docx.py` (MVP). Native footnotes,
tracked changes, comments, and complex page layout are intentionally
not promised — `docs/standalone-workflow.md` documents the supported
DOCX feature set.

The deterministic chunk → aggregate → render smoke runs entirely
offline against fixtures and is invoked by
`scripts/check-citation-auditor-smoke.py`.

---

## Detailed Status Model

The `citation-auditor` aggregator normalizes verifier responses into
the following statuses. The standalone deliverable manifest's
`audit.status` uses a separate value space (described above);
**these are per-claim** statuses inside the audit aggregate.

| Status | Meaning |
|:---|:---|
| `verified` | Source evidence directly supports the claim |
| `contradicted` | Source evidence conflicts with the claim |
| `unsupported` | Verifier ran but no supporting evidence was found |
| `source_unavailable` | A needed source could not be retrieved (network, paywall, or rate-limit) |
| `verifier_unavailable` | No verifier produced a result for the claim (no matching pattern, all verifiers failed) |
| `not_a_legal_claim` | Claim does not qualify for legal/factual auditing (forecast, opinion, rumor) |
| `unknown` | Residual unresolved state |

Aggregate metrics in the audit JSON include:

- `total_claims`
- `audited_claims`
- counts per status above (`verified`, `contradicted`, `unsupported`,
  `source_unavailable`, `verifier_unavailable`, `not_a_legal_claim`,
  `unknown`)
- `tool_failures`
- `coverage_ratio`

Forecasts, opinions, rumors, and soft prediction language
(`전망이다`, `예상된다`, `업계 관계자에 따르면`, `가능성이 있다`,
"is expected to", "may", "could", "is likely to") are intentionally
skipped at claim extraction. They never enter the audit surface as
claim candidates.

---

## Korean-Law MCP Degradation

The `korean-law` verifier is strongly preferred for Korean legal
claims. When the verifier routes a Korean-law claim but the
underlying MCP is unavailable, false, or only placeholder-configured:

```json
{
  "scope": "korean-law",
  "reason": "korean-law MCP unavailable or not declared available; primary-law verification may degrade to unknown.",
  "affected_claim_ids": ["claim_001", "claim_002"]
}
```

The verifier returns `verifier_unavailable` rather than fabricating
a verdict. The audit aggregate metadata records the degradation
scope so consumers can decide whether to ship or re-run.

The agent's source-collection skill applies the same discipline
upstream — `skills/source-collection.md` Korean Law Strategy and
`skills/output-contract.md` Error Vocabulary
(`mcp_unavailable`, `partial_sources`).

---

## Standalone Deliverable Audit Status

The standalone deliverable workflow records `audit.status` in the
manifest with these values (distinct from the per-claim status model
above):

| Status | Meaning |
|:---|:---|
| `not_required` | Audit not requested for this deliverable (e.g., internal-only draft) |
| `not_run_session_unavailable` | Live verifier dispatch could not run in this Claude Code session |
| `deterministic_smoke` | Local deterministic smoke ran; live verifiers did not |
| `live_passed` | Live verifier dispatch ran and the audit passed the project's quality bar |
| `live_failed` | Live verifier dispatch ran and the audit flagged a material issue |

A deliverable cannot be labeled "final" if the required audit status
is `not_run_session_unavailable` and the manifest does not also mark
the deliverable as `draft` or `source-limited`. See
[`docs/standalone-workflow.md`](standalone-workflow.md).

---

## Vendor Discipline

`citation-auditor` is vendored. Refresh the vendor stamp at
`.claude/skills/citation-auditor/VENDOR.md` only when intentionally
upgrading from the sibling source repo:

```bash
../citation-auditor/scripts/vendor-into.sh "$PWD"
```

The vendor smoke (`scripts/check-citation-auditor-vendor.py`) verifies
the file set and CLI help. The deterministic audit smoke
(`scripts/check-citation-auditor-smoke.py`) runs the chunk / aggregate /
render pipeline against a legal-research result fixture. Live verifier
dispatch and web/MCP-backed audits are not part of the local preflight.

---

## 한국어 요약

이 문서는 `legal-research-agent`의 citation audit 정식 규약입니다.

- `/audit <file.md|file.docx>`는 수동 실행이며 정식 리서치 기록을 수정하지
  않습니다.
- 스탠드얼론 산출물 워크플로우는 audit을 매니페스트의 `audit` 블록에 폴드하며,
  status는 `live_passed` / `deterministic_smoke` / `live_failed` /
  `not_required` / `not_run_session_unavailable` 중 하나입니다.
- 마크다운은 인라인 통합, DOCX는 사이드카 통합, 그 외 형식(`.pdf`, `.html`,
  `.txt`)은 직접 생성하지 않으며 마크다운에서 변환 후 `/audit` 합니다.
- 한국법 인용 감사에는 `korean-law` MCP 사용을 강력 권장하며, 미사용 또는
  placeholder 설정이면 verifier가 `verifier_unavailable`을 반환하고 매니페스트
  메타데이터에 degradation을 기록합니다.
- 청구 단위 status 어휘(`verified` / `contradicted` / `unsupported` /
  `source_unavailable` / `verifier_unavailable` / `not_a_legal_claim` /
  `unknown`)는 매니페스트의 `audit.status` 어휘와 별개입니다 — 전자는 한
  청구의 검증 결과, 후자는 산출물 차원의 audit 실행 상태를 의미합니다.
- 전망·추측·소문·예측 표현은 의도적으로 audit 대상에서 제외됩니다.
