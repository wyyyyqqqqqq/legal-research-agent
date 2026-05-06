# Prompt Footprint

This document records the Phase 0 core instruction footprint diagnostic for
`legal-research-agent`.

The metric is a stable local proxy:

```text
rough_tokens = ceil(characters / 4)
```

It is useful for detecting prompt bloat inside this repo. It is not a substitute
for actual Claude Code usage from `events.jsonl`.

## Current Snapshot

Measured on 2026-05-06 KST with:

```bash
python3 scripts/measure-prompt-footprint.py
python3 scripts/measure-prompt-footprint.py --include-vendor
```

Core profile:

| Category | Rough tokens | Files |
|---|---:|---:|
| agent_prompt | 1,537 | 1 |
| knowledge | 8,609 | 9 |
| skills | 13,790 | 16 |
| templates | 512 | 2 |
| total | 24,448 | 28 |

Core plus vendored Claude skills:

| Category | Rough tokens | Files |
|---|---:|---:|
| agent_prompt | 1,537 | 1 |
| knowledge | 8,609 | 9 |
| skills | 13,790 | 16 |
| templates | 512 | 2 |
| vendor_claude | 16,031 | 11 |
| total | 40,479 | 39 |

## Interpretation

- Use the core profile for normal agent instruction-footprint tracking.
- Use the vendor-inclusive profile when evaluating optional citation-auditor
  skill loading impact.
- Do not treat lower prompt footprint as success unless legal-quality gates also
  pass.
