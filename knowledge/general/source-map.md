# General Legal Research Source Map

> **Source of truth:** `legal_sources.yaml` at the project root. This
> document is a human-readable narrative; URLs and grades come from
> the registry.

This file lists source categories. It is not a cached legal database.

## General Priority

1. Primary law: statutes, regulations, treaties, binding decisions.
2. Official guidance: regulator guidance, official FAQs, agency notices.
3. Official explanatory material.
4. Respected practitioner guides and academic commentary.
5. Secondary commentary only when primary sources are unavailable or incomplete.

## Source Category Rules

Use source categories consistently:

| Category | Examples | Default grade | Notes |
|---|---|---:|---|
| Primary law | statutes, regulations, decrees, binding rules, treaties | A | Verify currentness and pinpoint. |
| Binding decisions | court decisions, agency decisions, tribunal decisions | A | Confirm precedential or binding status where relevant. |
| Official guidance | regulator guidance, official FAQs, notices, forms | A/B | Grade depends on legal effect and issuer. |
| Official explanatory material | legislative notes, regulator press releases | B | Useful for context, not a substitute for law. |
| Practitioner or academic commentary | law firm alerts, treatises, articles | C | Use for discovery and context unless independently verified. |
| Unreliable material | anonymous summaries, marketing pages, uncited AI output | D | Do not cite for legal propositions. |

For every controlling proposition, try to connect at least one Grade A or strong
Grade B source to the relevant `issue_map` entry.

## Domain Playbooks

Before source collection for `general` mode, apply
`skills/general-law-source-playbook.md`.

Default domain source-layer minimums live in:

```text
knowledge/general/domain-source-checklist.md
```

Registered focused playbooks live in:

```text
knowledge/general/source-playbook-index.json
knowledge/general/playbooks/
```

Use active playbooks only when jurisdiction and domain match the issue. If no
active playbook exists, use the domain checklist and record the limitation when
it materially affects confidence.

## Korea

Prefer `korean-law` MCP where available for:

- statute text
- enforcement decrees
- amendments
- official decisions
- regulator guidance

If unavailable, use official public sources where possible and record the
limitation.

Korean source planning:

1. Identify the act, enforcement decree, enforcement rule, notice, and guidance
   chain before answering.
2. Check supplementary provisions for effective dates, transitional rules, and
   amendment timing.
3. Check the responsible regulator before relying on non-specialist commentary.
4. Prefer original Korean official text. Use translations only as reading aids
   unless official.
5. For sanctions, find the legal basis plus any penalty schedule, enforcement
   release, or official decision where available.

Common Korean source risks:

- delegated rules change the operative answer;
- an old article number survives in commentary after amendment;
- agency notices or forms contain procedure that the statute only sketches;
- unofficial translations omit exceptions or supplementary provisions;
- court or agency decision summaries obscure the holding.

## United States

US research must not collapse federal and state law.

Use official sources where available:

- US Code and Code of Federal Regulations;
- federal agency guidance, rules, advisory opinions, and enforcement releases;
- state statutes, regulations, attorneys general material, and regulator
  guidance;
- court decisions from official or reliable court databases.

US source planning:

1. Identify whether federal, state, or both levels control the answer.
2. If state law is material and no state is specified, record the state-law gap
   or ask for clarification when allowed.
3. Treat platform terms, industry standards, and trade association material as
   commercial or self-regulatory unless law incorporates them.
4. Separate binding law from agency guidance and enforcement posture.

## European Union

Use official EU and member-state sources where possible:

- EUR-Lex consolidated text and procedural status;
- European Commission guidance and official notices;
- EU agency or board guidance where relevant;
- member-state statutes, regulator guidance, and enforcement decisions.

EU source planning:

1. Distinguish regulations from directives and national implementation.
2. Check whether the operative issue is EU-level, member-state-level, or both.
3. Verify effective dates, transitional periods, and current consolidated text.
4. Do not generalize across member states when national implementation controls.

## Japan

Use official Japanese sources where possible:

- statutes, cabinet orders, ministerial ordinances, and official guidance;
- Consumer Affairs Agency, MIC, METI, FSA, or other competent agency materials;
- official court or agency decisions where relevant.

Japan source planning:

1. Identify the competent ministry, agency, or commission.
2. Separate statutory obligations from industry self-regulation.
3. Verify consumer, advertising, payment, youth, and platform issues against
   official sources before relying on commentary.
4. Treat English summaries as secondary unless official and current.

## United Kingdom

Use official UK sources where possible:

- legislation.gov.uk for statutes and statutory instruments;
- regulator guidance, enforcement notices, and decisions;
- court and tribunal decisions from official or reliable sources.

UK source planning:

1. Check whether the rule differs across England and Wales, Scotland, or
   Northern Ireland.
2. Distinguish statute, statutory instrument, regulator guidance, and codes.
3. Verify retained, assimilated, or post-Brexit rule status where material.

## Foreign Law

For non-Korean law:

- identify the jurisdiction precisely;
- use official government or regulator sources where possible;
- record when only secondary commentary was available;
- avoid high-confidence conclusions based only on secondary sources.

## Cross-Jurisdiction Questions

For comparisons:

- answer each jurisdiction separately first;
- then synthesize differences and shared compliance themes;
- record missing jurisdictions or incomplete official source coverage in
  `coverage_gaps`.
- use `comparison_matrix` when differences affect launch timing, compliance
  workflow, disclosure wording, sanctions, or specialist handoff.

## Minimum Coverage By Deliverable

| Deliverable | Minimum coverage before confident answer |
|---|---|
| Quick answer | one controlling official source, or two if delegated rules matter |
| Research memo | source plan, issue tree, controlling authority, counter-analysis |
| Compliance checklist | controlling rule, procedure/form source, enforcement or sanctions source |
| Multi-jurisdiction comparison | jurisdiction-specific sources before synthesis |
| Handoff note | source-backed framing plus specialist owner and unresolved question |

If the minimum cannot be met, use conservative confidence and explain the gap.
