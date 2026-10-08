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

## User Config Precedence

When `user-config.json` is present and the run is standalone:

1. If the user-supplied question explicitly names a research mode, use it.
2. Else if `output_preferences.default_research_mode` is set in the
   config, use it as the starting hypothesis.
3. Else self-classify per the rules below.

When the run is a subagent dispatch (orchestrator-supplied intake
payload), the standard `## Precedence` rules apply — `user-config.json`
is ignored because the orchestrator owns classification.

If the config-suggested mode is inconsistent with the question facts,
record `classification_warnings: ["config_mismatch"]` and continue
with the routed mode rather than silently switching.

## Self-Classification Rules

Use `game_regulation` when the question is materially connected to the development, publishing, distribution, operation, monetization, marketing, launch, maintenance, or commercial exploitation of a video game, online game, mobile game, cloud game, or related digital game product.

Classification should be based primarily on the factual and business context rather than on whether the question matches a predefined legal category or keyword list.

Relevant game-industry facts may include product mechanics, monetization models, users, distribution channels, platforms, technologies, commercial relationships, content, marketing, live-service operation, cross-border launch, or other aspects of the game business.

Examples may include loot boxes, gacha, age ratings, advertising, virtual goods, consumer protection, privacy, intellectual property, employment, tax, competition, payments, platform rules, online safety, contracts, regulatory approvals, or other legal issues arising from the game business. These examples are illustrative rather than exhaustive.

Do not route a game-industry question to `general` merely because the material legal issue falls outside the repository's predefined game-regulation categories or specialist skills.

Use `game_plus_general` only when the matter contains both:

- a material game-industry component requiring game-specific legal or regulatory analysis; and
- a distinct legal workstream that is substantially independent of the game product or game-business context and is better handled through the general research workflow.

The existence of tax, employment, corporate, intellectual-property, contract, competition, finance, or other general legal issues does not by itself require `game_plus_general` if those issues arise directly from the development, launch, operation, distribution, monetization, or commercial exploitation of the game.

Use `general` when the question is not materially game-industry framed and no narrower game-regulation analysis is required.

Use `fallback` when the relevant facts, jurisdiction, or subject matter are too unclear to classify reliably, source coverage is materially insufficient, or the matter falls outside the agent's competence and no better route is available.

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
