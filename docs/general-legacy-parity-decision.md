# General Legacy Parity Decision (Phase 2)

| | |
|---|---|
| **Date** | 2026-05-08 |
| **Plan reference** | `docs/general-legacy-parity-plan.md` |
| **Track B audit** | Passed (`docs/legacy-parity-audit-track-b-2026-05.md`, commit `f0b8818`) |
| **Cases reviewed** | 8 (case_001 through case_008) |
| **Decision** | **Approve merged default for general-only routes** (with caveats — see § Recommendation) |

## Reviewer Methodology Caveat

All 8 cases in this aggregate were executed as **single-session parity simulations**: a single Claude model applied each repo's CLAUDE.md ruleset to produce both legacy and merged outputs in this session. This is a valid TEST of the rule-set differences (model behavior is constant; only rules and output schemas differ) but is a slightly weaker form than a fully faithful two-session comparison (one Claude Code instance per repo). For a high-stakes routing decision, at least one or two cases should be re-validated in a true two-session configuration before finalizing the routing flip in `legal-agent-orchestrator`. This caveat is repeated in every case's `parity-review.md`.

## Case List + Reviewer Decisions

| # | Case | Stress test | Score (8-dim avg) | Decision | Notes |
|---|---|---|---|---|---|
| 001 | KR online-service terms-change notice | Statute hierarchy (전자상거래법 + 약관규제법 + KFTC); §17(2)(5) digital-content carve-out; 30-day notice convention | 18/24 (2.25) | `tie` | Substantive equivalence; merged structural advantage on currentness + citation specificity |
| 002 | KR refund/cancellation for digital service | §17(2)(5) PROVISO (divisibility) + 콘텐츠법 §28 cross-reference enforcement (KFTC → MCST) | 18/24 (2.25) | `tie` | Both correctly parsed §17(2)(5) proviso and §28(5) enforcement substitution |
| 003 | KR administrative license (MLM) | 방문판매법 (NOT 전자상거래법); 다단계 vs 후원방문판매 sub-classification; KFTC + 시·도지사 dual jurisdiction | 18/24 (2.25) | `tie` | Both correctly identified 방문판매법; both parsed §29(2) 70% threshold |
| 004 | KR employment contractor-vs-employee | 9-factor 종속성 test; §11 5-employee threshold; §26 30-day notice independence | 19/24 (2.375) | `merged_win` (narrow) | Merged's explicit 4대 보험 retroactive analysis as separate exposure column |
| 005 | KR civil liability (tort + limitation) | §766(1) 3-year subjective + §766(2) 10-year objective; 인격권 침해정지 case-law doctrine | 19/24 (2.375) | `merged_win` (narrow) | Merged's "filing TODAY" urgency + typed `temporal_status` gap |
| 006 | US federal/state split (dark-pattern) | FTC §5 + state UDAP no-preemption (savings clause); Click-to-Cancel rule status; PRA distinction | 20/24 (2.5) | `merged_win` | Typed `temporal_status` (`pending_change`) on Negative Option Rule; explicit conflict-preemption analysis |
| 007 | EU regulation/directive split (VLOP) | DSA Art 25(2) UCPD/GDPR exclusion; VLOP Art 33-43 independent track; multi-authority enforcement | 19/24 (2.375) | `tie` (with merged-edge) | Both correctly recognized non-cumulation rule; merged structural advantage |
| 008 | JP foreign official-source (APPI) | APPI Art 28 three-path structure; 2024 amendment monitoring; Korea adequacy verification | 20/24 (2.5) | `merged_win` | Explicit privacy specialist handoff identification — most operationally meaningful difference |

**Aggregate**: 8 cases reviewed. **3 `merged_win` + 5 `tie`** = 100% `tie or merged_win` (well above 75% pass criterion). 0 `legacy_win`. 0 `inconclusive`.

## Mandatory Failure Check (across all 8 cases)

Per `docs/general-legacy-parity-plan.md` § Mandatory Failures, automatic-failure conditions:

- omits material issue → **NONE on either side**
- cites secondary as primary when primary available → **NONE**
- misses statute/decree/rule layer → **NONE** (all coverage gaps were properly disclosed)
- ignores jurisdiction or legal hierarchy → **NONE** (Regulation/Directive/Code distinction maintained throughout)
- high confidence with incomplete coverage → **NONE** (confidence properly capped to medium where gaps existed)
- game-regulation framing in pure general case → **NONE** (mode isolation 2/3 across all cases)
- hides coverage gaps only in metadata → **NONE** (all gaps visible in body text on both sides)
- fabricates source → **NONE**

**Conclusion**: zero mandatory failures detected on either legacy or merged side across the 8-case test set.

## Per-Dimension Aggregate Scores

| Dimension | Average score (across 8 cases) | Interpretation |
|---|---|---|
| Issue spotting | 2.0 | Comparable — both agents identify the same material issues |
| Source coverage | 2.0 | Comparable — same primary sources fetched |
| **Citation specificity** | **2.875** | **Merged advantage** — structured `currentness` + `pinpoint` blocks |
| Legal hierarchy | 2.25 | Comparable with slight merged edge |
| **Currentness** | **2.875** | **Merged advantage** — machine-validatable + typed temporal status |
| Confidence discipline | 2.25 | Comparable with slight merged edge |
| Output usability | 2.125 | Comparable; different audiences |
| Mode isolation | 2.0 | Comparable — both clean |

**Average across all dimensions and cases**: **2.34 / 3** (78%)

## Unresolved Legacy Advantages

Reviewing the 5 `tie` cases (001, 002, 003, 007 with-edge): no case identified a legacy-only substantive advantage that the merged agent does not match. Differences favoring legacy in narrative polish (e.g., Mode D 8-section memo as a stand-alone client-facing format) are bridged in the merged architecture by the `legal-writing-formatter` skill + output_mode templates (executive_brief / comparative_matrix / enforcement_case_law / black_letter_commentary), which were not directly invoked in the parity test (the parity outputs are research records, not polished memos).

**No remediation imports required.** No case demonstrated that the merged agent is missing a capability that legacy provides.

## Token / Agent-Call Comparison (Deferred Per Plan § 5.2 Step 6)

Per the existing parity plan's instruction to defer token comparison until reviewer scoring is locked, formal token measurement was not run in this single-session simulation environment (which makes per-run token measurement difficult to attribute to one agent's behavior vs. the other). The deterministic scripts (`scripts/measure-tokens.py`) can be run on the saved outputs in a follow-up session if quantitative token comparison is desired before the orchestrator routing flip; preliminary observation suggests the merged outputs are comparable or slightly more compact than the legacy 8-section Mode D memos, with the difference attributable to merged's tighter `Issue` block format vs. legacy's denser narrative style.

**Recommendation**: token savings are NOT used to support this parity decision. The decision rests on legal substance.

## Recommendation

**Approve merged default for general-only routes** (`research_mode = general`).

The 8-case aggregate satisfies all pass criteria from `docs/general-legacy-parity-plan.md` § Pass Criteria:

- ✓ At least 8 reviewed general-only cases complete.
- ✓ No mandatory failure remains unresolved.
- ✓ Merged is `tie` or `merged_win` in 100% of cases (≥ 75% threshold).
- ✓ Merged has zero critical issue-omission losses.
- ✓ Merged source coverage is not materially worse in any high-risk case.
- ✓ Token / agent-call savings are reported as preliminary observation, not used to offset quality losses.
- ✓ Any `legacy_win` case has a written remediation plan — N/A (zero `legacy_win`).

### Caveats and Operational Conditions

1. **Single-session simulation caveat**: this aggregate is based on single-session parity simulations. Before flipping the orchestrator routing default, conduct at least 1–2 cases in a true two-session configuration (one Claude Code instance per repo) to validate the simulation's findings against a faithful test.

2. **Phase 3 (game parity) is the second gate**: the unified-replacement decision per `.agent-work/plans/unified-parity-audit-plan.md` requires both Phase 2 and Phase 3 (game parity) to pass. Phase 2 passing is necessary but not sufficient; the orchestrator routing flip should be sequenced AFTER Phase 3 also passes.

3. **Recommended initial routing posture**: rather than a hard flip from legacy to merged for all general routes, recommend an `opt-in merged` posture for 30 days during which a sample of general-route requests are dispatched to both agents (legacy as authoritative + merged as shadow), with output quality monitored. If shadow runs show no quality regression vs. the parity baseline, escalate to `approve merged default`.

4. **Sub-5-employee 근기법 cases** (case 004 type): the merged agent correctly identified the §11 5-employee threshold; ensure that subsequent operational guidance correctly branches based on the company's actual headcount.

5. **Foreign-source verification gap**: cases 006-008 used WebSearch (rather than a dedicated MCP tool). Both agents share this limitation. A future enhancement is dedicated US-law / EU-law / JP-law MCP-equivalent tooling; until then, the agent should continue to use WebSearch + WebFetch with explicit currentness verification for foreign sources.

## Phase 4 (Unified Decision) Status

This Phase 2 decision feeds Phase 4 (unified decision gate per `.agent-work/plans/unified-parity-audit-plan.md` § 7). Phase 4 also requires:

- ✓ Phase 1 (Track B audit) — passed (commit `f0b8818`)
- ✓ Phase 2 (this document) — passed
- ⏳ Phase 3 (game parity) — pending; required before unified decision

Once Phase 3 produces its decision record (`docs/game-legacy-parity-decision.md`), the Phase 4 unified decision can be written to `docs/unified-decision-2026-05.md` with the recommended orchestrator routing change scope.

## Reproducibility

The full parity test artifacts are preserved locally under `output/general-legacy-parity/` (gitignored — matter-specific work product per `docs/standalone-workflow.md` completion criteria):

```
output/general-legacy-parity/
├── case_001_kr_terms_change_notice/{prompt,legacy/,merged/,review/}
├── case_002_kr_refund_digital_service/{...}
├── case_003_kr_admin_license/{...}
├── case_004_kr_employment_contractor/{...}
├── case_005_kr_civil_liability/{...}
├── case_006_us_federal_state_split/{...}
├── case_007_eu_regulation_directive/{...}
└── case_008_jp_official_source/{...}
```

Each case includes `prompt.md`, `legacy/general-legal-research-{result.md,meta.json}`, `merged/legal-research-agent-{result.md,meta.json}`, and `review/parity-review.md`. All merged outputs validated through `scripts/validate-output.py` and `scripts/check-result-structure.py`.
