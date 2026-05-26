# Conflict Report Template

Use this template when primary or official sources appear to disagree about a
definition, scope boundary, obligation, sanction, effective date, or applicable
legal hierarchy. The report is a research control, not a substitute for the
final memo.

## Use When

Prepare a conflict report when any of these conditions appears:

- two sources support materially different answers to the same issue;
- a newer source may supersede or narrow an older source;
- a delegated rule may exceed, narrow, or fail to implement the parent rule;
- a national, state, local, or sector-specific rule may change the answer;
- a source is current for one date, entity, product, or jurisdiction but not
  another;
- a high-confidence conclusion would otherwise rely on unresolved hierarchy or
  recency assumptions.

Do not use this report for ordinary source gaps where no contradictory source
has been found. Record those in `coverage_gaps` instead.

## Conflict Summary

```text
Issue:
Jurisdiction(s):
Research mode:
Conflict type:
Severity: High / Medium / Low
Affected conclusion:
Current answer if resolved:
Answer if unresolved:
```

Severity guide:

| Severity | Use when | Required handling |
|---|---|---|
| High | Obligation, prohibition, sanction, eligibility, deadline, or market-entry answer changes | Re-enter source collection before finalizing unless impossible. |
| Medium | Scope, definition, transitional rule, or effective-date answer changes | Resolve if feasible; otherwise downgrade confidence and isolate affected period or population. |
| Low | Secondary-source phrasing, non-controlling terminology, or background context differs | Explain briefly or omit if immaterial. |

## Source Conflict Matrix

| Source ID | Source / issuer | Grade | Legal status | Date checked | Pinpoint | Position supported | Limitation |
|---|---|---:|---|---|---|---|---|
| `src_001` | | A/B/C | statute / regulation / guidance / decision / commentary | | | | |
| `src_002` | | A/B/C | statute / regulation / guidance / decision / commentary | | | | |

Rules:

- Each row must cite an `authority_id` or source ID that also appears in
  metadata.
- Use original-language text where it controls.
- Identify whether each source is current, pending, stale, superseded, or not
  checked under `skills/currentness-check.md`.
- Do not resolve the conflict by source grade alone. Apply hierarchy, scope,
  date, and legal effect.

## Legal Hierarchy Analysis

Explain the governing hierarchy before choosing a source:

| Question | Answer |
|---|---|
| Which source is higher in legal hierarchy? | |
| Which source is more specific to the issue? | |
| Which source is later in time? | |
| Which source has binding effect? | |
| Which source is merely interpretive, explanatory, or secondary? | |
| Does the lower-level rule implement a delegation from the higher-level rule? | |

Resolution order:

1. jurisdiction and legal authority;
2. hierarchy and binding effect;
3. delegated-rule authority and limits;
4. special law over general law;
5. currentness and effective date;
6. original text over summary;
7. official source over secondary commentary.

## Currentness and Effective-Date Analysis

| Source ID | Temporal status | Effective date | Amendment date | Transition rule | Applies to facts? |
|---|---|---|---|---|---|
| `src_001` | checked_current / pending_change / stale_or_superseded / not_checked | | | | |
| `src_002` | checked_current / pending_change / stale_or_superseded / not_checked | | | | |

Minimum checks:

- current consolidated text or official version status;
- effective date and enforcement date if different;
- supplementary provisions, transition periods, and grandfathering;
- pending amendments where the user asks for launch, compliance planning, or
  future conduct;
- date of the user's conduct or intended activity.

If the effective date is unresolved for a material rule, the final answer must
say so and lower confidence.

## Jurisdiction and Scope Analysis

Use this section to separate conflicts that only appear to overlap:

| Scope axis | Finding |
|---|---|
| Geography | |
| Entity type | |
| Product or activity | |
| Consumer / business / minor / regulated-person status | |
| Online / offline / platform / intermediary role | |
| Sector-specific carve-out | |
| Procedural posture | |

If two sources govern different scopes, state that there is no true conflict
and explain which source controls which scope.

## Korean-Specific Conflict Patterns

For Korean law, check these patterns before resolving:

| Pattern | Required check | Tag if unresolved |
|---|---|---|
| Law vs. Enforcement Decree | Does the decree stay within delegated authority from the parent statute? | `[Unresolved Conflict - delegation limit]` |
| Law vs. Enforcement Rule or Notice | Does the lower rule implement a statute/decree provision, or add an unsupported obligation? | `[Unresolved Conflict - lower rule authority]` |
| National law vs. local ordinance | Is there explicit statutory delegation or permissible local scope? | `[Unresolved Conflict - ordinance authority]` |
| Old law vs. new law | Do supplementary provisions preserve old-law application? | `[Unresolved Conflict - transition rule]` |
| General law vs. special law | Does the special law cover the entity, data, transaction, or conduct? | `[Unresolved Conflict - special law scope]` |
| Official Korean text vs. translation | Is the translation official and complete? | `[Unresolved Conflict - translation only]` |

Use Korean legal labels in the memo where helpful, but keep this template's
source IDs and confidence treatment intact.

## Resolution Path

```text
Resolved? Yes / No / Partly
Controlling source(s):
Source(s) distinguished:
Reason:
Affected conclusion wording:
Confidence impact:
```

Resolution examples:

- higher-level rule controls unless valid delegation makes the lower rule
  operative;
- later law controls only for conduct or facts within its effective period;
- special law controls only within its subject-matter scope;
- agency guidance may explain enforcement posture but cannot override the
  statute;
- secondary commentary may discover a conflict but cannot resolve a high-risk
  conflict by itself.

## Research Re-Entry Plan

For high-severity or unresolved medium-severity conflicts, list the next
research actions:

| Step | Source or action | Purpose | Stop condition |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

Re-enter source collection when:

- the answer changes a legal obligation, prohibition, sanction, or deadline;
- hierarchy cannot be resolved from collected sources;
- a currentness gap affects a launch or compliance-planning answer;
- the only support for the preferred answer is secondary commentary.

## Confidence Impact

| Conflict status | Confidence treatment |
|---|---|
| Fully resolved by primary or official source | Confidence may remain high if other quality gates pass. |
| Resolved only by secondary commentary | Medium at most; cite the secondary source as context only. |
| Partly resolved by scope distinction | Confidence high only for the resolved scope; lower elsewhere. |
| Currentness unresolved | Medium or low depending on materiality; state date limitation. |
| Hierarchy unresolved | Low for the affected conclusion unless the memo is framed as issue spotting. |

Do not use "clear" or equivalent high-certainty language for a material
conclusion with an unresolved hierarchy, currentness, or sanction conflict.

## Final Answer Wording

Use this wording pattern in the final memo:

```text
The better-supported answer is [conclusion] for [scope/period], because
[controlling source] governs [reason]. [Contrary source] does not change that
answer because [scope/hierarchy/currentness distinction]. Confidence is
[level] because [remaining gap or no remaining gap].
```

If unresolved:

```text
The source record is incomplete on [conflict]. The available sources support
[narrow conclusion] only for [scope]. I would not treat [broader conclusion] as
settled without [missing source/check].
```

## Citation Appendix

List only the authorities needed to audit the conflict:

| Source ID | Short citation | Pinpoint | Use in conflict analysis |
|---|---|---|---|
| `src_001` | | | |
| `src_002` | | | |

## Quality Checklist

- [ ] Every conflict row has a source ID and pinpoint.
- [ ] Currentness and effective date were checked or explicitly marked.
- [ ] Legal hierarchy was analyzed before source grade.
- [ ] Scope differences were separated from true contradictions.
- [ ] Korean delegated-rule and supplementary-provision checks were performed
      where Korean law is involved.
- [ ] High-severity conflicts triggered source re-entry or an explicit
      limitation.
- [ ] The final memo's confidence language matches the unresolved-risk level.
- [ ] Secondary commentary was not used to override primary or official law.
