**Language:** [한국어](../ko/how-to-use.md) | [**English**](how-to-use.md)

# How to Use | Legal Research Agent

> **[README](../../README.md)** | **[Disclaimer](disclaimer.md)** | **[MCP Setup Guide](mcp-setup-guide.md)** | **[Citation Audit Spec](../citation-audit.md)**

This guide walks you through running `legal-research-agent` for the first
time. The agent runs entirely inside a Claude Code session and produces
two contract files (orchestrator-compatible) plus optional mode-shaped
deliverables.

## Prerequisites

| Requirement | Details |
|:---|:---|
| **Claude Code** | [CLI](https://claude.ai/code) installed and authenticated |
| **Python 3.11+** | Standard library only for the validators; `marko`, `pydantic`, `python-docx` for the renderer (see `pyproject.toml`) |
| **`korean-law` MCP server** | Optional but strongly preferred for KR primary-source coverage. See the [MCP Setup Guide](mcp-setup-guide.md) |
| **Network** | Required for `WebFetch` / `WebSearch` fallbacks; not required for the local preflight |

## Quick Start

1. Open the project directory in Claude Code:

   ```bash
   cd legal-research-agent
   claude
   ```

2. Ask your research question in natural language, in English or Korean.
   The agent reads `CLAUDE.md`, picks a research mode, and runs the
   8-stage workflow.

3. (Optional) Use the `/research` slash command for an explicit invocation:

   ```text
   /research <jurisdiction or topic> <question text> [mode=<output_mode>]
   ```

4. The agent writes two contract files into the orchestrator-supplied
   `output_dir` (or your working directory in standalone use):

   - `legal-research-agent-result.md` — canonical 9-section research record
   - `legal-research-agent-meta.json` — orchestrator-compatible metadata

5. If you requested a polished deliverable (executive brief, comparative
   matrix, etc.), the agent also writes a mode-shaped file under
   `deliverables/` and updates `standalone-deliverable-manifest.json`.
   See [`docs/standalone-workflow.md`](../standalone-workflow.md).

## Personal Configuration

For repeated standalone use, the `/onboard` slash command captures your
default scope (industry, area-of-law focus, jurisdictions, language,
preferred output mode) into `user-config.json` so the agent reuses the
same defaults every session. The wizard never collects personal
identifiers — preferences only.

```text
/onboard
```

The wizard asks five questions plus an optional sixth:

1. Industry — `game`, `fintech`, `healthcare`, `platform`, `e_commerce`,
   `media`, or `other`.
2. Area-of-law focus — multi-select from `general`, `regulatory`,
   `contract`, `consumer_protection`, `intellectual_property`,
   `employment`, `privacy`, `tax`, `competition`, `other`.
3. Primary jurisdictions — at least one ISO country code (or `EU` /
   `UK` shortcuts).
4. Secondary jurisdictions — optional.
5. Output preference — a shortcut bundle that sets default
   `output_mode`, packaging, and language together.
6. *(Optional)* Build a starter knowledge directory now? — when
   `yes`, the wizard executes the recipe in
   [`docs/knowledge-construction-recipe.md`](../knowledge-construction-recipe.md)
   to generate a `knowledge/<industry>-<area>/` directory with
   regulator map, source map, issue taxonomy, and library index. The
   directory is gated `[GENERATED — REQUIRES HUMAN REVIEW]` until the
   user lifts the gate via `/review-knowledge`.

The full schema lives at
[`templates/user-config.example.json`](../../templates/user-config.example.json),
and the validator at
[`scripts/check-user-config.py`](../../scripts/check-user-config.py)
runs as part of the local preflight.

### Replacing or refreshing the config

```text
/onboard --reset             # full re-run after explicit confirmation
/onboard --build-knowledge   # rebuild the knowledge directory only
/onboard --skip-knowledge    # update preferences without touching knowledge
```

### Reviewing a generated knowledge directory

When the wizard built a knowledge directory (Question 6 = `yes`), every
`.md` file starts with `[GENERATED — REQUIRES HUMAN REVIEW]`. After
inspecting and (optionally) editing the contents, lift the gate:

```text
/review-knowledge knowledge/<industry>-<area>/
```

The slash command verifies the directory passes
`scripts/check-generated-knowledge.py`, replaces the banner with
`[VERIFIED]`, and updates the matching entry in `user-config.json`.

### Precedence

| Run mode | Primary | Fallback |
|:---|:---|:---|
| Standalone | `user-config.json` defaults | Per-question overrides win when explicit |
| Subagent dispatch | Orchestrator classification | `user-config.json` fills only fields the orchestrator did not specify |

### Privacy and file location

`user-config.json` lives at the project root. It is gitignored, so
the file stays on your machine. Generated knowledge directories under
`knowledge/<industry>-<area>/` are also gitignored by default — they
move out of the ignore list only when you intentionally commit
reviewed knowledge to share.

The wizard never collects names, firms, or bar admissions. Only
preferences (industry, jurisdictions, output mode, language) are
stored.

## Research Modes

The agent picks one of four research modes based on the orchestrator
classification, the `/research` argument, or self-classification:

| Mode | Use when |
|:---|:---|
| `general` | Ordinary legal questions where no narrower specialist applies |
| `game_regulation` | Game publishing, randomized items, ratings, virtual goods, platform compliance, youth protection |
| `game_plus_general` | Game-industry question with a distinct non-game legal issue |
| `fallback` | Ambiguous question, insufficient source coverage, or out of scope |

Routing rules and self-classification logic live in
`skills/classify-research-mode.md` and `CLAUDE.md`.

## Output Modes

Output mode shapes the *deliverable structure* — independent of the
research mode (which routes the *content domain*). The four named modes
mirror predecessor `general-legal-research`'s Mode A/B/C/D plus a fifth
`canonical` slug for the orchestrator-compatible 9-section memo.

| Slug | Label | Best for |
|:---|:---|:---|
| `executive_brief` | Executive Brief (Mode A) | Decision-makers, C-suite |
| `comparative_matrix` | Comparative Matrix (Mode B) | Multi-jurisdiction compliance |
| `enforcement_case_law` | Enforcement and Case Law (Mode C) | Litigation, enforcement strategy |
| `black_letter_commentary` | Black-letter and Commentary (Mode D) | Statute or regulation deep dive |
| `canonical` *(default)* | Canonical research memo | Orchestrator-compatible record |

Selection rules and the slug-to-template map live in
[`knowledge/output-modes/mode-index.md`](../../knowledge/output-modes/mode-index.md).
Each non-canonical mode comes with a template under
[`templates/output-modes/`](../../templates/output-modes/) and a
counter-analysis discipline under
[`knowledge/output-modes/counter-analysis-checklist.md`](../../knowledge/output-modes/counter-analysis-checklist.md).

## Packaging Modes

Packaging is the *output format* axis, orthogonal to output mode. A run
picks one packaging slug:

| Mode | Use when |
|:---|:---|
| `standalone_markdown` | Default polished memo or opinion-style note |
| `handoff_packet` | A downstream legal-writing agent will draft the final document |
| `docx_ready_markdown` | Word-ready source or binary DOCX requested |

Combine an output mode with a packaging mode for 5 × 3 = 15 valid
deliverable combinations. Defaults are recorded in
[`knowledge/output-modes/mode-index.md`](../../knowledge/output-modes/mode-index.md).

## Citation Audit

The agent ships the vendored
[`citation-auditor`](../../citation_auditor/) skill plus a per-jurisdiction
verifier family. Citation audit runs in two contexts:

| Context | Trigger | Behavior |
|:---|:---|:---|
| Standalone `/audit` | Manual invocation on any Markdown or DOCX file | Inline annotations on Markdown; sidecar `*.audit.md` and `*.audit.json` for DOCX |
| Standalone deliverable workflow | External or client-facing standalone output | Audit folded into the manifest; `live_passed` / `deterministic_smoke` / `not_run_session_unavailable` recorded explicitly |

The full canonical specification is in
[`docs/citation-audit.md`](../citation-audit.md).

## Local-Only vs MCP-Connected

| Mode | What works | What doesn't |
|:---|:---|:---|
| Local-only | All `scripts/` validators and tests; `WebSearch` / `WebFetch` against whitelisted legal portals; standalone formatter; mode template rendering | Korean primary-source MCP toolset; live verifier dispatch |
| MCP-connected | Full workflow including `mcp__claude_ai_Korean-law__*` tools (statutes, decrees, decisions, chain-research) | Requires registration in Claude.ai integrations or `.mcp.json` — see the [MCP Setup Guide](mcp-setup-guide.md) |

Without MCP, the agent records `mcp_unavailable` in `coverage_gaps` and
lowers confidence rather than guessing at primary law. The agent never
fabricates Korean primary law to fill an MCP gap.

## Tips

- **Be specific about jurisdictions.** The agent performs best when you
  name the country, state, or regulator you care about.
- **Pick an output mode if you have a preference.** "Give me a
  comparative matrix for KR vs JP" or "use `executive_brief`" both work.
- **Ask for `.docx` only when you actually need it.** DOCX rendering is
  an MVP via `scripts/render-docx.py`; native footnotes, tracked changes,
  comments, and complex page layout are intentionally not promised.
- **Watch for `coverage_gaps` entries.** They mark the limits of the
  research run and should not be smoothed away in client-facing copy.
- **Review every output.** This is a research tool, not a substitute
  for legal judgment. See the [Disclaimer](disclaimer.md).

## Local Preflight

Run all 21 validators in well under a second:

```bash
python3 scripts/run-local-checks.py
python3 scripts/run-local-checks.py --report
```

The preflight does not call MCP or the network. It validates fixtures,
contracts, frontmatter, output-mode templates, prompt-footprint, and the
deterministic citation-audit smoke. See the project README for the full
list.
