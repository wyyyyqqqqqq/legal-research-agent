# General Legacy Parity Plan

This plan defines how to test whether `legal-research-agent` can match or
exceed the legacy `general-legal-research` agent on pure general legal research
work.

The default assumption is conservative: the merged agent is not proven to be a
drop-in replacement for general-only work until it beats this plan.

Before running this parity plan, complete or explicitly defer the hardening
items in `docs/archive/plans/general-quality-hardening-plan.md`.

## Objective

Establish an evidence-backed decision on whether `legal-research-agent` is ready
to replace `general-legal-research` for general-only routes.

The test must answer:

- Does the merged agent find the same material legal issues?
- Does it cite the same or better primary and official sources?
- Does it preserve citation specificity and current-law discipline?
- Does it avoid game-regulation drift in pure general work?
- Does it produce an output that is easier to validate downstream?

## Non-Goals

- Do not edit `../legal-agent-orchestrator` during this parity phase.
- Do not make `legal-research-agent` the default for general-only routes based
  on deterministic fixture validation alone.
- Do not treat token savings, smaller prompts, or cleaner formatting as
  substitutes for legal research parity.
- Do not require the merged agent to copy the legacy answer style exactly.
  Better structure is acceptable if legal substance is preserved or improved.

## Test Set

Start with 8 general-only cases. Five is the minimum; 10 is better if time
allows.

| Case type | Example prompt shape | Required stress point |
|---|---|---|
| KR service/platform | Terms change, user notice, refund, consumer notice | statute plus regulator guidance |
| KR commercial/corporate | Distribution, agency, unfair terms, B2B risk | civil/commercial code plus agency guidance |
| KR administrative | License/reporting/sanction question | statute, decree, rule, agency guidance |
| KR employment | Contractor/employee, wage, dismissal, working time | statute plus official labor guidance |
| KR civil liability | Tort, damages, limitation, injunction | statute plus court/currentness check |
| US general | Federal/state split, consumer/platform issue | federal/state separation |
| EU general | regulation/directive/member-state split | EU hierarchy discipline |
| JP/UK general | official ministry/regulator source availability | foreign official-source handling |

Prefer real prompts from prior `general-legal-research` usage where available.
If old prompts are unavailable, write prompts that include enough facts to test
issue spotting and source planning.

## Artifact Layout

Use a separate parity workspace outside deterministic fixtures:

```text
output/general-legacy-parity/
  {case_id}/
    prompt.md
    legacy/
      general-legal-research-result.md
      general-legal-research-meta.json
      events.jsonl
    merged/
      legal-research-agent-result.md
      legal-research-agent-meta.json
      events.jsonl
    review/
      parity-review.md
      required-findings.json
      token-comparison-quality.json
```

Do not place live parity outputs under `tests/fixtures/` until a case has been
manually reviewed and converted into a stable deterministic fixture.

## Run Procedure

For each case:

1. Save the exact user prompt in `prompt.md`.
2. Run the legacy `general-legal-research` agent with no merged-agent context.
3. Run `legal-research-agent` in `research_mode = general` with equivalent
   route context.
4. Save both `events.jsonl` files when available.
5. Run local validation on the merged output:

```bash
python3 scripts/validate-output.py output/general-legacy-parity/{case_id}/merged
python3 scripts/check-result-structure.py output/general-legacy-parity/{case_id}/merged
python3 scripts/evaluate-quality.py output/general-legacy-parity/{case_id}/merged \
  --case-spec output/general-legacy-parity/{case_id}/review/required-findings.json
```

6. Complete the reviewer rubric in `review/parity-review.md`.
7. Record token evidence with `scripts/measure-tokens.py` or a
   `compare-token-runs.py` manifest only after quality review is complete.

## Review Rubric

Score each dimension from 0 to 3.

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Issue spotting | missed material issue | partial issue framing | same material issues | better framing or extra material issue |
| Source coverage | weak/secondary support | missing primary layer | same primary/official support | better or more current official support |
| Citation specificity | vague or unverifiable | source named but weak pinpoint | comparable pinpoint | clearer pinpoint/currentness |
| Legal hierarchy | hierarchy confused | some hierarchy gaps | hierarchy comparable | hierarchy cleaner than legacy |
| Currentness | stale or unchecked | currentness unclear | currentness comparable | explicit currentness/effective-date handling |
| Confidence discipline | overconfident | some caveats missing | comparable | more useful and conservative |
| Output usability | harder to review | structure helps but substance weaker | comparable | easier downstream validation |
| Mode isolation | game/general drift | small irrelevant game residue | no drift | tightly scoped general analysis |

Reviewer decision:

- `merged_win`
- `legacy_win`
- `tie`
- `inconclusive`

## Mandatory Failures

A merged output fails parity regardless of score if it:

- omits a material issue present in legacy or identified by reviewer;
- cites secondary commentary as controlling law when primary/official sources
  were reasonably available;
- misses a statute/decree/rule layer needed for the answer;
- ignores jurisdiction or legal hierarchy;
- gives high confidence while source coverage is incomplete;
- uses game-regulation framing in a pure general-law case;
- hides coverage gaps only in metadata;
- fabricates or unverifiably names a source.

## Pass Criteria

Do not approve general-only default replacement unless all are true:

- At least 8 reviewed general-only cases are complete.
- No mandatory failure remains unresolved.
- Merged is `tie` or `merged_win` in at least 75% of cases.
- Merged has zero critical issue-omission losses.
- Merged source coverage is not materially worse in any high-risk case.
- Token or agent-call savings are reported, but not used to offset quality
  losses.
- Any `legacy_win` case has a written remediation plan.

## Remediation Loop

For each `legacy_win`:

1. Identify whether the loss came from source planning, issue spotting,
   currentness, citation specificity, or mode drift.
2. Add a targeted skill or knowledge checklist only for the missing behavior.
3. Add or update deterministic quality expectations when possible.
4. Re-run the same case.
5. Record whether the loss is fixed, still open, or accepted as a reason to
   keep legacy routing.

Avoid broad prompt expansion unless multiple cases show the same failure mode.

## Fixture Promotion

Promote a parity case into deterministic fixtures only after manual review.

Promotion checklist:

- `required-findings.json` has stable required jurisdictions, domains, issue
  terms, result terms, source grades, and expected errors if any.
- The merged output has no live-only source placeholders.
- Source IDs and pinpoints are stable enough for deterministic checks.
- The case adds a failure mode not already covered by local fixtures.
- `scripts/evaluate-golden-set.py` still passes after promotion.

## Decision Record

At the end of the parity phase, write:

```text
docs/general-legacy-parity-decision.md
```

Include:

- case list and route pattern;
- reviewer decisions;
- mandatory failures found;
- remediations applied;
- unresolved legacy advantages;
- token and agent-call summary;
- final recommendation:
  - keep legacy default;
  - shadow-run merged only;
  - opt-in merged for selected general-only cases;
  - approve merged default for general-only routes.

## Recommended First Cases

Start with these five:

1. KR online-service terms-change notice.
2. KR refund/cancellation duty for digital service.
3. KR administrative license or reporting obligation.
4. KR employment contractor-vs-employee risk.
5. US or EU platform/consumer issue requiring jurisdiction hierarchy.

These are broad enough to expose whether the merged agent preserves general
legal research discipline without game-mode contamination.
