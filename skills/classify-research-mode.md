---
name: classify-research-mode
description: Use only when the orchestrator route is missing or uncertain — self-classifies the research mode.
disable-model-invocation: true
---

# Classify Research Mode

Use this skill only when the orchestrator did not provide a valid
`agent_research_mode` or canonical `route_mode`, or when the provided route is
explicitly uncertain.

## Canonical Modes

- `general`
- `game_regulation`
- `game_plus_general`
- `fallback`

## Precedence

1. If `orchestrator_classification.agent_research_mode` is present, use it.
2. Otherwise, if `orchestrator_classification.route_mode` is canonical, use it.
3. If the route looks inconsistent with the question, keep the routed mode and
   add `classification_mismatch` to `classification_warnings`.
4. If no route is usable, self-classify.
5. If self-classification is uncertain, use `fallback`.

## Self-Classification Rules

Use `game_regulation` when the facts involve:

- online, mobile, PC, console, or cloud games
- game publishing or distribution
- app-store or platform compliance for a game product
- loot boxes, gacha, random rewards, or probability disclosure
- game age ratings or youth protection
- game advertising, influencer marketing, dark patterns, or monetization
- virtual items, paid currency, cash-out boundaries, or gambling adjacency
- game consumer protection or refund issues

Use `game_plus_general` only when:

- the question is game-industry framed; and
- there is a distinct non-game legal issue that cannot be handled as adjacency.

Examples of distinct non-game issues:

- corporate licensing unrelated to game publishing rules
- tax treatment
- employment or labor issue
- securities, finance, or corporate governance issue
- non-game platform liability

Use `general` when:

- no narrower specialist is required; and
- the question is not game-industry framed.

Use `fallback` when:

- jurisdiction or domain is unclear;
- source coverage is materially insufficient; or
- the subject falls outside this agent's competence and no better specialist is
  available.

## Metadata

Record:

```json
{
  "research_mode": "game_regulation",
  "mode_source": "orchestrator|self_classified",
  "orchestrator_route_mode": "game_regulation",
  "fallback_reason": null,
  "classification_warnings": []
}
```

If the route and question visibly diverge:

```json
{
  "classification_warnings": ["classification_mismatch"],
  "coverage_gaps": [
    {
      "type": "classification",
      "description": "Question appears game-related, but orchestrator route was general."
    }
  ]
}
```
