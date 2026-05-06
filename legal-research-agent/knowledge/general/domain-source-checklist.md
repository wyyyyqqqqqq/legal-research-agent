# General Domain Source Checklist

This checklist gives default source-layer minimums for general legal research.
Use it when no active source playbook exists, or as a baseline before applying a
more specific playbook.

## How To Use

1. Pick the closest domain for each material issue.
2. Apply the jurisdiction profile from `skills/jurisdiction-source-playbook.md`.
3. Apply any active matching playbook from
   `knowledge/general/source-playbook-index.json`.
4. Treat the rows below as minimum source layers, not exhaustive research.
5. If a required layer is missing, lower confidence and record a coverage gap.

## Domain Minimums

| Domain | Required source layers |
|---|---|
| KR platform/service | statute; enforcement decree/rule; competent regulator guidance, notice, FAQ, or enforcement position; consumer/e-commerce guidance where the service relationship affects users |
| KR contracts/commercial | Civil Act or Commercial Act provision; special statute if it displaces the default rule; Fair Trade Commission or competent regulator guidance where relevant; case law when interpretation or damages turns on doctrine |
| KR administrative | statute; enforcement decree/rule; notice, guideline, form, or procedure source; competent agency FAQ or enforcement position; sanction basis where risk or penalty is material |
| KR employment | Labor Standards Act or special employment statute; enforcement decree/rule; Ministry guidance or administrative interpretation; cases or labor commission decisions where needed |
| KR civil liability | statute; Supreme Court or court cases when rule depends on interpretation; limitation period and remedy source; damages or causation authority where material |
| KR consumer/e-commerce | Framework Act, E-Commerce Act, Consumer Protection Act, or special statute; enforcement decree/rule; Korea Consumer Agency or Fair Trade Commission guidance; refund, cancellation, disclosure, or unfair-practice source where relevant |
| US general | federal/state split; federal statute/regulation if controlling; state statute/regulation when state law controls; agency guidance or enforcement release; case law where doctrine-driven |
| EU general | regulation/directive distinction; consolidated EU text and procedural status; member-state implementation when practical obligations depend on national law; Commission, EDPB, ESA, or regulator guidance where relevant |
| JP general | statute; cabinet order or ministerial ordinance; competent ministry or agency guidance; official Q&A or notice where practical compliance depends on it; court or agency decision where interpretation is controlling |
| UK general | statute; statutory instrument or regulation; regulator guidance, code, notice, or decision; case law where doctrine-driven; devolved-nation variation where material |

## Confidence Consequences

- Missing controlling statute or regulation: confidence ceiling is `low`.
- Missing delegated rule where the statute delegates operative detail:
  confidence ceiling is `medium` unless the gap is immaterial.
- Missing currentness check for controlling law: confidence ceiling is `medium`
  or lower.
- Reliance only on secondary commentary for a controlling proposition:
  confidence ceiling is `low`.
- Missing state, member-state, or devolved law where local law controls:
  confidence ceiling is `fallback` or `low`.

## Coverage Gap Labels

Use specific coverage-gap labels when a minimum cannot be met:

- `source_coverage_insufficient`
- `delegated_rule_missing`
- `agency_guidance_missing`
- `case_law_missing`
- `state_law_missing`
- `member_state_law_missing`
- `temporal_status`
- `secondary_only`

## Checklist Maintenance

When a domain row becomes too broad for recurring work, add a focused playbook
under `knowledge/general/playbooks/` and register it in
`knowledge/general/source-playbook-index.json`.
