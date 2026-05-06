# Orchestrator Intake Payload

This repo does not edit `legal-agent-orchestrator`, but it keeps a local
contract for the payload the orchestrator should eventually pass to
`legal-research-agent`.

Validate examples with:

```bash
python3 scripts/validate-intake-payload.py tests/fixtures/intake-payloads
```

## Required Shape

```json
{
  "user_question": "...",
  "output_dir": "/path/to/output",
  "active_profile": "merged",
  "orchestrator_classification": {
    "domains": ["game_regulation"],
    "jurisdictions": ["KR"],
    "route_mode": "game_regulation",
    "agent_research_mode": "game_regulation",
    "confidence": "high"
  },
  "co_running_agents": [],
  "style_guide_path": null
}
```

## Validation Rules

- `active_profile` must be `merged` for this agent's runtime payload.
- `orchestrator_classification.domains` and `jurisdictions` must be non-empty
  string lists.
- `route_mode` must be canonical unless it is a supported composite route.
- Supported canonical research modes are:
  - `general`
  - `game_regulation`
  - `game_plus_general`
  - `fallback`
- Supported composite route modes currently include:
  - `game_and_data_protection`
- Composite route modes must include a canonical `agent_research_mode`.
- If both `route_mode` and `agent_research_mode` are canonical, they must match.
- Data-protection composite payloads must include a co-running specialist owner.
- Legacy agent IDs must not appear in `co_running_agents` or `selected_agents`.
- If `selected_agents` is provided, duplicate `legal-research-agent` entries
  fail because deduplication should happen before dispatch.

## Classification Mismatch

The intake payload should still preserve the orchestrator route. If the user
question visibly looks like another mode, the agent records the mismatch in
output metadata and coverage gaps rather than silently changing modes.
