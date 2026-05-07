# Output Modes and User-Facing Docs Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development` (if
> subagents are available) or `superpowers:executing-plans` to implement this
> plan. Steps use checkbox (`- [ ]`) syntax so progress can be tracked in the
> file itself.

**Goal:** Bring `legal-research-agent` to deliverable-shape and user-doc parity
with `general-legal-research`. Add four output modes (Executive Brief /
Comparative Matrix / Enforcement & Case Law / Black-letter Commentary)
backed by templates, frameworks, and validators, plus a parity user-doc
set (how-to-use, disclaimer, MCP setup, citation audit canonical spec,
release process), in both English and Korean.

**Approach:** Output modes are an additive metadata field plus a new
composition skill that renders mode-shaped deliverables on top of the
existing standalone formatter. The orchestrator-compatible `result.md`
keeps its current 9-section structure unchanged. Existing skills,
contracts, scripts, and tests remain untouched except for additive
extension points.

**Tech Stack:** Python 3.11+, YAML frontmatter, Markdown, Mermaid,
existing `marko`/`pydantic`/`python-docx` runtime.

## Out of scope

- Editing any existing skill body except `skills/legal-writing-formatter.md`
  (which is the natural integration surface for output modes).
- Editing the orchestrator-compatible `result.md` structure or the legacy
  metadata fields.
- Editing `legal-agent-orchestrator`.
- Adding mode-specific Python rendering logic beyond Markdown (DOCX
  rendering reuses the existing `scripts/render-docx.py`).
- Translating skill bodies, knowledge files, or Python script docstrings
  into Korean. Translation is limited to the user-facing docs under
  `docs/en/` and `docs/ko/`.
- Replacing the existing 3 formatter packaging modes (`standalone_markdown`
  / `handoff_packet` / `docx_ready_markdown`). They stay as is. Output
  modes are an orthogonal axis.

## Background

`general-legal-research` exposes four deliverable shapes (Mode A/B/C/D)
plus a parity user-doc set (how-to-use / disclaimer / MCP setup guide /
citation audit canonical spec / release process). `legal-research-agent`
currently has neither: every research output uses a single 9-section
memo structure, and user-facing docs are limited to README plus
`docs/standalone-workflow.md`.

The 9-section memo is the right canonical research record (orchestrator
contract preservation), but it is not the right shape for an executive
asking for a 1-page brief, for a multi-jurisdiction comparison, for a
litigation-focused enforcement timeline, or for a deep article-by-article
black-letter commentary. Today the user gets the same shape regardless of
intent.

The merge story in `README.md` already commits to "same legal-quality
floor, smaller token footprint, single dispatch path." Adding mode-shaped
deliverables on top of that is the next quality bar — the agent should
produce the *kind* of document the user actually asked for.

## Architecture

### Two orthogonal axes

```
                 ┌────────────────────────────────────────────┐
                 │  Standalone formatter packaging mode       │
                 │  (existing — unchanged)                    │
                 │                                            │
                 │  standalone_markdown / handoff_packet /    │
                 │  docx_ready_markdown                       │
                 └────────────────────────────────────────────┘
                                       ×
                 ┌────────────────────────────────────────────┐
                 │  Output mode (NEW — deliverable shape)     │
                 │                                            │
                 │  executive_brief / comparative_matrix /    │
                 │  enforcement_case_law /                    │
                 │  black_letter_commentary / canonical       │
                 └────────────────────────────────────────────┘
```

The orchestrator-compatible `result.md` stays in `canonical` shape (the
current 9-section structure) regardless of `output_mode`. The standalone
formatter consults `output_mode` to render a *separate* mode-shaped
deliverable file under `deliverables/`.

A given run can produce zero deliverables (orchestrator-only), or one,
or several. Each deliverable picks one packaging mode and one output
mode. Default when `output_mode` is unset: `canonical`, which renders
the existing 9-section memo as the standalone deliverable.

### File Structure (after plan)

```
legal-research-agent/
  CLAUDE.md                                    # MODIFY: add output-mode workflow note
  README.md                                    # MODIFY: replace Standalone Deliverables with Output Modes section
  README.ko.md                                 # MODIFY: mirror
  LICENSE                                      # CREATE: project license (TBD with user)
  .claude/
    commands/
      research.md                              # MODIFY: argument hint includes output mode
  knowledge/
    output-modes/                              # CREATE
      comparative-framework.md                 # CREATE: Mode B 10 axes + extended axes
      counter-analysis-checklist.md            # CREATE: per-mode counter-analysis discipline
      mode-index.md                            # CREATE: maps slug → template + framework + audience
  templates/
    output-modes/                              # CREATE
      executive-brief.md                       # CREATE: Mode A template
      comparative-matrix.md                    # CREATE: Mode B template
      enforcement-case-law.md                  # CREATE: Mode C template
      black-letter-commentary.md               # CREATE: Mode D template
  skills/
    output-mode-composition.md                 # CREATE: composition workflow + template selection
    legal-writing-formatter.md                 # MODIFY: dispatch to output-mode-composition when output_mode is set
    output-contract.md                         # MODIFY: add optional output_mode field documentation
  scripts/
    check-output-modes.py                      # CREATE: template structure + framework integrity validator
    check-formatter-output.py                  # MODIFY: mode-aware structure check
    run-local-checks.py                        # MODIFY: register output_modes check
    check-knowledge-coverage.py                # MODIFY: enforce required markers in new docs
  tests/
    fixtures/
      output-modes/                            # CREATE
        executive-brief/                       # CREATE: meta.json + result.md + deliverable.md
        comparative-matrix/
        enforcement-case-law/
        black-letter-commentary/
    test_output_modes.py                       # CREATE: validates fixture round-trip + template integrity
  templates/
    meta.example.json                          # MODIFY: add optional output_mode key
  docs/
    output-modes-and-docs-plan.md              # THIS FILE
    citation-audit.md                          # CREATE: canonical citation audit spec
    release-process.md                         # CREATE: release preflight workflow
    en/                                        # CREATE
      README.md                                # CREATE: bridge to root README.md
      how-to-use.md                            # CREATE
      disclaimer.md                            # CREATE
      mcp-setup-guide.md                       # CREATE
    ko/                                        # CREATE
      README.md                                # CREATE: bridge to root README.ko.md
      how-to-use.md                            # CREATE
      disclaimer.md                            # CREATE
      mcp-setup-guide.md                       # CREATE
```

### Mode catalog

| Slug (snake_case) | User-facing label | Best for | Default packaging |
|:---|:---|:---|:---|
| `executive_brief` | Executive Brief (Mode A) | Quick overview for decision-makers | `standalone_markdown` |
| `comparative_matrix` | Comparative Matrix (Mode B) | Multi-jurisdiction side-by-side | `standalone_markdown` |
| `enforcement_case_law` | Enforcement & Case Law (Mode C) | Litigation strategy and precedent | `standalone_markdown` |
| `black_letter_commentary` | Black-letter & Commentary (Mode D) | Article-by-article statute deep dive | `docx_ready_markdown` |
| `canonical` *(default)* | Canonical research memo | Orchestrator-compatible record | `standalone_markdown` |

`canonical` is reserved for the existing 9-section structure. It is
implicitly active when `output_mode` is unset or null. The four named
modes mirror `general-legal-research`'s Mode A/B/C/D catalog with
descriptive snake_case slugs that match our metadata vocabulary.

### Metadata addition (additive; backward-compatible)

```json
{
  "output_mode": "executive_brief",
  "output_mode_audience": "C-suite",
  "output_mode_format": "markdown"
}
```

All three keys are optional. Existing readers ignore them. New
validators consume them only when present. The `output_contract.md`
skill documents the vocabulary.

### Counter-analysis and comparative frameworks

Both frameworks are reference content (not instruction surface), so
they live under `knowledge/output-modes/`:

- `counter-analysis-checklist.md`: six counter-analysis dimensions
  (alternative interpretation, minority view, jurisdictional risk,
  factual sensitivity, practical enforcement risk, similar-statute
  confusion). Per-mode minimum thresholds.
- `comparative-framework.md`: ten standard comparison axes for Mode B
  plus six optional extended axes.

The new `skills/output-mode-composition.md` references both. The
existing `skills/analysis-issue-structuring.md` is unchanged; the
counter-analysis checklist is invoked specifically when an output mode
is selected.

## Chunk 1: Output mode foundation (templates, frameworks, composition skill)

### Task 1: Add the comparative framework reference

**Files:**

- Create: `knowledge/output-modes/comparative-framework.md`

- [ ] **Step 1: Write the framework**

```markdown
# Comparative Framework (Mode B)

Used by `output_mode = comparative_matrix` deliverables. Every Mode B
deliverable must compare jurisdictions along the ten standard axes.
Inapplicable axes are marked `N/A`, not omitted.

## Standard Axes

| # | Axis | Description |
|---|------|-------------|
| 1 | Regulatory Scope | What conduct, entities, or transactions does the law cover? |
| 2 | Obligated Parties | Who bears the compliance obligation? |
| 3 | Key Obligations | Core duties imposed by the law |
| 4 | Exemptions and Safe Harbors | Carve-outs, thresholds, or de minimis rules |
| 5 | Sanctions and Penalties | Maximum penalties, penalty types, enforcement track record |
| 6 | Competent Authority | Regulator(s) with enforcement power |
| 7 | Effective Date and Transition | When the law took effect; transitional periods |
| 8 | Extraterritorial Reach | Does the law apply to foreign entities, and under what conditions? |
| 9 | Cross-Border Mechanisms | Transfer requirements, mutual recognition, adequacy |
| 10 | Pending Reforms | Active legislative proposals, regulatory guidance in progress |

## Optional Extended Axes

Add these only when the query requires them.

| Axis | When to add |
|------|-------------|
| Licensing or Registration | Market entry, regulated industries |
| Consumer Protection | B2C, platform, e-commerce queries |
| Local Representation | Foreign entity operating locally |
| Record-Keeping or Reporting | Compliance program design |
| Private Right of Action | Litigation risk assessment |
| Industry Self-Regulation | Where industry codes supplement legislation |

## Divergence Commentary Rules

After the matrix, every Mode B deliverable must include a
`## Divergence Commentary` section that:

1. Highlights material differences with practical impact.
2. Identifies the strictest standard per axis.
3. Notes convergence trends.
4. Flags pending reforms that could change the analysis.

## Practical Implications (Mandatory)

Every Mode B deliverable ends with a `## Practical Implications` section
covering Compliance Strategy, Risk Hotspots, and Monitoring Points. See
`templates/output-modes/comparative-matrix.md` for the structural anchor.
```

- [ ] **Step 2: Commit**

```bash
git add knowledge/output-modes/comparative-framework.md
git commit -m "Add comparative framework for Mode B output"
```

### Task 2: Add the counter-analysis checklist

**Files:**

- Create: `knowledge/output-modes/counter-analysis-checklist.md`

- [ ] **Step 1: Write the checklist**

```markdown
# Counter-Analysis Checklist

Every key conclusion in a mode-shaped deliverable must be tested against
at least one of the six counter-analysis dimensions before publication.

## Dimensions

### 1. Alternative Interpretation
- Is there a plausible alternative reading of the statute or regulation?
- Has any court, regulator, or commentary adopted a different reading?
- Could the provision be read more narrowly or more broadly?

### 2. Minority or Dissenting View
- Are there dissenting opinions in relevant case law?
- Does any credible secondary source argue the opposite position?
- Has any regulator taken a different stance from the majority view?

### 3. Jurisdictional Risk
- Would the conclusion hold if a different court or regulator reviewed it?
- Are pending amendments or guidance likely to change the outcome?
- Is there a split between lower and higher courts, or between agencies?

### 4. Factual Sensitivity
- Would the conclusion change if key facts were slightly different?
- What threshold conditions (monetary, temporal, scope) could shift the analysis?

### 5. Practical Enforcement Risk
- Is the provision actively enforced or largely dormant?
- What is the realistic enforcement probability?
- Are there safe harbors or compliance program mitigants?

### 6. Similar-Statute Confusion
- Are there two or more statutes in the same jurisdiction covering the same subject?
- Could operative language, safe harbors, or definitions be confused across statutes?
- Do the statutes share adjacent code sections or near-identical names?
- High-risk pattern: shared code-section ranges (e.g., Cal. Civ. Code §§1798.80-1798.84,
  Korean PIPA vs. Credit Information Act). Subsection-level citation verification required.

## Per-Mode Minimums

| Output mode | Minimum counter-analysis |
|---|---|
| `executive_brief` | At least 1 counter-argument per key conclusion (brief). |
| `comparative_matrix` | At least 1 counter-argument per material divergence point. |
| `enforcement_case_law` | At least 1 dissenting or minority view per enforcement trend. |
| `black_letter_commentary` | At least 1 counter-argument per article-level conclusion (detailed). |
| `canonical` | Same as `black_letter_commentary` — preserves the agent's existing analysis discipline. |

## Output Format

For each key conclusion, append a structured counter-analysis block:

```text
**Counter-Analysis:**
- **Alternative interpretation:** <description> — <source if available>
- **Risk level:** High / Medium / Low
- **Mitigant:** <what reduces this risk, if anything>
```

When a counter-analysis dimension is rated **High**, flag it inline with
`[Material Risk]`, surface it in the Conclusion Summary or Executive
Summary, and (for `black_letter_commentary`) add a dedicated Risk
Considerations paragraph under the affected article.
```

- [ ] **Step 2: Commit**

```bash
git add knowledge/output-modes/counter-analysis-checklist.md
git commit -m "Add counter-analysis checklist for output modes"
```

### Task 3: Add the four mode templates

**Files:**

- Create: `templates/output-modes/executive-brief.md`
- Create: `templates/output-modes/comparative-matrix.md`
- Create: `templates/output-modes/enforcement-case-law.md`
- Create: `templates/output-modes/black-letter-commentary.md`

Each template is a Markdown skeleton with mandatory section headings
that the validator (Task 6) checks for. Use the structures below
verbatim — they encode the per-mode contract.

- [ ] **Step 1: Executive brief template**

`templates/output-modes/executive-brief.md`:

```markdown
<!--
Output mode: executive_brief
Audience: decision-makers, executives
Length target: 1-2 pages
-->

# {Title}

## Scope and As-of Date
- Jurisdictions:
- As-of date:
- Assumptions:
- Exclusions:

## Key Conclusions
1. {Finding} [src_001]

## Counter-Analysis and Risk Assessment
Per `knowledge/output-modes/counter-analysis-checklist.md`. At least one
counter-argument per key conclusion (brief).

## Risk and Priority Ranking
- High:
- Medium:
- Low:

## Practical Implications
- What the findings mean for the decision
- Recommended next steps

## Immediate Action Checklist
- [ ] {Action item}

## Top Sources
- [src_001] {Title} — {Citation} — {Pinpoint} — {Access}

## Verification Guide
| Finding | Source | Pinpoint | Verification URL |
|---|---|---|---|
| | [src_001] | | |
```

- [ ] **Step 2: Comparative matrix template**

`templates/output-modes/comparative-matrix.md`:

```markdown
<!--
Output mode: comparative_matrix
Audience: multi-jurisdiction decision support
Required framework: knowledge/output-modes/comparative-framework.md
-->

# {Title}

## Scope and As-of Date
- Jurisdictions:
- As-of date:
- Assumptions:
- Exclusions:

## Comparative Matrix

Use the ten standard axes from
`knowledge/output-modes/comparative-framework.md`. Mark inapplicable
axes `N/A`.

| Axis | {Jurisdiction A} | {Jurisdiction B} | Divergence Note |
|------|------------------|------------------|-----------------|
| Regulatory Scope | | | |
| Obligated Parties | | | |
| Key Obligations | | | |
| Exemptions and Safe Harbors | | | |
| Sanctions and Penalties | | | |
| Competent Authority | | | |
| Effective Date and Transition | | | |
| Extraterritorial Reach | | | |
| Cross-Border Mechanisms | | | |
| Pending Reforms | | | |

## Divergence Commentary
- Material differences with practical impact
- Strictest standard per axis
- Convergence trends

## Counter-Analysis
Per `knowledge/output-modes/counter-analysis-checklist.md`. At least one
counter-argument per material divergence point.

## Practical Implications
### Compliance Strategy
- Baseline jurisdiction and rationale
- Key multi-jurisdiction actions

### Risk Hotspots
- Highest compliance risk areas
- Active enforcement areas

### Monitoring Points
- Pending reforms
- Expected regulatory guidance

## Annotated Bibliography
- Primary:
- Secondary:

## Verification Guide
- Finding -> Pinpoint
```

- [ ] **Step 3: Enforcement and case-law template**

`templates/output-modes/enforcement-case-law.md`:

```markdown
<!--
Output mode: enforcement_case_law
Audience: litigation and enforcement strategy
-->

# {Title}

## Scope and As-of Date
- Jurisdictions:
- As-of date:
- Assumptions:
- Exclusions:

## Conclusion Summary
- {Finding} [src_001]

## Enforcement Timeline
| Date | Authority | Action | Legal Basis | Source |
|------|-----------|--------|-------------|--------|
| | | | | [src_001] |

## Case and Decision Summaries
- Case name:
- Holding:
- Practical implication:
- Pinpoint:

## Counter-Analysis
Per `knowledge/output-modes/counter-analysis-checklist.md`. At least one
dissenting or minority view per enforcement trend.

## Practical Implications
- Enforcement landscape impact
- Compliance risk areas and recommended actions
- Monitoring points

## Annotated Bibliography
- Primary:
- Secondary:

## Verification Guide
- Finding -> paragraph or page or article
```

- [ ] **Step 4: Black-letter commentary template**

`templates/output-modes/black-letter-commentary.md`:

```markdown
<!--
Output mode: black_letter_commentary
Audience: detailed statute or regulation deep dive
Default packaging: docx_ready_markdown
-->

# {Title}

## Scope and As-of Date
- Jurisdictions:
- As-of date:
- Assumptions:
- Exclusions:

## Legal System Overview
- Hierarchy:
- Authorities:

## Core Definitions and Scope
- {Definition}

## Article-by-Article Commentary

| Provision | Requirement | Exception | Procedure | Source |
|-----------|-------------|-----------|-----------|--------|
| | | | | [src_001] |

For each article-level conclusion, include a Counter-Analysis subsection
per `knowledge/output-modes/counter-analysis-checklist.md` (at least one
alternative interpretation, with similar-statute confusion verification
where applicable).

## Implementation Relationships
- Parent statute -> implementing rule map

## Practical Implications
- Operational impact
- Key compliance actions
- Risk areas and mitigants

## Annotated Bibliography
- Primary:
- Secondary:

## Verification Guide
- Finding -> pinpoint map
```

- [ ] **Step 5: Commit all four templates**

```bash
git add templates/output-modes/
git commit -m "Add four output-mode deliverable templates"
```

### Task 4: Add the mode index

**Files:**

- Create: `knowledge/output-modes/mode-index.md`

The index lets the composition skill resolve `output_mode` slug → template
path → framework dependencies in one place.

- [ ] **Step 1: Write the index**

```markdown
# Output Mode Index

Maps each `output_mode` slug to its template, framework dependencies,
default packaging mode, and audience profile.

| Slug | Label | Template | Required Frameworks | Default Packaging | Audience |
|---|---|---|---|---|---|
| `executive_brief` | Executive Brief (Mode A) | `templates/output-modes/executive-brief.md` | counter-analysis | `standalone_markdown` | Decision-makers, C-suite |
| `comparative_matrix` | Comparative Matrix (Mode B) | `templates/output-modes/comparative-matrix.md` | counter-analysis, comparative-framework | `standalone_markdown` | Multi-jurisdiction compliance |
| `enforcement_case_law` | Enforcement and Case Law (Mode C) | `templates/output-modes/enforcement-case-law.md` | counter-analysis | `standalone_markdown` | Litigation, enforcement strategy |
| `black_letter_commentary` | Black-letter and Commentary (Mode D) | `templates/output-modes/black-letter-commentary.md` | counter-analysis | `docx_ready_markdown` | Statute or regulation deep dive |
| `canonical` | Canonical research memo | `templates/result.md` | (existing skill chain) | `standalone_markdown` | Orchestrator-compatible record |

## Selection Rules

- If the user explicitly names a mode (slug or label), use it.
- If the user requests "executive brief", "summary for executives", or
  similar, select `executive_brief`.
- If the user requests a comparison or asks about more than one
  jurisdiction with comparison framing, select `comparative_matrix`.
- If the user asks about enforcement, litigation, regulator decisions,
  or case law trends, select `enforcement_case_law`.
- If the user asks for an article-by-article analysis, statute deep
  dive, or regulatory commentary, select `black_letter_commentary`.
- Otherwise default to `canonical`.

If the user requests a `.docx` deliverable and does not name a mode,
default to `black_letter_commentary` plus `docx_ready_markdown` packaging.
```

- [ ] **Step 2: Commit**

```bash
git add knowledge/output-modes/mode-index.md
git commit -m "Add output mode index for slug-to-template resolution"
```

### Task 5: Add the composition skill

**Files:**

- Create: `skills/output-mode-composition.md`

This is a new instructional skill the agent applies when an `output_mode`
is selected. It is the bridge between the existing canonical memo and
the new mode-shaped deliverables.

- [ ] **Step 1: Write the skill**

```markdown
---
name: output-mode-composition
description: Use when standalone use selects a non-canonical output_mode — composes a mode-shaped deliverable on top of the canonical research record using the matching template and counter-analysis discipline.
disable-model-invocation: true
---

# Output Mode Composition

Use this skill only when:

- the canonical research record (`legal-research-agent-result.md` and
  `legal-research-agent-meta.json`) is already complete and quality-gated; and
- the user, slash command, or intake payload selects an `output_mode`
  other than `canonical`.

This skill does not change the canonical research record. It composes a
*separate* mode-shaped deliverable file under `deliverables/`.

## Inputs

- The completed canonical research record.
- `output_mode` slug (one of `executive_brief`, `comparative_matrix`,
  `enforcement_case_law`, `black_letter_commentary`).
- Selected packaging mode (`standalone_markdown` / `handoff_packet` /
  `docx_ready_markdown`). Default per
  `knowledge/output-modes/mode-index.md`.
- Output language (`ko` / `en` / `bilingual`).

## Steps

1. Resolve `output_mode` against `knowledge/output-modes/mode-index.md`:
   - load the matching template;
   - identify required frameworks (counter-analysis always;
     comparative framework for `comparative_matrix`).
2. Load the selected language profile from `knowledge/legal-writing/`.
3. Apply `skills/legal-writing-formatter.md` mandatory preservation rules:
   - all material issues from `issue_map`;
   - all `sources[*].id` anchors used by key findings or issue blocks;
   - source grades and pinpoint limits;
   - confidence levels and limiting caveats;
   - `coverage_gaps`, fallback reasons, and errors;
   - privacy or other specialist handoff boundaries;
   - jurisdiction labels and temporal-status caveats.
4. Render the mode-shaped deliverable into the selected template:
   - every section header from the template appears in the deliverable;
   - inapplicable axes (`comparative_matrix`) are explicitly `N/A`,
     not omitted;
   - every cited `src_*` anchor exists in metadata;
   - per-mode counter-analysis minimum is met.
5. Apply `knowledge/output-modes/counter-analysis-checklist.md` discipline
   per the per-mode minimum table.
6. For `comparative_matrix`, apply
   `knowledge/output-modes/comparative-framework.md`:
   - all ten standard axes appear as rows;
   - inapplicable axes are `N/A`;
   - extended axes are added only when the query requires them.
7. Carry the selected `output_mode`, audience, and format into the
   standalone deliverable manifest.
8. Run `scripts/check-formatter-output.py` with `--output-mode <slug>`
   when local execution is available.

## Mode Dispatch Rules

| `output_mode` | Required template sections (validator-enforced) |
|---|---|
| `executive_brief` | Scope and As-of Date; Key Conclusions; Counter-Analysis and Risk Assessment; Risk and Priority Ranking; Practical Implications; Immediate Action Checklist; Top Sources; Verification Guide |
| `comparative_matrix` | Scope and As-of Date; Comparative Matrix; Divergence Commentary; Counter-Analysis; Practical Implications; Annotated Bibliography; Verification Guide |
| `enforcement_case_law` | Scope and As-of Date; Conclusion Summary; Enforcement Timeline; Case and Decision Summaries; Counter-Analysis; Practical Implications; Annotated Bibliography; Verification Guide |
| `black_letter_commentary` | Scope and As-of Date; Legal System Overview; Core Definitions and Scope; Article-by-Article Commentary; Implementation Relationships; Practical Implications; Annotated Bibliography; Verification Guide |

## Quality Floor

- Do not invent legal propositions absent from the canonical research record.
- Do not collapse `coverage_gaps` into soft prose. They appear as
  visible caveats in the deliverable's body, not only in metadata.
- Do not promote a `medium` or `low` confidence finding into a
  client-facing definitive conclusion.
- Do not omit the per-mode minimum counter-analysis.
- Do not promise advanced DOCX features beyond what `scripts/render-docx.py`
  actually provides.

## Manifest Update

When a mode-shaped deliverable is produced, update the standalone
manifest entry per `docs/standalone-workflow.md`:

```json
{
  "mode": "standalone_markdown",
  "language": "en",
  "output_mode": "executive_brief",
  "output_mode_audience": "C-suite",
  "path": "deliverables/20260507_kr-loot-box-probability_standalone_executive-brief_en_v1.md"
}
```

The filename slug `_<output_mode_slug>_` is inserted between the existing
`_<mode>_` and `_<language>_` segments. See
`docs/standalone-workflow.md` for the canonical naming rules.
```

- [ ] **Step 2: Commit**

```bash
git add skills/output-mode-composition.md
git commit -m "Add output-mode composition skill"
```

### Task 6: Add the templates and frameworks validator

**Files:**

- Create: `scripts/check-output-modes.py`

The validator enforces template integrity and framework presence so
future contributors cannot silently break a mode template.

- [ ] **Step 1: Write the script**

```python
#!/usr/bin/env python3
"""Validate output-mode templates and frameworks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_TEMPLATE_SECTIONS: dict[str, list[str]] = {
    "templates/output-modes/executive-brief.md": [
        "## Scope and As-of Date",
        "## Key Conclusions",
        "## Counter-Analysis and Risk Assessment",
        "## Risk and Priority Ranking",
        "## Practical Implications",
        "## Immediate Action Checklist",
        "## Top Sources",
        "## Verification Guide",
    ],
    "templates/output-modes/comparative-matrix.md": [
        "## Scope and As-of Date",
        "## Comparative Matrix",
        "## Divergence Commentary",
        "## Counter-Analysis",
        "## Practical Implications",
        "## Annotated Bibliography",
        "## Verification Guide",
    ],
    "templates/output-modes/enforcement-case-law.md": [
        "## Scope and As-of Date",
        "## Conclusion Summary",
        "## Enforcement Timeline",
        "## Case and Decision Summaries",
        "## Counter-Analysis",
        "## Practical Implications",
        "## Annotated Bibliography",
        "## Verification Guide",
    ],
    "templates/output-modes/black-letter-commentary.md": [
        "## Scope and As-of Date",
        "## Legal System Overview",
        "## Core Definitions and Scope",
        "## Article-by-Article Commentary",
        "## Implementation Relationships",
        "## Practical Implications",
        "## Annotated Bibliography",
        "## Verification Guide",
    ],
}

REQUIRED_FRAMEWORK_MARKERS: dict[str, list[str]] = {
    "knowledge/output-modes/comparative-framework.md": [
        "## Standard Axes",
        "Regulatory Scope",
        "Obligated Parties",
        "Key Obligations",
        "Exemptions and Safe Harbors",
        "Sanctions and Penalties",
        "Competent Authority",
        "Effective Date and Transition",
        "Extraterritorial Reach",
        "Cross-Border Mechanisms",
        "Pending Reforms",
        "## Divergence Commentary Rules",
        "## Practical Implications (Mandatory)",
    ],
    "knowledge/output-modes/counter-analysis-checklist.md": [
        "Alternative Interpretation",
        "Minority or Dissenting View",
        "Jurisdictional Risk",
        "Factual Sensitivity",
        "Practical Enforcement Risk",
        "Similar-Statute Confusion",
        "## Per-Mode Minimums",
        "executive_brief",
        "comparative_matrix",
        "enforcement_case_law",
        "black_letter_commentary",
        "canonical",
    ],
    "knowledge/output-modes/mode-index.md": [
        "executive_brief",
        "comparative_matrix",
        "enforcement_case_law",
        "black_letter_commentary",
        "canonical",
        "counter-analysis",
        "comparative-framework",
    ],
}


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for relative, sections in REQUIRED_TEMPLATE_SECTIONS.items():
        path = root / relative
        if not path.exists():
            errors.append(f"{relative}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        for section in sections:
            if section not in text:
                errors.append(f"{relative}: missing required section {section!r}")
    for relative, markers in REQUIRED_FRAMEWORK_MARKERS.items():
        path = root / relative
        if not path.exists():
            errors.append(f"{relative}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative}: missing required marker {marker!r}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)

    errors = check(args.root)
    if errors:
        for line in errors:
            print(f"FAIL: {line}", file=sys.stderr)
        return 1
    print("OK: output-mode templates and frameworks valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run it; expect pass**

```bash
python3 scripts/check-output-modes.py
```

Expected: `OK: output-mode templates and frameworks valid`. If it fails,
fix the underlying template or framework — do not loosen the validator.

- [ ] **Step 3: Register in `scripts/run-local-checks.py`**

Insert next to other `check-*.py` entries:

```python
{
    "id": "output_modes",
    "description": "Verify output-mode templates and frameworks (executive brief / comparative matrix / enforcement / black-letter).",
    "cmd": ["python3", "scripts/check-output-modes.py"],
},
```

- [ ] **Step 4: Run preflight**

```bash
python3 scripts/run-local-checks.py
```

Expected: `output_modes` PASS plus all existing checks PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/check-output-modes.py scripts/run-local-checks.py
git commit -m "Add output-modes validator and register in preflight"
```

## Chunk 2: Metadata, formatter, manifest, fixtures

### Task 7: Document `output_mode` in the output contract skill

**Files:**

- Modify: `skills/output-contract.md`
- Modify: `templates/meta.example.json`

- [ ] **Step 1: Add the new field to `skills/output-contract.md`**

After the existing `## Optional Claim Checks` block, insert:

```markdown
## Optional Output Mode

`output_mode` is optional and additive. Existing readers ignore it. When
present, it must be one of:

- `executive_brief`
- `comparative_matrix`
- `enforcement_case_law`
- `black_letter_commentary`
- `canonical` (default; equivalent to omitting the field)

Optional companion fields:

- `output_mode_audience`: free-text audience descriptor (e.g. `C-suite`,
  `compliance team`, `litigation lead`).
- `output_mode_format`: one of `markdown` or `docx_ready` or `docx`.
  When `docx`, the deliverable is generated via `scripts/render-docx.py`
  on top of `docx_ready_markdown` packaging.

Apply `skills/output-mode-composition.md` whenever a non-`canonical`
mode is selected for a standalone deliverable. The orchestrator-compatible
`legal-research-agent-result.md` is unchanged regardless of `output_mode`.
```

- [ ] **Step 2: Add example to `templates/meta.example.json`**

Append (or merge into the existing example) the optional keys:

```json
{
  "output_mode": "canonical",
  "output_mode_audience": null,
  "output_mode_format": "markdown"
}
```

- [ ] **Step 3: Run the conventions check and the result-structure check**

```bash
python3 scripts/check-claude-conventions.py
python3 scripts/check-result-structure.py tests/fixtures/output/valid
```

Both must continue to pass.

- [ ] **Step 4: Commit**

```bash
git add skills/output-contract.md templates/meta.example.json
git commit -m "Document output_mode optional metadata field"
```

### Task 8: Extend the standalone formatter skill

**Files:**

- Modify: `skills/legal-writing-formatter.md`

The formatter must dispatch to `output-mode-composition` when a non-
canonical mode is selected, while keeping its existing behavior for
`canonical` (or unset).

- [ ] **Step 1: Insert dispatch language**

Inside `## Output Modes`, after the existing modes table, append:

```markdown
## Cross-Cutting Output Mode

When `output_mode` is set to `executive_brief`, `comparative_matrix`,
`enforcement_case_law`, or `black_letter_commentary`, apply
`skills/output-mode-composition.md` after deliverable selection but
before legal prose rewrite. The composition skill resolves the mode
template, applies the per-mode counter-analysis minimum, and produces
the mode-shaped deliverable file.

The packaging mode (`standalone_markdown` / `handoff_packet` /
`docx_ready_markdown`) is independent. A given run can produce
`comparative_matrix` + `docx_ready_markdown` or `executive_brief` +
`handoff_packet`. Defaults are recorded in
`knowledge/output-modes/mode-index.md`.
```

- [ ] **Step 2: Run the conventions check**

```bash
python3 scripts/check-claude-conventions.py
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add skills/legal-writing-formatter.md
git commit -m "Wire output-mode-composition into the standalone formatter"
```

### Task 9: Update `check-formatter-output.py` for mode-aware validation

**Files:**

- Modify: `scripts/check-formatter-output.py`

The formatter validator already checks language and meta consistency.
Extend it with an optional `--output-mode <slug>` flag that, when
present, additionally enforces the per-mode required template sections.

- [ ] **Step 1: Add the CLI flag and dispatch**

Find the `argparse` setup and add:

```python
parser.add_argument(
    "--output-mode",
    choices=["canonical", "executive_brief", "comparative_matrix",
             "enforcement_case_law", "black_letter_commentary"],
    default=None,
    help="Optional output-mode-specific structural check.",
)
```

Then, after the existing structural checks, add:

```python
if args.output_mode and args.output_mode != "canonical":
    required = REQUIRED_OUTPUT_MODE_SECTIONS.get(args.output_mode, [])
    text = formatted_path.read_text(encoding="utf-8")
    for section in required:
        if section not in text:
            errors.append(
                f"{formatted_path}: missing required section for "
                f"output_mode={args.output_mode!r}: {section!r}"
            )
```

Define `REQUIRED_OUTPUT_MODE_SECTIONS` with the same map used by
`scripts/check-output-modes.py`. Reuse by importing the constant if
clean, or duplicate the constant and add a `tests/test_output_modes.py`
parity assertion (Task 11) so they stay in sync.

- [ ] **Step 2: Run the existing formatter fixture suite**

```bash
python3 scripts/check-formatter-output.py tests/fixtures/formatter
```

Expected: PASS (no `--output-mode` flag; existing fixtures unaffected).

- [ ] **Step 3: Commit**

```bash
git add scripts/check-formatter-output.py
git commit -m "Add optional --output-mode flag to check-formatter-output.py"
```

### Task 10: Add fixtures for each output mode

**Files:**

- Create: `tests/fixtures/output-modes/executive-brief/{meta.json,result.md,deliverable.md}`
- Create: `tests/fixtures/output-modes/comparative-matrix/{meta.json,result.md,deliverable.md}`
- Create: `tests/fixtures/output-modes/enforcement-case-law/{meta.json,result.md,deliverable.md}`
- Create: `tests/fixtures/output-modes/black-letter-commentary/{meta.json,result.md,deliverable.md}`

Each fixture has:

- `legal-research-agent-meta.json` — canonical metadata with
  `output_mode` set.
- `legal-research-agent-result.md` — canonical 9-section memo
  (orchestrator contract).
- `deliverable.md` — mode-shaped deliverable rendered against the
  matching template.

Use realistic but compact content (re-use sources from existing
golden-set fixtures where possible). The validator does not need
substantive legal content — it needs structural conformance.

- [ ] **Step 1: Build the four fixtures**

For each mode, copy the matching template into `deliverable.md`,
fill placeholder text with one example finding, and ensure every
required section header is present. Reuse a minimal `meta.json`
shape based on `tests/fixtures/output/valid/legal-research-agent-meta.json`
plus the new `output_mode` field.

- [ ] **Step 2: Run the new validator against each fixture**

```bash
python3 scripts/check-formatter-output.py tests/fixtures/output-modes/executive-brief/deliverable.md \
  --meta tests/fixtures/output-modes/executive-brief/legal-research-agent-meta.json \
  --language en \
  --output-mode executive_brief

python3 scripts/check-formatter-output.py tests/fixtures/output-modes/comparative-matrix/deliverable.md \
  --meta tests/fixtures/output-modes/comparative-matrix/legal-research-agent-meta.json \
  --language en \
  --output-mode comparative_matrix

python3 scripts/check-formatter-output.py tests/fixtures/output-modes/enforcement-case-law/deliverable.md \
  --meta tests/fixtures/output-modes/enforcement-case-law/legal-research-agent-meta.json \
  --language en \
  --output-mode enforcement_case_law

python3 scripts/check-formatter-output.py tests/fixtures/output-modes/black-letter-commentary/deliverable.md \
  --meta tests/fixtures/output-modes/black-letter-commentary/legal-research-agent-meta.json \
  --language en \
  --output-mode black_letter_commentary
```

All four must PASS. If a fixture fails, fix the fixture — do not
loosen the validator.

- [ ] **Step 3: Commit**

```bash
git add tests/fixtures/output-modes/
git commit -m "Add structural fixtures for the four output modes"
```

### Task 11: Add the unit test

**Files:**

- Create: `tests/test_output_modes.py`

- [ ] **Step 1: Write the test**

```python
#!/usr/bin/env python3
"""Validate output-mode templates, frameworks, and fixtures."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class OutputModesTest(unittest.TestCase):
    def test_templates_and_frameworks_valid(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/check-output-modes.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode, 0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    def test_each_fixture_passes_mode_aware_formatter_check(self) -> None:
        modes = [
            ("executive-brief", "executive_brief"),
            ("comparative-matrix", "comparative_matrix"),
            ("enforcement-case-law", "enforcement_case_law"),
            ("black-letter-commentary", "black_letter_commentary"),
        ]
        for fixture_dir, slug in modes:
            with self.subTest(slug=slug):
                base = REPO_ROOT / "tests" / "fixtures" / "output-modes" / fixture_dir
                result = subprocess.run(
                    [
                        sys.executable, "scripts/check-formatter-output.py",
                        str(base / "deliverable.md"),
                        "--meta", str(base / "legal-research-agent-meta.json"),
                        "--language", "en",
                        "--output-mode", slug,
                    ],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    result.returncode, 0,
                    msg=f"slug={slug}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
                )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run it**

```bash
python3 tests/test_output_modes.py
```

Expected: 2 tests, all PASS.

- [ ] **Step 3: Run the full preflight**

```bash
python3 scripts/run-local-checks.py
```

Expected: 21/21 PASS (existing 20 plus the new `output_modes` entry).

- [ ] **Step 4: Commit**

```bash
git add tests/test_output_modes.py
git commit -m "Add output-modes unit tests"
```

## Chunk 3: User-facing documentation

### Task 12: Create the docs/en and docs/ko directory bridges

**Files:**

- Create: `docs/en/README.md`
- Create: `docs/ko/README.md`

- [ ] **Step 1: Write the bridges**

`docs/en/README.md`:

```markdown
This directory holds the English user-facing docs for `legal-research-agent`.

- [How to Use](how-to-use.md)
- [Disclaimer](disclaimer.md)
- [MCP Setup Guide](mcp-setup-guide.md)

The project README lives at the repository root: [`README.md`](../../README.md).
```

`docs/ko/README.md`:

```markdown
이 디렉터리는 `legal-research-agent`의 한국어 사용자 문서를 담습니다.

- [사용 가이드](how-to-use.md)
- [면책조항](disclaimer.md)
- [MCP 설정 가이드](mcp-setup-guide.md)

프로젝트 메인 README는 리포 루트의 [`README.ko.md`](../../README.ko.md)에 있습니다.
```

- [ ] **Step 2: Commit**

```bash
git add docs/en/README.md docs/ko/README.md
git commit -m "Add docs/en and docs/ko index bridges"
```

### Task 13: Write the How to Use docs

**Files:**

- Create: `docs/en/how-to-use.md`
- Create: `docs/ko/how-to-use.md`

The doc is the user's "first session" walkthrough. Cover:
prerequisites, standalone use, slash commands, output modes, packaging
modes, citation audit, MCP degradation behavior, troubleshooting.

- [ ] **Step 1: English version**

The English version mirrors the structure used by
`general-legal-research/docs/en/how-to-use.md`, but written for our
agent and our four output modes plus the canonical research mode.
Required sections (validator-enforced, see Task 18):

- `## Prerequisites`
- `## Quick Start`
- `## Research Modes` (the four routing modes)
- `## Output Modes` (the four deliverable shapes plus canonical)
- `## Packaging Modes`
- `## Citation Audit`
- `## Local-Only vs MCP-Connected`
- `## Tips`

Cross-link to README.md, disclaimer.md, mcp-setup-guide.md, and
docs/citation-audit.md (created in Task 16).

- [ ] **Step 2: Korean version**

`docs/ko/how-to-use.md` mirrors the English version section-by-section.
Section headings stay English where they are anchors used elsewhere
(`## Prerequisites`, `## Quick Start`, etc.). Body prose is Korean.

- [ ] **Step 3: Commit**

```bash
git add docs/en/how-to-use.md docs/ko/how-to-use.md
git commit -m "Add How to Use docs (en/ko)"
```

### Task 14: Write the Disclaimer docs

**Files:**

- Create: `docs/en/disclaimer.md`
- Create: `docs/ko/disclaimer.md`

The disclaimer covers: personal-project status, not legal advice, AI
limitations (hallucinations / fabricated citations / outdated rules /
jurisdiction conflation / source-hierarchy misclassification), data
handling, no warranty, scope of responsibility.

- [ ] **Step 1: Choose the license**

The current repo has no `LICENSE`. The disclaimer must reference one.
Apache 2.0 and MIT are both reasonable. Default to **Apache 2.0** to
match the predecessor `general-legal-research` README badge unless the
user requests otherwise. Add a `LICENSE` file at the repo root with the
chosen text before committing the disclaimer.

- [ ] **Step 2: English version**

Required sections (validator-enforced, see Task 18):

- `## Personal Project`
- `## Not Legal Advice`
- `## AI Limitations`
- `## Data Handling`
- `## No Warranty`
- `## Scope of Responsibility`

The AI Limitations section must enumerate at least the six failure
modes from the predecessor disclaimer (fabricate authority, misstate
the law, conflate jurisdictions, omit material issues, misclassify
source hierarchy, invent citations).

- [ ] **Step 3: Korean version**

`docs/ko/disclaimer.md` mirrors with Korean prose. Anchors stay
English.

- [ ] **Step 4: Commit**

```bash
git add LICENSE docs/en/disclaimer.md docs/ko/disclaimer.md
git commit -m "Add LICENSE and Disclaimer docs (en/ko)"
```

### Task 15: Write the MCP Setup Guide

**Files:**

- Create: `docs/en/mcp-setup-guide.md`
- Create: `docs/ko/mcp-setup-guide.md`

This guide covers the `korean-law` MCP server registration, how it
maps to our `mcp__claude_ai_Korean-law__*` toolset, and what happens
when MCP is unavailable (graceful degradation to `WebSearch` / `WebFetch`
plus `mcp_unavailable` error tagging).

- [ ] **Step 1: English version**

Required sections (validator-enforced, see Task 18):

- `## Korean Law MCP Server`
- `## Configuration`
- `## Verification`
- `## Degradation Behavior`
- `## Troubleshooting`

Reference `mcp__claude_ai_Korean-law__search_law`,
`mcp__claude_ai_Korean-law__get_law_text`,
`mcp__claude_ai_Korean-law__chain_full_research`, and the
`korean-law-mcp` upstream project. Mention that the agent records
`mcp_unavailable` in `coverage_gaps` when the server is missing or
degraded, per `skills/source-collection.md`.

- [ ] **Step 2: Korean version**

Mirror with Korean prose. Anchors stay English.

- [ ] **Step 3: Commit**

```bash
git add docs/en/mcp-setup-guide.md docs/ko/mcp-setup-guide.md
git commit -m "Add MCP Setup Guide (en/ko)"
```

### Task 16: Write the Citation Audit canonical spec

**Files:**

- Create: `docs/citation-audit.md`

This is the single source of truth for citation audit behavior across
the standalone `/audit` invocation and the standalone deliverable
workflow. Mirror the structure of
`general-legal-research/docs/citation-audit.md` but adapted to our agent.

- [ ] **Step 1: Write the spec**

Required sections (validator-enforced, see Task 18):

- `## Invocation Contexts`
- `## Output Artifacts`
- `## Format Support Matrix`
- `## Detailed Status Model`
- `## Korean-Law MCP Degradation`
- `## 한국어 요약`

Cover:

1. Two invocation contexts: standalone `/audit` (manual) vs. standalone
   deliverable workflow (auto-folded into manifest).
2. Output artifacts produced by each context: per-claim audit JSON,
   sidecar `.audit.md` for DOCX, manifest `audit.status` field.
3. Format support matrix: `.md` full append, `.docx` appendix
   integration via `scripts/render-docx.py`, other formats sidecar-only.
4. Status model: `verified`, `contradicted`, `unsupported`,
   `source_unavailable`, `verifier_unavailable`, `not_a_legal_claim`,
   `unknown`.
5. Korean-law MCP degradation: how `mcp_unavailable` propagates from
   the agent into the audit metadata.
6. Korean-language summary at the end.

- [ ] **Step 2: Commit**

```bash
git add docs/citation-audit.md
git commit -m "Add canonical Citation Audit spec"
```

### Task 17: Write the Release Process spec

**Files:**

- Create: `docs/release-process.md`

A short, concrete checklist that future releases run before publishing.
Tie it to the existing local preflight.

- [ ] **Step 1: Write the spec**

Required sections (validator-enforced, see Task 18):

- `## Pre-Release Checklist`
- `## Version Tagging`
- `## Release Notes`
- `## Post-Release`

Required content:

- Run `python3 scripts/run-local-checks.py` and require all checks PASS.
- Run `python3 scripts/measure-prompt-footprint.py` and confirm token
  footprint is recorded.
- Run `python3 scripts/compare-token-runs.py` against the latest
  manifest and confirm `quality_status` is acceptable.
- Tag the release as `v<MAJOR>.<MINOR>.<PATCH>` after the merge commit.
- Cross-link from README's Roadmap.

- [ ] **Step 2: Commit**

```bash
git add docs/release-process.md
git commit -m "Add Release Process spec"
```

## Chunk 4: README integration and knowledge-coverage enforcement

### Task 18: Extend `check-knowledge-coverage.py` to enforce required markers in new docs

**Files:**

- Modify: `scripts/check-knowledge-coverage.py`

- [ ] **Step 1: Add required markers**

Append to `REQUIRED_MARKERS` dict:

```python
"docs/en/how-to-use.md": [
    "## Prerequisites",
    "## Quick Start",
    "## Research Modes",
    "## Output Modes",
    "## Packaging Modes",
    "## Citation Audit",
    "## Local-Only vs MCP-Connected",
    "## Tips",
],
"docs/ko/how-to-use.md": [
    "## Prerequisites",
    "## Quick Start",
    "## Research Modes",
    "## Output Modes",
    "## Packaging Modes",
    "## Citation Audit",
    "## Local-Only vs MCP-Connected",
    "## Tips",
],
"docs/en/disclaimer.md": [
    "## Personal Project",
    "## Not Legal Advice",
    "## AI Limitations",
    "## Data Handling",
    "## No Warranty",
    "## Scope of Responsibility",
    "fabricate",
    "conflate",
    "invent citations",
],
"docs/ko/disclaimer.md": [
    "## Personal Project",
    "## Not Legal Advice",
    "## AI Limitations",
    "## Data Handling",
    "## No Warranty",
    "## Scope of Responsibility",
],
"docs/en/mcp-setup-guide.md": [
    "## Korean Law MCP Server",
    "## Configuration",
    "## Verification",
    "## Degradation Behavior",
    "## Troubleshooting",
    "mcp__claude_ai_Korean-law__",
    "mcp_unavailable",
],
"docs/ko/mcp-setup-guide.md": [
    "## Korean Law MCP Server",
    "## Configuration",
    "## Verification",
    "## Degradation Behavior",
    "## Troubleshooting",
],
"docs/citation-audit.md": [
    "## Invocation Contexts",
    "## Output Artifacts",
    "## Format Support Matrix",
    "## Detailed Status Model",
    "## Korean-Law MCP Degradation",
    "## 한국어 요약",
    "verified",
    "contradicted",
    "unsupported",
    "source_unavailable",
    "verifier_unavailable",
    "not_a_legal_claim",
],
"docs/release-process.md": [
    "## Pre-Release Checklist",
    "## Version Tagging",
    "## Release Notes",
    "## Post-Release",
    "scripts/run-local-checks.py",
    "scripts/measure-prompt-footprint.py",
    "scripts/compare-token-runs.py",
],
```

- [ ] **Step 2: Run the check**

```bash
python3 scripts/check-knowledge-coverage.py
```

Expected: PASS (because Tasks 13–17 already wrote the required markers
into the new docs).

- [ ] **Step 3: Commit**

```bash
git add scripts/check-knowledge-coverage.py
git commit -m "Enforce required markers in new user-facing docs"
```

### Task 19: Update README.md and README.ko.md

**Files:**

- Modify: `README.md`
- Modify: `README.ko.md`

The current "Standalone Deliverables" section describes only the three
packaging modes. Replace it with a richer "Output Modes" section that
documents the four deliverable shapes plus canonical, mirroring the
depth of `general-legal-research/README.md`'s output-modes section.

- [ ] **Step 1: Restructure the README's Standalone Deliverables section**

Rename to `## Output Modes` with two subsections:

```markdown
## Output Modes

### Deliverable shape

| Mode | Slug | Best for | Default packaging |
|:---|:---|:---|:---|
| Executive Brief (Mode A) | `executive_brief` | Decision-makers, C-suite | `standalone_markdown` |
| Comparative Matrix (Mode B) | `comparative_matrix` | Multi-jurisdiction compliance | `standalone_markdown` |
| Enforcement and Case Law (Mode C) | `enforcement_case_law` | Litigation, enforcement strategy | `standalone_markdown` |
| Black-letter and Commentary (Mode D) | `black_letter_commentary` | Statute or regulation deep dive | `docx_ready_markdown` |
| Canonical research memo *(default)* | `canonical` | Orchestrator-compatible record | `standalone_markdown` |

### Packaging mode

| Mode | Use when |
|:---|:---|
| `standalone_markdown` | Default polished memo or opinion-style note |
| `handoff_packet` | A downstream legal-writing agent will draft |
| `docx_ready_markdown` | Word-ready source or binary DOCX requested |

The two axes are independent — see
`knowledge/output-modes/mode-index.md` for slug-to-template resolution.

The orchestrator-compatible `legal-research-agent-result.md` always
uses the canonical 9-section structure. Mode-shaped deliverables sit
under `deliverables/` and are recorded in
`standalone-deliverable-manifest.json`.

For frameworks and per-mode counter-analysis discipline:

- [`knowledge/output-modes/comparative-framework.md`](knowledge/output-modes/comparative-framework.md)
- [`knowledge/output-modes/counter-analysis-checklist.md`](knowledge/output-modes/counter-analysis-checklist.md)
- [`knowledge/output-modes/mode-index.md`](knowledge/output-modes/mode-index.md)

For the standalone deliverable workflow, naming rules, manifest, and
citation audit sequencing, see
[`docs/standalone-workflow.md`](docs/standalone-workflow.md).
```

- [ ] **Step 2: Update the top-of-page link bar**

Add user-doc links:

```markdown
**[How to Use](docs/en/how-to-use.md)** · **[Disclaimer](docs/en/disclaimer.md)** · **[MCP Setup Guide](docs/en/mcp-setup-guide.md)** · **[Citation Audit Spec](docs/citation-audit.md)** · **[Release Process](docs/release-process.md)** · **[Standalone Workflow](docs/standalone-workflow.md)** · **[Orchestrator Intake](docs/orchestrator-intake.md)**
```

- [ ] **Step 3: Mirror in `README.ko.md`**

Same restructuring with Korean prose. Anchors and slugs stay English.
Update the top-of-page link bar to point at `docs/ko/` for the
translated docs and `docs/citation-audit.md` / `docs/release-process.md`
for the language-neutral specs.

- [ ] **Step 4: Run the conventions check**

```bash
python3 scripts/check-claude-conventions.py
```

Expected: PASS (README is not a conventions check target, but ensure
no regression).

- [ ] **Step 5: Commit**

```bash
git add README.md README.ko.md
git commit -m "Document Output Modes and link new user docs in both READMEs"
```

### Task 20: Update CLAUDE.md and the /research slash command

**Files:**

- Modify: `CLAUDE.md`
- Modify: `.claude/commands/research.md`

- [ ] **Step 1: Add an `output_mode` paragraph to CLAUDE.md**

Inside the existing `## Workflow` step 7 block, append:

```markdown
   - For standalone deliverables, the `output_mode` (default `canonical`)
     selects the deliverable shape per
     `knowledge/output-modes/mode-index.md`. When the mode is non-canonical,
     apply `skills/output-mode-composition.md` after
     `skills/legal-writing-formatter.md` so the canonical research record
     stays unchanged.
```

- [ ] **Step 2: Update the `/research` slash command argument hint**

Edit `.claude/commands/research.md`:

```markdown
---
description: Run a source-first legal research task using the legal-research-agent workflow.
argument-hint: "<jurisdiction or topic> <question text> [mode=executive_brief|comparative_matrix|enforcement_case_law|black_letter_commentary|canonical]"
---
```

In the body, append a short paragraph:

```markdown
If the user names a mode (e.g. `mode=comparative_matrix`), apply
`skills/output-mode-composition.md` after the canonical research record
is complete and use the matching template under `templates/output-modes/`.
```

- [ ] **Step 3: Run the conventions check**

```bash
python3 scripts/check-claude-conventions.py
```

Expected: PASS.

- [ ] **Step 4: Run knowledge-coverage**

```bash
python3 scripts/check-knowledge-coverage.py
```

Expected: PASS (existing CLAUDE.md markers preserved).

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md .claude/commands/research.md
git commit -m "Wire output_mode into CLAUDE.md workflow and /research command"
```

## Chunk 5: Final verification

### Task 21: Full preflight + push

- [ ] **Step 1: Run the full preflight**

```bash
python3 scripts/run-local-checks.py
```

Expected: 22/22 PASS (existing 20 + `output_modes` from Task 6 +
`claude_conventions` already there + any other new check). Adjust
the expected count to whatever the registry shows after all tasks.

- [ ] **Step 2: Run the meta-test**

```bash
python3 tests/test_run_local_checks.py
```

Expected: PASS. If it asserts a fixed registry count, update it.

- [ ] **Step 3: Run full test discovery**

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

Expected: 167+ tests, all OK.

- [ ] **Step 4: Confirm no preflight regression in CI-relevant scripts**

```bash
python3 scripts/measure-prompt-footprint.py
```

Expected: footprint grows by the new template/skill/knowledge bytes
plus the new doc bytes; do not update the frozen Phase 0 snapshot in
`docs/prompt-footprint.md` unless the user says so.

- [ ] **Step 5: Push**

```bash
git push origin main
```

Or open a PR if branching policy changes.

## Verification Plan

After Task 21, all of these must pass cleanly:

```bash
python3 scripts/run-local-checks.py
python3 scripts/check-output-modes.py
python3 scripts/check-claude-conventions.py
python3 scripts/check-knowledge-coverage.py
python3 tests/test_output_modes.py
python3 tests/test_claude_conventions.py
python3 tests/test_run_local_checks.py
python3 tests/test_knowledge_coverage.py
python3 tests/test_formatter_output.py
python3 tests/test_standalone_workflow.py
python3 tests/test_output_contract.py
python3 tests/test_quality_evaluation.py
python3 tests/test_result_structure.py
python3 -m unittest discover -s tests -p "test_*.py"
```

Manual verification:

- Open the project in Claude Code; the README's new Output Modes
  section renders correctly with all anchor links resolving.
- Type `/research` and confirm the new `mode=` argument hint appears.
- From an orchestrator-style intake payload with `output_mode` set,
  confirm the agent produces both the canonical research record and a
  mode-shaped deliverable under `deliverables/`.
- Render a Mode D + `docx_ready_markdown` sample through
  `scripts/render-docx.py` and confirm the DOCX preserves required
  sections.

## Risk and Rollback

Risk surface is moderate but additive. The orchestrator-compatible
`result.md` and existing metadata fields are unchanged. No existing
skill body is rewritten beyond `skills/legal-writing-formatter.md`'s
appended dispatch paragraph and `skills/output-contract.md`'s appended
optional-field block. Existing tests, golden-set fixtures, and the
prompt footprint baseline are preserved.

Rollback: each task commits independently, and chunks are sequenced so
that the system stays in a runnable state at every commit boundary.
`git revert` of the relevant task commits restores prior behavior. The
output-mode validator and unit tests can be reverted without touching
the canonical research workflow.

## Done Definition

This plan is done when:

- `python3 scripts/run-local-checks.py` exits 0 from a clean checkout,
  including the new `output_modes` check.
- A standalone request that selects `output_mode=comparative_matrix`
  produces a deliverable that contains all ten standard axes from
  `knowledge/output-modes/comparative-framework.md`.
- A standalone request that selects `output_mode=executive_brief`
  produces a deliverable that satisfies the per-mode counter-analysis
  minimum from `knowledge/output-modes/counter-analysis-checklist.md`.
- The README's `## Output Modes` section, the link bar, and CLAUDE.md
  workflow language all describe the four modes plus canonical
  consistently.
- `docs/en/`, `docs/ko/`, `docs/citation-audit.md`, and
  `docs/release-process.md` exist with required markers, and
  `python3 scripts/check-knowledge-coverage.py` exits 0 against them.
- A `LICENSE` file exists at the repo root.
- No regression appears in any pre-existing test or quality gate.
