# Legacy Parity Audit — Track B (Skill / Knowledge Mapping)

| | |
|---|---|
| **Date** | 2026-05-08 |
| **Scope** | Skill and knowledge inventory of `legal-research-agent` against legacy `general-legal-research` and `game-legal-research` repos |
| **Result** | Track B passes — no regressions detected |
| **Decision** | Conditionally on track for unified-replacement; runtime parity (Phase 2 + 3) is the remaining gate |

## Purpose

Establish whether `legal-research-agent` preserves every capability provided by the two legacy repos at the **rule-set level** (skills, knowledge, references, templates), as the first gate of the unified-parity audit. A static rule-set comparison is necessary but not sufficient — the runtime parity tests in Phase 2 (general) and Phase 3 (game) decide the final replacement question.

## Scope

- **Legacy general**: `../general-legal-research/.claude/skills/` (28 skills) + `../general-legal-research/knowledge/` + 13 per-skill `references/` files.
- **Legacy game**: `../game-legal-research/.claude/skills/` (28 skills, identical to general core) + `../game-legal-research/library/` (gitignored user materials).
- **Merged target**: `legal-research-agent/skills/` (34 files: 22 top-level + 12 specialists) + `knowledge/` + `references/` + `templates/` + `legal_sources.yaml`.

## Findings

### 1. The two legacy repos share a single 28-skill core

`general-legal-research` and `game-legal-research` ship an **identical** 28-skill set under `.claude/skills/`. Game-specific behavior (loot box, GRAC, Game Industry Promotion Act) lives in legacy in `library/` user materials and per-skill `references/`, not in distinct skill files. The audit therefore collapses from "compare against two repos" to "compare against one shared skill set", with the game-specific content dimension handled in knowledge mapping.

### 2. No accidental skill or knowledge drops

All 28 legacy skills and 13 reference files are accounted for with explicit status:

| Status | Skills | References |
|---|---|---|
| `preserved` (12 specialists, 1-to-1 relocated under `skills/specialists/`) | 12 | — |
| `renamed` / relocated | 7 | 5 |
| `split-into` (finer-grained merged skills) | 4 | — |
| `merged-into` (folded into another file) | 2 | 6 |
| `upgraded` (markdown → structured registry) | 1 | 1 |
| `dropped (accepted scope reduction)` | 2 | 2 |
| **`dropped (accidental — IMPORT)`** | **0** | **0** |
| `unmapped` | 0 | 0 |

The 4 `split-into` decompositions are intentional architectural improvements:

- `fact-checker` → `claim-spot-check` + `claim-verification-loop`
- `jurisdiction-mapper` → `jurisdiction-source-playbook` + `general-law-source-playbook`
- `legal-research` → `general-research` + `game-regulation-research`
- `output-generator` → `output-contract` + `result-memo-composition` + `output-mode-composition`

### 3. Two intentional scope reductions

`client-memo` and `compliance-summaries` are deliverable-shaping skills that produce client-facing memoranda and compliance posture reports. These belong to a downstream **legal-writing agent**, not to legal-research. The boundary is already documented in `docs/migration-notes.md`:

> ## First Rollout Scope
>
> The first rollout replaces only the two legacy research roles above. It does not consolidate data-protection specialists or change writing/review agents.

No additional documentation is required.

### 4. Architectural improvements over legacy baseline

The merged repo restructures legacy's per-skill `references/` siloes into shared, reusable directories:

- `knowledge/<area>/` — cross-skill orientation by domain (game-regulation, general, legal-writing, output-modes, onboarding).
- `references/` — top-level reference corpus + per-specialist `packs/`.
- `templates/` — output-mode templates and example schemas.
- `legal_sources.yaml` — structured jurisdiction-source registry replacing legacy `web-researcher/references/legal-source-urls.md` markdown URL list (validated by `scripts/check-legal-sources.py`).

### 5. Capability expansion beyond the legacy baseline

The merged repo adds **7 net-new skills** (no legacy counterpart):

`citation-hierarchy`, `currentness-check`, `game-library`, `general-law-source-playbook`, `legal-output-quality-standard`, `output-mode-composition`, `trust-boundary`.

And **~22 net-new knowledge / reference / template files**, including the entire `knowledge/game-regulation/` (4 files), `knowledge/output-modes/` (3 files), `knowledge/legal-writing/` (5 profiles), `references/packs/` (6 specialist packs), and per-mode templates under `templates/output-modes/` (4 templates).

## Decision

**Track B passes.** At the rule-set / capability level, `legal-research-agent` preserves every legacy capability and adds substantial improvements. The audit detected zero accidental drops; both intentional scope reductions are pre-documented; all legacy specialist skills are 1-to-1 preserved.

The decision to use `legal-research-agent` as the unified replacement for `general-legal-research` and `game-legal-research` is **conditionally on track**:

- ✓ Static rule-set parity (Track B) — confirmed in this audit.
- ⏳ Runtime general parity (Phase 2 of `unified-parity-audit-plan`) — pending.
- ⏳ Runtime game parity (Phase 3) — pending.

Until Phase 2 and Phase 3 produce decision records (`docs/general-legacy-parity-decision.md`, `docs/game-legacy-parity-decision.md`), the legacy routing default in `legal-agent-orchestrator` remains authoritative for both routes.

## Reproducibility

The full audit artifacts are preserved locally under `.agent-work/audit/` (gitignored — local audit data, not committed):

```
.agent-work/audit/
├── inventories-2026-05/
│   ├── general-legacy.txt              # 28 skills
│   ├── game-legacy.txt                 # 28 skills
│   └── legal-research-agent.txt        # 34 skill files
├── skill-mapping-2026-05.md            # 28 legacy → merged status table
├── knowledge-mapping-2026-05.md        # 13 references + 4 user-material groups
├── import-tasks-2026-05.md             # 0 imports needed
└── phase1-summary-and-handoff-2026-05.md
```

Anyone re-running the audit can regenerate the inventories with the bash commands documented in `.agent-work/plans/unified-parity-audit-plan.md` § 4.1, and verify mapping completeness by checking that no row carries the `unmapped` status.

## Reference

- `docs/migration-notes.md` — design intent and legacy-to-merged role mapping.
- `docs/general-legacy-parity-plan.md` — runtime parity test plan for general routes (Phase 2).
- `.agent-work/plans/unified-parity-audit-plan.md` — overarching plan with Phase 1 (this document) + Phase 2 + Phase 3 + Phase 4.
