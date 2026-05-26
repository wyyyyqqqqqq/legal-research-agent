# Privacy Law Updates Reference Pack

Detailed briefing framework for `skills/specialists/privacy-law-updates.md`.
Load this pack only when preparing, tailoring, or quality-checking a privacy or
data-protection update.

This pack is procedural. It identifies what to verify and how to structure the
briefing; it is not a cached statement of current privacy law.

## Quick Start

1. Fix the reporting period and jurisdictions.
2. Classify each development by legal status and effective date.
3. Build jurisdiction-first update sections before cross-cutting synthesis.
4. Separate enacted law and final guidance from proposals or consultations.
5. Track compliance deadlines, enforcement signals, and operational impact.
6. Apply the output quality checklist before finalizing.

## Intake

| Item | Required | Notes |
|---|---:|---|
| Reporting period | Yes | Default to past 12-18 months only when user is silent. |
| Jurisdictions | Yes | Use exact jurisdictions; avoid "global" unless scoped. |
| Industry or product | Yes | Platform, game, fintech, health, adtech, SaaS, AI, etc. |
| Data categories | If known | Children, biometric, health, financial, precise location, sensitive data. |
| Processing activities | If known | Ads, analytics, profiling, transfers, automated decisions, breach response. |
| Audience | Yes | Executive, legal/compliance, product, or mixed. |
| Output mode | If specified | Executive brief, matrix, canonical memo, handoff, or DOCX-ready. |

## Development Taxonomy

Use one primary type per development:

| Type | Treatment |
|---|---|
| Enacted statute | Verify enactment, effective date, compliance date, amendments, and codified text. |
| Final regulation or rule | Verify final publication, effective date, regulated entities, and transition periods. |
| Proposed law or rule | Label as proposed; include procedural status and avoid treating as binding. |
| Official guidance | Identify issuer, legal effect, issue date, and whether it supersedes earlier guidance. |
| Enforcement action | Capture order, fine, remedy, conduct, authority, and precedential limits. |
| Court decision | Capture holding, procedural posture, jurisdiction, and appeal status if material. |
| Consultation or draft guidance | Label as non-final; include comment deadline and expected next step. |
| Regulator priority statement | Treat as enforcement signal, not binding law unless tied to authority. |

Never combine enacted and proposed developments in the same bullet without
explicit labels.

## Jurisdiction Update Template

Use this structure for each jurisdiction:

```text
### [Jurisdiction]

#### [Development title]
- Type:
- Status:
- Issuer / authority:
- Date issued:
- Effective date:
- Compliance deadline:
- Scope:
- Key requirements or holding:
- Delta from prior framework:
- Operational impact:
- Penalties or remedies:
- Source IDs:
- Confidence / gaps:
```

Rules:

- Include at least one official or primary source for each material
  development.
- If currentness is not checked, mark the development `not_checked` and lower
  confidence.
- If the source is a proposal, use "would" or "proposed to"; do not use "must".

## Effective-Date and Deadline Tracker

For compliance planning, add a tracker:

| Jurisdiction | Development | Effective date | Compliance deadline | Transition period | Affected function | Source ID |
|---|---|---|---|---|---|---|
| | | | | | | |

Minimum checks:

- effective date vs. enforcement or compliance date;
- phased obligations;
- grandfathering or transition rules;
- regulator grace periods;
- pending amendments that may change near-term compliance.

## Enforcement Tracker

When enforcement is relevant:

| Jurisdiction | Authority | Date | Conduct | Legal basis | Remedy / penalty | Signal | Source ID |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

Capture:

- whether the action is final, settled, appealed, or pending;
- whether the conduct maps to the user's product or industry;
- whether the remedy is monetary, injunctive, operational, deletion, audit, or
  governance-focused;
- whether the action is a one-off fact pattern or part of a stated priority.

## Pending and Proposed Law Treatment

Use status labels:

| Label | Meaning |
|---|---|
| `enacted_not_effective` | Enacted but not yet effective or enforceable. |
| `proposed` | Introduced or proposed; not binding. |
| `consultation_open` | Draft or consultation with open comments. |
| `final_pending_publication` | Final action announced but official publication not yet verified. |
| `withdrawn_or_failed` | No longer active; include only if useful context. |

Rules:

- Pending proposals may support monitoring recommendations, not current-law
  compliance conclusions.
- Legislative likelihood should not be editorialized. State procedural status
  and known next steps.
- If a proposed rule has a comment deadline, include it in the deadline tracker.

## Cross-Cutting Topic Matrix

Use after jurisdiction-first sections:

| Topic | Jurisdictions affected | Change type | Operational impact | Deadline | Source IDs |
|---|---|---|---|---|---|
| Cross-border transfers | | | | | |
| Consent and notice | | | | | |
| Data-subject rights | | | | | |
| Breach notification | | | | | |
| AI / automated decisions | | | | | |
| Children's privacy | | | | | |
| Biometric data | | | | | |
| Advertising / profiling | | | | | |
| Health data | | | | | |
| Financial data | | | | | |

Cross-cutting synthesis must not erase jurisdictional differences. If the same
topic has different effective dates or legal tests, keep the distinctions in
the matrix.

## Source Minimums

For every material development, prefer:

1. statute, regulation, official decision, or official guidance;
2. official explanatory notes or regulator press releases;
3. respected practitioner summaries only for discovery or context.

Minimum source layers by development type:

| Development | Minimum source layer |
|---|---|
| Enacted law | Official enacted text or consolidated code. |
| Final rule | Official final rule publication and agency page if separate. |
| Guidance | Official issuing-authority guidance page or PDF. |
| Enforcement | Official order, decision, settlement, press release, or docket. |
| Court decision | Official or reliable court text with posture. |
| Proposal | Official bill, consultation, notice, or rulemaking docket. |

## Output Quality Checklist

- [ ] Reporting period and jurisdictions are explicit.
- [ ] Each development has a status label and source ID.
- [ ] Effective dates and compliance deadlines are separated.
- [ ] Proposed and pending materials are not phrased as binding law.
- [ ] Enforcement items identify conduct, authority, remedy, and status.
- [ ] Jurisdiction-specific sections precede cross-cutting synthesis.
- [ ] Sector carve-outs are checked where relevant.
- [ ] Currentness gaps are recorded in `coverage_gaps`.
- [ ] Executive-facing summaries preserve the same source-backed status labels.

## Pitfalls

- Treating a bill, consultation, or draft guidance as current law.
- Collapsing US state privacy laws into a single US rule.
- Treating GDPR-adjacent national implementation as uniform across the EU.
- Missing children's, biometric, health, financial, or advertising-specific
  overlays.
- Quoting enforcement amounts without explaining the conduct and legal basis.
- Using regulator priority speeches as binding obligations.
- Omitting effective dates when the user asks for launch or roadmap planning.
