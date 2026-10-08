---
name: jurisdiction-source-playbook
description: Use after mode classification and before source collection — turns the user question into a jurisdiction-specific source plan.
disable-model-invocation: true
---

# Jurisdiction Source Playbook

Use this skill after mode classification and before source collection. Its job
is to turn a user question into a jurisdiction-specific source plan.

The canonical jurisdiction-source priority registry is
`legal_sources.yaml` at the project root. Use it via
`scripts/legal_source_registry.py show <jurisdiction>` to retrieve
the controlling primary-source list and MCP fallback policy. The
prose below describes the strategy; the registry is the source of
truth for URLs and Grade defaults.

For Korean-law jurisdictional structure (statute hierarchy, ministerial
rule conventions, court-system layout), consult
`references/korean-law-reference.md`.

## Jurisdiction Profile

Create a compact jurisdiction profile for each requested jurisdiction:

```json
{
  "jurisdiction": "KR",
  "legal_system_notes": "civil law; statute and delegated rules are central",
  "primary_regulators": ["agency-or-court"],
  "likely_source_types": ["statute", "delegated regulation", "official guidance"],
  "language": "ko",
  "currentness_method": "check amendment history and supplementary provisions",
  "coverage_risks": ["unverified delegated rule", "missing agency notice"]
}
```

Do not merge profiles across jurisdictions. Build the profiles separately, then
synthesize later.

## Source Minimums

Use these minimums unless the task is a narrow directly verified lookup:

| Task type | Minimum source plan |
|---|---|
| Single-jurisdiction statutory question | current statute or regulation plus any delegated rule that changes operation |
| Regulator or procedure question | official agency page, notice, guideline, form, or decision plus legal basis |
| Sanctions or enforcement question | legal basis plus official enforcement release, decision, or penalty schedule where available |
| Multi-jurisdiction comparison | at least one controlling or official source per jurisdiction before synthesis |
| Specialist handoff | game/general framing source plus explicit handoff note to the specialist owner |

If the minimum cannot be met, lower confidence and add a `coverage_gaps` entry.

## Korea

For KR research:

1. Identify the controlling act and delegated rule chain:
   - act;
   - enforcement decree;
   - enforcement rule;
   - notice, guideline, form, or agency interpretation.
2. Check supplementary provisions before stating effective dates, transition
   rules, grandfathering, or penalties.
3. Identify the competent agency before collecting guidance.
4. Prefer current official Korean text over translations.
5. Use translations only as reading aids unless they are official.
6. Preserve Korean legal terms when translation could affect the answer.

Record unresolved Korean-source limitations as `mcp_unavailable`,
`partial_sources`, or `source_coverage_insufficient` when material.

## United States

For US research:

1. Separate federal law, state law, local law, and agency guidance.
2. Identify whether state variation is material.
3. Do not generalize "US law" when the answer turns on state law.
4. Use official agency, statute, regulation, and court sources where possible.
5. Treat private platform rules, trade association material, and commentary as
   non-primary unless a legal source gives them effect.

If the user does not specify a state and state law is material, either ask for a
state when interactive clarification is available or record state variation as a
coverage gap.

## European Union

For EU research:

1. Distinguish regulations, directives, delegated acts, guidance, and national
   implementation.
2. Check consolidated text and effective dates.
3. Do not state that "the EU requires" something if member-state law controls
   the practical answer.
4. For consumer, platform, data, and game-adjacent issues, identify whether the
   operative rule is EU-level, member-state-level, or both.

When a data-protection specialist is co-running, this agent should identify the
handoff point and avoid duplicating detailed GDPR analysis.

## Japan

For JP research:

1. Identify the ministry, agency, or commission responsible for the issue.
2. Separate statutes, cabinet orders, ordinances, agency guidance, and industry
   self-regulation.
3. Treat self-regulatory material as context unless official law gives it
   binding or practical legal effect.
4. Verify consumer, prize, payment, gambling, and youth-protection issues
   against official sources where possible.

  ## Australia

For AU research:

1. Identify whether the relevant rule operates at the Commonwealth, State, or Territory level.

2. Do not generalize one State or Territory rule as "Australian law" where subnational variation is material.

3. Where Commonwealth and State or Territory law may overlap, identify and research each legal layer separately before synthesizing the practical position.

4. Identify the competent court, tribunal, regulator, government agency, or other authoritative body where relevant before collecting guidance, decisions, enforcement materials, or administrative sources.

5. Distinguish between relevant source types, including primary and delegated legislation, court and tribunal decisions, regulator and government materials, official registers and administrative decisions, contracts and licences, treaties and international instruments, industry codes and recognised standards, and secondary academic or practitioner commentary.

6. Prefer current primary or official Australian sources for material legal propositions. Use secondary sources principally for source discovery, context, interpretation, or identifying unresolved issues.

7. Check currentness before relying on controlling law, including consolidated legislation, amendments, commencement provisions, transitional provisions, and relevant current decisions or guidance.

8. Treat the source registry in `legal_sources.yaml` as a set of preferred starting points rather than a closed list. Where the facts or legal issues require sources not listed in the registry, identify and use additional authoritative Australian sources consistent with the source-first and source-grading rules.

9. Where the answer materially depends on State or Territory variation and the relevant jurisdiction is unknown, seek clarification where possible or record the variation as a coverage gap.

10. Record unresolved jurisdictional allocation, source availability, currentness, or authority questions as coverage gaps rather than inferring a uniform Australian position.

## Cross-Border And Comparisons

For any comparison:

1. Build separate issue trees by jurisdiction.
2. Add `comparison_matrix` when differences affect launch, disclosure,
   procedure, risk, or handoff strategy.
3. Use columns such as:
   - issue;
   - jurisdiction;
   - controlling source;
   - obligation or rule;
   - practical action;
   - confidence;
   - coverage gap.
4. Synthesize only after the jurisdiction rows are supported.

## Stop Conditions

Do not proceed to confident analysis when:

- the controlling jurisdiction is unknown;
- the legal hierarchy is unclear;
- a required delegated rule or regulator source is missing;
- a source is secondary but being used as primary law;
- the answer turns on currentness and currentness was not checked.

Use fallback mode or a coverage-gap result when these conditions cannot be
resolved within the available run.
