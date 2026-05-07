# Knowledge Construction Recipe

## Status and Audience

Canonical recipe for building `knowledge/<industry>-<area>/`
directories. The same recipe is followed by:

- the `/onboard --build-knowledge` wizard execution
  (`skills/onboarding.md`); and
- human contributors writing knowledge by hand.

Generated and hand-built directories are interchangeable as long as
they conform to this recipe and pass
`scripts/check-generated-knowledge.py`.

## Required Files

Every `knowledge/<industry>-<area>/` directory must contain four
Markdown files plus one JSON gate file:

- `issue-taxonomy.md`
- `regulatory-map.md`
- `source-map.md`
- `library-index.md`
- `review-status.json`

Missing any of these makes the directory invalid.

## Per-File Structure

### `issue-taxonomy.md`

- Banner block on line 1 (see [Verification Metadata](#verification-metadata)).
- YAML frontmatter with the six required fields.
- `## Issue Categories` section with **at least 5 categories** specific
  to the industry-area pair.
- For each category: scope sentence, key sub-issues, applicable
  `output_mode` default, and at least one source URL backing the
  category's existence (or `[Unverified]` when no source can be cited).

### `regulatory-map.md`

- Banner block + frontmatter.
- `## Regulators` section listing each regulator with:
  - Name (verbatim from the official source).
  - Official URL.
  - Jurisdiction.
  - Scope of authority (one sentence from the official source).
  - Source URL backing the entry.
- `## Statutes and Rules` section listing **3-7 controlling statutes**
  and **3-7 delegated rules** with:
  - Citation (statute or rule number and section, verbatim).
  - Effective date in `YYYY-MM-DD` when verifiable, otherwise
    `[Effective date unverified]`.
  - Source URL.

### `source-map.md`

- Banner block + frontmatter.
- `## Primary Sources` section listing official portals, statute
  databases, and case databases for the jurisdiction-area pair. Each
  entry: name, URL, Grade `A`, scope note.
- `## Secondary Sources` section listing **at least 3** trusted
  practitioner publications, regulator press release feeds, or
  academic journals. Each entry: name, URL, Grade `B`, scope note.
- Every source has a Grade (A, B, C, or D per the project's source
  grading vocabulary in `skills/source-grading.md`).

### `library-index.md`

- Banner block + frontmatter.
- `## Index` section. An empty list is acceptable when no library
  files have been ingested yet.

### `review-status.json`

Tracks the gate state and audit summary:

```json
{
  "industry": "fintech",
  "area_of_law": "regulatory",
  "jurisdiction": "KR",
  "review_status": "draft",
  "source_audit_status": "live_passed",
  "audit_summary": {
    "total_facts": 42,
    "verified_facts": 39,
    "unverified_facts": 3
  },
  "created_at": "2026-05-08",
  "lifted_at": null,
  "recipe_version": "1.0"
}
```

`review_status` is one of:

- `draft` — directory was just generated; gate not lifted.
- `verified` — user reviewed and lifted the gate via
  `/review-knowledge`.

`source_audit_status` is one of the citation-audit manifest values:

- `not_required`
- `not_run_session_unavailable`
- `deterministic_smoke`
- `live_passed`
- `live_failed`

## Verification Metadata

### Banner block

The first line of every generated `.md` file is a banner that the
agent's source-collection skill recognizes as a draft gate:

```text
> **[GENERATED — REQUIRES HUMAN REVIEW]** This file was built by the
> /onboard wizard from live research. Lift the gate with
> `/review-knowledge knowledge/<industry>-<area>/` after editing.
```

When the user lifts the gate via `/review-knowledge`, the banner is
replaced with:

```text
> **[VERIFIED]** Reviewed on YYYY-MM-DD by the user.
```

### YAML frontmatter

Every `.md` file in a generated directory carries this frontmatter:

```yaml
---
industry: fintech
area_of_law: regulatory
jurisdiction: KR
recipe_version: "1.0"
generated_at: 2026-05-08
verification_status: draft
sources:
  - url: https://example.gov/regulator/about
    grade: A
    accessed_at: 2026-05-08
---
```

Required frontmatter fields (validator-enforced):

- `industry`
- `area_of_law`
- `jurisdiction`
- `recipe_version`
- `generated_at`
- `verification_status`

The `sources` array lists every URL the agent (or human) fetched
while building this file. Each fact in the body must reference at
least one entry from this array via inline citation, otherwise the
fact must be marked `[Unverified]`.

## Live-Research Protocol

Per file, in this run order:

1. **`source-map.md` first.** Enumerate official portals for the
   jurisdiction-area pair. This builds the source registry that
   subsequent files draw from.
   - For `jurisdiction: KR`, prefer
     `mcp__claude_ai_Korean-law__search_law` and
     `mcp__claude_ai_Korean-law__chain_full_research` over
     `WebFetch`. Korean-law MCP returns structured statute lookups
     with stable IDs.
   - For other jurisdictions, use `WebFetch` against whitelisted
     official portals: `eur-lex.europa.eu` (EU), `congress.gov` and
     `ecfr.gov` (US), `legislation.gov.uk` (UK), `laws.e-gov.go.jp`
     (JP), `legifrance.gouv.fr` (FR), `gesetze-im-internet.de` (DE),
     `boe.es` (ES), `gazzettaufficiale.it` (IT), `flk.npc.gov.cn`
     (CN), `sso.agc.gov.sg` (SG), `legislation.gov.au` (AU),
     `laws-lois.justice.gc.ca` (CA), `planalto.gov.br` (BR).
   - For each official portal: fetch the home page, extract the
     directory of statutes / regulations / guidance, save the URL to
     `## Primary Sources` with Grade A.
   - For secondary sources: enumerate at least three trusted
     practitioner publications (law-firm newsletters, academic
     journals, regulator press release feeds). Grade B.
2. **`regulatory-map.md`.** Using the `## Primary Sources` from
   `source-map.md`, fetch the official regulator page(s) and extract:
   - Regulator name (verbatim).
   - Scope of authority (one sentence from the official source).
   - Top 3-7 controlling statutes for the area.
   - Top 3-7 delegated rules.
   Each fact records the source URL it came from.
3. **`issue-taxonomy.md`.** Using both prior files, enumerate at
   least 5 issue categories specific to the industry-area pair.
   Examples: for `fintech-regulatory` in KR, categories like "Virtual
   asset custody", "Lending platform licensing", "AML/KYC compliance",
   "Consumer credit consumer protection", "Algorithmic trading
   oversight". For each category, identify:
   - Scope (one paragraph).
   - Key sub-issues (bullet list).
   - Default `output_mode` (e.g., `executive_brief` for compliance
     overviews, `comparative_matrix` for cross-jurisdiction work).
   - At least one source URL backing the category's existence.
4. **`library-index.md`.** Empty `## Index` is acceptable.
5. **`review-status.json`.** After all four `.md` files are
   generated, write `review-status.json` with:
   - `review_status: "draft"`.
   - `audit_summary` populated from the citation-auditor run (next
     step).
   - `source_audit_status` set after the citation-auditor runs.

## Hallucination Mitigation Rules

Mandatory rules for both human contributors and the wizard:

- **Every fact is sourced.** Regulator names, statute numbers,
  effective dates, and scope statements always cite a source URL via
  inline reference (e.g., `[src_001]`) or surrounding link. Any fact
  without a source is marked `[Unverified]` inline.
- **Cite verbatim.** Regulator names and statute citations come
  verbatim from the source. No paraphrasing the regulator's name
  ("FSC" vs "Financial Services Commission" — the official source
  decides which to use).
- **Date format.** Effective dates use ISO `YYYY-MM-DD` and only
  when the source explicitly states the date; otherwise
  `[Effective date unverified]`.
- **No primary-law text generation.** This recipe builds metadata
  about regulators, statutes, and source URLs. It does not write
  out statute text. For statute text, the agent fetches the source
  live during research runs (not during generation).
- **Citation audit before review.** After all files are generated,
  the wizard runs the vendored `citation-auditor` over the directory.
  The audit's per-claim verdicts populate `audit_summary` in
  `review-status.json`.
- **Banner gate.** Every `.md` file always starts with the banner;
  the gate is lifted only by `/review-knowledge`.
- **Audit failure handling.** If the citation auditor reports
  `live_failed`, the wizard surfaces the audit findings to the user
  and asks whether to keep the draft directory or roll back. The
  wizard never silently writes a directory whose audit failed.

## Run Order

```
source-map.md
  → regulatory-map.md
    → issue-taxonomy.md
      → library-index.md
        → citation audit
          → review-status.json
```

The wizard runs the citation auditor before writing the final
`review-status.json` so the audit summary is recorded accurately.

## Recipe Version

Current version: `1.0`.

Version is recorded in each generated file's frontmatter and in
`review-status.json` so future recipe upgrades can identify and
migrate older generated directories. Recipe version bumps follow
SemVer:

- Patch (1.0 → 1.0.1): clarifications, no schema change.
- Minor (1.0 → 1.1): additive new optional fields or sections.
- Major (1.0 → 2.0): breaking changes; previous generated dirs need
  migration.

## Human Contributor Path

Humans building a knowledge directory by hand should follow exactly
the same recipe. The only differences from wizard execution:

- The banner block on line 1 may be the `[VERIFIED]` form from the
  start (skipping the draft gate), as long as the contributor has
  reviewed every fact.
- `review-status.json` may set `review_status: "verified"` and
  `source_audit_status: "live_passed"` immediately, but the
  contributor must still run the citation auditor and record the
  result.
- Hand-built directories should still be validated by
  `python3 scripts/check-generated-knowledge.py --dir
  knowledge/<industry>-<area>` before being relied on.

This single recipe is the source of truth — wizard and human paths
must not diverge.
