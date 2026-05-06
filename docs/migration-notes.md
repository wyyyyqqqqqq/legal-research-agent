# Migration Notes

## Canonical Agent

- New canonical ID: `legal-research-agent`

## Legacy Mapping

| Legacy role | Merged behavior |
|---|---|
| `general-legal-research` | `research_mode = general` |
| `game-legal-research` | `research_mode = game_regulation` or `game_plus_general` |

## First Rollout Scope

The first rollout replaces only the two legacy research roles above. It does not
consolidate data-protection specialists or change writing/review agents.

## Behavioral Changes

- Orchestrator classification is primary.
- Composite routes may include `agent_research_mode` for the merged agent.
- Duplicate mapped `legal-research-agent` entries must be deduplicated before
  dispatch.
- `legacy_scope` is not emitted in per-run metadata.
- `active_profile` and route details should be recorded in route artifacts.

## Rollback

Use the orchestrator's legacy profile to restore previous routing behavior.
Golden-set outputs should be stored in separate directories for comparison.
