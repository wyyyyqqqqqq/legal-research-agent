# General Law Source Playbook

Use this skill in `general` mode and for the general-law branch of
`game_plus_general` after `jurisdiction-source-playbook.md` and before final
source collection.

Its job is to select the right domain source layers, load any matching compact
playbook, and define source minimums before analysis begins.

## Source Playbook Selection

1. Identify the jurisdiction.
2. Identify the legal domain using the closest vocabulary from
   `knowledge/general/domain-source-checklist.md`.
3. Check `knowledge/general/source-playbook-index.json` for an `active`
   playbook matching the jurisdiction and domain.
4. If a matching active playbook exists, load only that compact playbook.
5. If no active playbook exists, use the domain checklist and record that no
   domain-specific playbook was available when the limitation is material.

Do not load every playbook. Playbooks are narrow source-layer tools, not a
general prompt bundle.

## Source Layer Plan

For each material issue, create a compact source layer plan before collecting
sources:

```json
{
  "issue_id": "issue_001",
  "jurisdiction": "KR",
  "domain": "platform_service",
  "required_layers": ["statute", "delegated_rule", "regulator_guidance"],
  "active_playbook_id": "kr-platform-service",
  "missing_layers": [],
  "confidence_ceiling": "high"
}
```

Use `confidence_ceiling` conservatively:

- `high`: required source layers are checked or clearly not applicable.
- `medium`: one useful official layer is missing but the core rule is supported.
- `low`: controlling law, delegated rules, or currentness are not verified.
- `fallback`: the answer is primarily source-limited or jurisdiction-limited.

## Required Source Layer Types

Use these normalized layer names in planning notes where possible:

- `statute`
- `delegated_rule`
- `regulator_guidance`
- `official_procedure`
- `case_law`
- `agency_decision`
- `sanction_or_enforcement`
- `currentness`
- `member_state_or_state_law`
- `secondary_context`

Secondary context can help discovery, but it does not satisfy a required
controlling-law layer.

## Confidence Rule

Do not mark an issue `high` confidence unless:

- the controlling jurisdiction is identified;
- the required source layers from the domain checklist or active playbook were
  checked;
- delegated rules were checked when statutes delegate operative detail;
- currentness and effective date were checked for controlling sources; and
- any missing layer is immaterial and explained.

If a required layer is missing, add a `coverage_gaps` entry and visibly caveat
the answer.

## General-Law Domain Defaults

Use `knowledge/general/domain-source-checklist.md` when no active playbook
exists. If the user's issue maps to more than one domain, apply the stricter
minimum for each material issue rather than averaging the domains.

Examples:

- A Korean platform terms-change question may need platform-service,
  consumer/e-commerce, and contracts/commercial layers.
- A US service suspension question may require state law if contract or consumer
  law controls.
- An EU platform question may require member-state implementation when a
  directive or national procedure controls the practical answer.

## Stop Conditions

Pause before confident analysis when:

- the active playbook requires a source layer that has not been checked;
- the domain checklist requires state, member-state, delegated-rule, agency, or
  case-law coverage and it is absent;
- currentness is unknown for a controlling source;
- only Grade C or D sources support a controlling legal proposition.

If the source layer cannot be resolved in the current run, proceed only with a
source-limited result and lower confidence.
