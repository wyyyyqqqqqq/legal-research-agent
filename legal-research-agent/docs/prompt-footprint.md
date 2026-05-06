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
| agent_prompt | 1,422 | 1 |
| knowledge | 4,981 | 5 |
| skills | 11,167 | 15 |
| templates | 512 | 2 |
| total | 18,082 | 23 |

Core plus vendored Claude skills:

| Category | Rough tokens | Files |
|---|---:|---:|
| agent_prompt | 1,422 | 1 |
| knowledge | 4,981 | 5 |
| skills | 11,167 | 15 |
| templates | 512 | 2 |
| vendor_claude | 16,031 | 11 |
| total | 34,113 | 34 |

## Interpretation

- Use the core profile for normal agent instruction-footprint tracking.
- Use the vendor-inclusive profile when evaluating optional citation-auditor
  skill loading impact.
- Do not treat lower prompt footprint as success unless legal-quality gates also
  pass.
