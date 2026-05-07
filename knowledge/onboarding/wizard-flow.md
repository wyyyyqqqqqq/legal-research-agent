# Onboarding Wizard Question Catalog

This file is the canonical question catalog used by the `/onboard`
slash command and the `skills/onboarding.md` skill body. The
controlled vocabulary here must match `scripts/check-user-config.py`
exactly — when one changes, the other must be updated in the same
commit.

## Question 1 — Industry

Single-select. Values:

| Value | Label |
|:---|:---|
| `game` | Game industry (publishing, ratings, virtual goods, randomized items) |
| `fintech` | Financial technology, payments, lending, virtual assets |
| `healthcare` | Healthcare, medical devices, biotech, pharma |
| `platform` | Online platforms, marketplaces, intermediary services |
| `e_commerce` | E-commerce, retail, consumer goods |
| `media` | Media, broadcasting, content distribution |
| `other` | Other industry — wizard collects free-text label |

When `other` is selected, the wizard asks a follow-up free-text
question (`industry_freetext`) that is required and stored verbatim.

## Question 2 — Area of law focus

Multi-select. At least one value required.

| Value | Label |
|:---|:---|
| `general` | General law (no narrower specialization) |
| `regulatory` | Regulatory compliance, sectoral licensing, agency rules |
| `contract` | Contract drafting, review, dispute |
| `consumer_protection` | Consumer protection, advertising, refund rules |
| `intellectual_property` | IP — trademark, patent, copyright, trade secrets |
| `employment` | Employment, labor, dispatch, severance |
| `privacy` | Data privacy, cross-border transfers, breach notification |
| `tax` | Tax, transfer pricing, indirect tax |
| `competition` | Competition, antitrust, M&A clearance |
| `other` | Other area — wizard collects free-text label |

## Question 3 — Primary jurisdictions

Multi-select. At least one value required. ISO country codes (or
`EU` / `UK` shortcuts):

`KR`, `US`, `JP`, `EU`, `UK`, `DE`, `FR`, `CN`, `SG`, `AU`, `CA`,
`BR`, `ES`, `IT`, `NL`, `IN`, `MX`, `OTHER`.

When `OTHER` is selected, the wizard asks a free-text follow-up and
stores the value in the primary list as a free-text token.

## Question 4 — Secondary jurisdictions

Multi-select. May be empty. Same vocabulary as Question 3.

## Question 5 — Output preference

Single-select shortcut bundle. Each shortcut sets
`default_output_mode`, `default_packaging`, and `default_language`
together.

| Shortcut | Output mode | Packaging | Language | Best for |
|:---|:---|:---|:---|:---|
| Quick brief in Korean | `executive_brief` | `standalone_markdown` | `ko` | 임원·의사결정자 |
| Quick brief in English | `executive_brief` | `standalone_markdown` | `en` | C-suite, foreign counsel |
| Multi-jurisdiction comparison | `comparative_matrix` | `standalone_markdown` | `en` | Cross-border compliance |
| Statute deep dive (DOCX) | `black_letter_commentary` | `docx_ready_markdown` | `ko` | In-house counsel deep dive |
| Enforcement / case-law trends | `enforcement_case_law` | `standalone_markdown` | `en` | Litigation strategy |
| Default research memo | `canonical` | `standalone_markdown` | `ko` | Mixed daily work |

When the user selects a shortcut, the wizard records the three
fields together. The user may override any field individually after
the wizard finishes by editing `user-config.json`.

## Question 6 — Build a starter knowledge directory now?

Single-select.

| Value | Behavior |
|:---|:---|
| `yes` | Run the recipe in `docs/knowledge-construction-recipe.md` for the chosen `industry`-`area_of_law`-`jurisdiction` triple. Generation runs live research, writes `knowledge/<industry>-<area>/` files, runs citation audit, and reports the audit status. Files are gated `[GENERATED — REQUIRES HUMAN REVIEW]` until `/review-knowledge` lifts the gate. |
| `no` | Skip generation. The user can run `/onboard --build-knowledge` later or write knowledge by hand following the same recipe. |
| `later` | Same as `no` semantically; recorded so the wizard can offer to build at a later session. |

When the user selects multiple `area_of_law` values in Question 2,
the wizard generates one directory per area (e.g.,
`knowledge/fintech-regulatory/`, `knowledge/fintech-privacy/`) and
asks per-area whether to generate.

## Derivation rules

After Questions 1–5, the wizard derives `default_research_mode`:

- `industry == "game"` and any `area_of_law` value other than
  `general` → `default_research_mode = "game_regulation"`.
- `industry == "game"` and `area_of_law == ["general"]` exactly →
  `default_research_mode = "general"` (rare; record a
  `classification_warnings` flag if the user proceeds).
- `industry != "game"` and any `area_of_law` value present →
  `default_research_mode = "general"`.
- If the user explicitly mentions a non-game-industry question with
  game-adjacent issues during a research run later, the agent picks
  `game_plus_general` per `skills/classify-research-mode.md`.
- `default_research_mode` is never `fallback` from the wizard — that
  mode is only chosen by the agent at runtime when source coverage
  is insufficient or the topic is out of scope.

## Skip rules

- **Question 4** (secondary jurisdictions) may be skipped (empty
  list).
- **Question 6** is skipped entirely when the user runs
  `/onboard --skip-knowledge`. The wizard does not prompt and does
  not generate.
- **All questions** are skipped when the user runs `/onboard
  --reset` against an existing config and confirms replacement; in
  that case the wizard re-asks every question. Without `--reset`,
  the wizard offers field-by-field update of an existing config.

## Update rules

When `user-config.json` already exists and the user runs `/onboard`:

1. Load the current config and summarize the active values.
2. Ask whether to update specific fields (per question) or replace
   wholesale.
3. Update mode preserves fields not touched.
4. Replace mode requires explicit confirmation and discards the
   prior config (after offering to back up to
   `user-config.previous.json`, which is also gitignored).

## Authoritative vocabulary

The controlled vocabulary above must agree with the constants in
`scripts/check-user-config.py`:

- `ALLOWED_INDUSTRIES`
- `ALLOWED_AREAS`
- `ALLOWED_RESEARCH_MODES`
- `ALLOWED_OUTPUT_MODES`
- `ALLOWED_PACKAGING`
- `ALLOWED_LANGUAGES`

Any change to one must be accompanied by a change to the other in
the same commit.
