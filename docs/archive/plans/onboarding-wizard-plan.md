# Onboarding Wizard Implementation Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development`
> (if subagents are available) or `superpowers:executing-plans` to implement
> this plan. Steps use checkbox (`- [ ]`) syntax so progress can be tracked
> in the file itself.

**Goal:** Add an interactive `/onboard` slash command that asks the user
about their **industry**, **area-of-law focus**, **jurisdictions**, and
**output preferences**, then writes a project-local `user-config.json`
**and** executes a knowledge construction recipe that builds a curated
`knowledge/<industry>-<area>/` directory matching the depth of the
existing hand-curated `knowledge/game-regulation/`. Every generated
fact carries a source URL, the directory is gated `[GENERATED — REQUIRES
HUMAN REVIEW]` until the user lifts the gate, and `citation-auditor`
runs over the generated content before the gate is offered.

**Approach:** Two layers. **Layer 1** — runtime configuration via
`user-config.json` (existing skills consult it for defaults). **Layer 2**
— a versioned **knowledge construction recipe** at
`docs/knowledge-construction-recipe.md` that prescribes exactly how a
contributor (human or agent) builds a `knowledge/<area>/` directory:
required files, per-file structure, live-research protocol, source
verification rules, hallucination mitigations, and the human-review
gate. The wizard executes the recipe after writing the config; the same
recipe also serves as the contributor playbook for human-built knowledge
directories.

**Tech Stack:** Python 3.11+, JSON, Markdown, Mermaid, existing
`marko`/`pydantic`/`python-docx` runtime, `citation-auditor` for
post-generation validation.

## What "match game_regulation quality" really means

The current `game_regulation` mode delivers its quality from four
layers:

1. The right **research mode** is picked at intake.
2. The right **knowledge files** are loaded
   (`knowledge/game-regulation/` issue taxonomy, regulator map, source
   map, library index).
3. The **counter-analysis discipline** is applied per the per-mode
   minimum.
4. The right **output mode** is selected for the deliverable shape.

Layers 1, 3, and 4 are reproducible at runtime from a config. Layer 2
is the hard part — those knowledge files are hand-curated artifacts
that encode domain expertise (regulator names, statutory hierarchy,
agency precedents, similar-statute confusion traps). Option C in this
plan attacks Layer 2 with a versioned recipe plus a wizard executor
plus a mandatory verification gate:

- **Recipe-driven generation.** Every required file, section, and
  metadata field is specified in `docs/knowledge-construction-recipe.md`.
  The recipe applies equally to human contributors and to the wizard's
  agent execution.
- **Per-fact source verification.** Every regulator name, statute
  number, agency action, and source URL must be backed by a fetched
  source recorded in the file's frontmatter. Facts that cannot be
  sourced are marked `[Unverified]` and surfaced as gaps, not silently
  written as fact.
- **`[GENERATED — REQUIRES HUMAN REVIEW]` gate.** A generated knowledge
  directory is treated as draft. The agent disclaims its limitations
  every time it is loaded into a research run, and high-confidence
  conclusions cannot rely on a `[GENERATED]` source map alone. The
  `/review-knowledge` slash command lifts the gate after the user has
  reviewed and (optionally) edited the generated content.
- **Citation audit on output.** After generation, the wizard runs the
  vendored `citation-auditor` over the new knowledge directory to
  surface any unverifiable claims before handing the gate to the user.

**Realistic outcome.** With the gate lifted (post-review), a generated
`knowledge/<industry>-<area>/` matches `game_regulation` on process,
structure, and per-fact sourcing. Deeper hand-tuning (similar-statute
confusion traps unique to a specific industry, named agency
precedents, multi-jurisdiction comparison tables) still benefits from
human authorship, but the wizard delivers a usable starter that the
user edits rather than starts from scratch.

## Out of scope

- **Generating primary-law text** (statutes, regulations, recitals,
  case opinions) into article-level files. That is the GDPR-expert /
  PIPA-expert pattern. We generate metadata about regulators,
  statutes, and source URLs — not the law text itself.
- **Cross-jurisdiction unified knowledge directories** in a single
  generation pass (e.g., `knowledge/fintech-multi/` for KR + JP + US).
  One jurisdiction-and-area pair per generated directory keeps recipe
  execution simple. The wizard can run multiple times to cover
  multiple jurisdiction-area pairs.
- **Personal identifiers** in `user-config.json` (name, firm, bar
  admissions). Preferences only.
- **Cross-session or cross-machine config sync.**
- **Onboarding for the orchestrator subagent dispatch path.** The
  wizard is for standalone users; orchestrator dispatch keeps using
  its classification payload.
- **Web search or live MCP calls during the wizard's question phase.**
  Live calls happen only during recipe execution, after the user has
  answered the questions and approved the generation step.

## Locked design decisions

| Decision | Value | Reason |
|:---|:---|:---|
| Config location | `./user-config.json` (project root) | Matches `general-legal-research` convention; easy to find and edit. |
| Personal info | None — preferences only | Mitigates accidental commit risk; user-supplied scoping is enough. |
| Precedence (standalone) | User config wins over inferred defaults | The user explicitly stated their scope; respect it. |
| Precedence (subagent) | Orchestrator classification stays primary; config is fallback | Subagent dispatch must remain orchestrator-driven for predictable token costs. |
| Knowledge generation | **Yes — recipe-driven, with mandatory source verification + human-review gate** | Option C path. Hallucination is mitigated by per-fact source URL requirement, citation auditor on output, and `[GENERATED — REQUIRES HUMAN REVIEW]` banner until lifted via `/review-knowledge`. |
| Generated dir naming | `knowledge/<industry>-<area>/` (e.g. `knowledge/fintech-regulatory/`, `knowledge/healthcare-privacy/`) | Single jurisdiction-area pair per generated dir; multi-jurisdiction handled by multiple wizard runs. |
| Recipe location | `docs/knowledge-construction-recipe.md` | Versioned, contributor-readable; same recipe drives both wizard auto-gen and human contributors. |
| Review gate | `[GENERATED — REQUIRES HUMAN REVIEW]` banner on every generated file; lifted by `/review-knowledge` after user inspection | Treats auto-generation as draft until vouched-for. |
| Citation audit on generation | Mandatory before the wizard offers the review gate | `citation-auditor` is the existing trust layer; reuse it. |

## Architecture

### File structure (after plan)

```
legal-research-agent/
  user-config.json                              # CREATE on /onboard run; gitignored
  .gitignore                                    # MODIFY: add user-config.json + reports/
  CLAUDE.md                                     # MODIFY: add Stage 0 config loading note
  README.md                                     # MODIFY: link Personal Configuration
  README.ko.md                                  # MODIFY: mirror
  templates/
    user-config.example.json                    # CREATE: schema example
  knowledge/
    onboarding/
      wizard-flow.md                            # CREATE: question catalog + selection logic
    <industry>-<area>/                          # CREATE per /onboard run (gitignored by default)
      issue-taxonomy.md                         #   Generated, banner-gated
      regulatory-map.md                         #   Generated, banner-gated
      source-map.md                             #   Generated, banner-gated
      library-index.md                          #   Generated, banner-gated
      review-status.json                        #   Gate state and audit summary
  skills/
    onboarding.md                               # CREATE: /onboard skill
    classify-research-mode.md                   # MODIFY: consult config when present
    output-mode-composition.md                  # MODIFY: default output_mode from config
    source-collection.md                        # MODIFY: jurisdiction priority + generated knowledge gating
  .claude/
    commands/
      onboard.md                                # CREATE: /onboard slash command
      review-knowledge.md                       # CREATE: /review-knowledge slash command (gate lift)
  scripts/
    check-user-config.py                        # CREATE: optional config schema validator
    check-generated-knowledge.py                # CREATE: structure + banner + frontmatter validator
    run-local-checks.py                         # MODIFY: register check_user_config + check_generated_knowledge
  tests/
    test_user_config.py                         # CREATE
    test_knowledge_construction.py              # CREATE: validates fixture generated dir
    fixtures/
      user-config/
        kr-game-only.json                       # CREATE
        kr-fintech-multi.json                   # CREATE
        en-us-corporate.json                    # CREATE
        invalid-missing-jurisdictions.json      # CREATE
      generated-knowledge/
        kr-fintech-regulatory/                  # CREATE: sample generated dir for tests
          issue-taxonomy.md                     #   With banner + frontmatter + sourced facts
          regulatory-map.md
          source-map.md
          library-index.md
          review-status.json
        invalid-missing-banner/                 # CREATE: sample missing the gate banner
          issue-taxonomy.md
          ...
  docs/
    en/how-to-use.md                            # MODIFY: add Personal Configuration section
    ko/how-to-use.md                            # MODIFY: mirror
    knowledge-construction-recipe.md            # CREATE: the recipe document
    onboarding-wizard-plan.md                   # THIS FILE
```

### `user-config.json` schema

```json
{
  "schema_version": "1.0",
  "industry": "fintech",
  "industry_freetext": null,
  "area_of_law": ["regulatory", "consumer_protection"],
  "jurisdictions": {
    "primary": ["KR"],
    "secondary": ["JP", "SG"]
  },
  "output_preferences": {
    "default_research_mode": "general",
    "default_output_mode": "comparative_matrix",
    "default_packaging": "standalone_markdown",
    "default_language": "ko"
  },
  "specialist_handoff_owners": [],
  "generated_knowledge_directories": [
    {
      "path": "knowledge/fintech-regulatory/",
      "industry": "fintech",
      "area_of_law": "regulatory",
      "jurisdiction": "KR",
      "review_status": "draft",
      "source_audit_status": "live_passed",
      "created_at": "2026-05-08",
      "lifted_at": null
    }
  ],
  "created_at": "2026-05-08",
  "updated_at": "2026-05-08"
}
```

Field semantics (schema version 1.0):

- `industry` — controlled vocabulary: `game`, `fintech`, `healthcare`,
  `platform`, `e_commerce`, `media`, `other`. When `other`,
  `industry_freetext` carries the description.
- `area_of_law` — multi-select: `general`, `regulatory`, `contract`,
  `consumer_protection`, `intellectual_property`, `employment`,
  `privacy`, `tax`, `competition`, `other`.
- `jurisdictions.primary` and `jurisdictions.secondary` — non-empty
  primary; secondary may be empty. ISO country codes.
- `output_preferences.default_research_mode` — derived from `industry`
  + `area_of_law`, but explicitly stored so the agent doesn't re-infer
  every session.
- `output_preferences.default_output_mode` — one of
  `canonical`, `executive_brief`, `comparative_matrix`,
  `enforcement_case_law`, `black_letter_commentary`.
- `output_preferences.default_packaging` — one of
  `standalone_markdown`, `handoff_packet`, `docx_ready_markdown`.
- `output_preferences.default_language` — `ko`, `en`, or `bilingual`.
- `specialist_handoff_owners` — list of agent IDs the user routinely
  co-runs.
- `generated_knowledge_directories` — list of dirs the wizard built.
  Each entry tracks `review_status` (`draft` until `/review-knowledge`
  lifts the gate, then `verified`), `source_audit_status` (one of the
  citation-auditor manifest values: `not_required`, `not_run_session_unavailable`,
  `deterministic_smoke`, `live_passed`, `live_failed`), and timestamps.
- `created_at` and `updated_at` — ISO date strings.

### Wizard question flow

The wizard asks 5 questions, each with controlled-vocabulary answers
plus an "other / free text" escape:

1. **Industry** — single-select from 7 options.
2. **Area-of-law focus** — multi-select from 10 options.
3. **Primary jurisdiction(s)** — multi-select; at least one required.
4. **Secondary jurisdictions** — optional multi-select.
5. **Output preference** — single-select with mode + packaging + language
   shortcuts.

After answers, the wizard derives `default_research_mode`, writes
`user-config.json`, and **then asks one more question**:

6. **Build a starter knowledge directory now?** (`yes` / `no` / `later`)
   - `yes` → execute the recipe per
     `docs/knowledge-construction-recipe.md`. Generation runs live
     research against official portals, writes
     `knowledge/<industry>-<area>/` files with the gate banner, runs
     citation audit, and reports the audit status.
   - `no` / `later` → skip generation; user can run `/onboard --build-knowledge`
     later or write knowledge files by hand following the recipe.

The question catalog and selection logic live in
`knowledge/onboarding/wizard-flow.md`. The recipe lives in
`docs/knowledge-construction-recipe.md`.

### Skill integration

| Skill | Change |
|:---|:---|
| `skills/classify-research-mode.md` | Stage 0: load `user-config.json`. Standalone = config primary; subagent = orchestrator primary. |
| `skills/output-mode-composition.md` | Default `output_mode` from config when request leaves it unset. |
| `skills/source-collection.md` | Jurisdiction priority from config. **Generated knowledge files are loaded only when their `review_status` is `verified`; `draft` knowledge dirs surface a `[GENERATED — DRAFT]` warning and cannot alone support high-confidence conclusions.** |

`CLAUDE.md` adds Stage 0 documentation. The agent loads
`user-config.json` (if present) before Stage 1 intake and applies the
review-gate rule for any `generated_knowledge_directories`.

## Chunk 1: Schema, example, validator, gitignore

### Task 1: Add `templates/user-config.example.json`

**Files:**

- Create: `templates/user-config.example.json`

- [ ] **Step 1: Write the example**

Use the schema above. Set `industry` to `game`, `area_of_law` to
`["regulatory", "consumer_protection"]`, `jurisdictions.primary` to
`["KR"]`, `default_research_mode` to `game_regulation`,
`default_output_mode` to `canonical`, `default_language` to `ko`. Set
`generated_knowledge_directories` to `[]` (no generation yet).

- [ ] **Step 2: Validate JSON parses cleanly**

```bash
python3 -c "import json; json.load(open('templates/user-config.example.json'))"
```

Expected: no output, exit 0.

- [ ] **Step 3: Commit**

```bash
git add templates/user-config.example.json
git commit -m "Add user-config.example.json schema sample"
```

### Task 2: Add `user-config.json` to `.gitignore`

**Files:**

- Modify: `.gitignore`

- [ ] **Step 1: Append the entry**

```
# Local user configuration (created by /onboard)
user-config.json
!templates/user-config.example.json

# Generated knowledge directories (created by /onboard --build-knowledge)
# Tracked dirs are listed in user-config.json's generated_knowledge_directories.
# By default they are gitignored; remove specific paths from the ignore list
# only when intentionally committing reviewed knowledge to share.
knowledge/*-*/
!knowledge/game-regulation/
!knowledge/general/
!knowledge/legal-writing/
!knowledge/onboarding/
!knowledge/output-modes/
```

The negation lines preserve the hand-curated knowledge directories
that already exist in the repo. New `<industry>-<area>` dirs created
by the wizard are gitignored by default; the user moves them out of
the ignore list when ready to share.

- [ ] **Step 2: Verify**

```bash
echo '{"test":1}' > user-config.json
git status --short user-config.json
rm user-config.json
mkdir -p knowledge/test-fixture-area
git status --short knowledge/test-fixture-area
rm -rf knowledge/test-fixture-area
```

Expected: empty output for both checks (file and directory ignored).

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "Gitignore user-config.json and generated knowledge dirs"
```

### Task 3: Add `scripts/check-user-config.py`

**Files:**

- Create: `scripts/check-user-config.py`

The validator is **optional** — it runs only if `user-config.json`
exists. The local preflight passes when the file is absent.

- [ ] **Step 1: Write the script**

```python
#!/usr/bin/env python3
"""Validate user-config.json schema when the file is present.

This validator is intentionally tolerant: if user-config.json does not
exist, the script exits 0 and prints a SKIP line. The file is
gitignored runtime state created by the /onboard wizard.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ALLOWED_INDUSTRIES = {
    "game", "fintech", "healthcare", "platform",
    "e_commerce", "media", "other",
}
ALLOWED_AREAS = {
    "general", "regulatory", "contract", "consumer_protection",
    "intellectual_property", "employment", "privacy", "tax",
    "competition", "other",
}
ALLOWED_RESEARCH_MODES = {
    "general", "game_regulation", "game_plus_general", "fallback",
}
ALLOWED_OUTPUT_MODES = {
    "canonical", "executive_brief", "comparative_matrix",
    "enforcement_case_law", "black_letter_commentary",
}
ALLOWED_PACKAGING = {
    "standalone_markdown", "handoff_packet", "docx_ready_markdown",
}
ALLOWED_LANGUAGES = {"ko", "en", "bilingual"}
ALLOWED_REVIEW_STATUSES = {"draft", "verified"}
ALLOWED_AUDIT_STATUSES = {
    "not_required", "not_run_session_unavailable",
    "deterministic_smoke", "live_passed", "live_failed",
}


def validate(data: dict) -> list[str]:
    errors: list[str] = []

    if data.get("schema_version") != "1.0":
        errors.append(f"schema_version must be '1.0' (got {data.get('schema_version')!r})")

    industry = data.get("industry")
    if industry not in ALLOWED_INDUSTRIES:
        errors.append(f"industry must be one of {sorted(ALLOWED_INDUSTRIES)} (got {industry!r})")

    if industry == "other" and not data.get("industry_freetext"):
        errors.append("industry_freetext is required when industry is 'other'")

    areas = data.get("area_of_law", [])
    if not isinstance(areas, list) or not areas:
        errors.append("area_of_law must be a non-empty list")
    else:
        for area in areas:
            if area not in ALLOWED_AREAS:
                errors.append(f"area_of_law contains invalid value {area!r}")

    jurisdictions = data.get("jurisdictions", {})
    primary = jurisdictions.get("primary", [])
    if not isinstance(primary, list) or not primary:
        errors.append("jurisdictions.primary must be a non-empty list")

    secondary = jurisdictions.get("secondary", [])
    if not isinstance(secondary, list):
        errors.append("jurisdictions.secondary must be a list (may be empty)")

    prefs = data.get("output_preferences", {})
    if prefs.get("default_research_mode") not in ALLOWED_RESEARCH_MODES:
        errors.append(
            f"output_preferences.default_research_mode must be one of "
            f"{sorted(ALLOWED_RESEARCH_MODES)} "
            f"(got {prefs.get('default_research_mode')!r})"
        )
    if prefs.get("default_output_mode") not in ALLOWED_OUTPUT_MODES:
        errors.append(
            f"output_preferences.default_output_mode must be one of "
            f"{sorted(ALLOWED_OUTPUT_MODES)} "
            f"(got {prefs.get('default_output_mode')!r})"
        )
    if prefs.get("default_packaging") not in ALLOWED_PACKAGING:
        errors.append(
            f"output_preferences.default_packaging must be one of "
            f"{sorted(ALLOWED_PACKAGING)} "
            f"(got {prefs.get('default_packaging')!r})"
        )
    if prefs.get("default_language") not in ALLOWED_LANGUAGES:
        errors.append(
            f"output_preferences.default_language must be one of "
            f"{sorted(ALLOWED_LANGUAGES)} "
            f"(got {prefs.get('default_language')!r})"
        )

    handoff_owners = data.get("specialist_handoff_owners", [])
    if not isinstance(handoff_owners, list):
        errors.append("specialist_handoff_owners must be a list")

    generated = data.get("generated_knowledge_directories", [])
    if not isinstance(generated, list):
        errors.append("generated_knowledge_directories must be a list")
    else:
        for i, entry in enumerate(generated):
            prefix = f"generated_knowledge_directories[{i}]"
            if not isinstance(entry, dict):
                errors.append(f"{prefix} must be an object")
                continue
            if not isinstance(entry.get("path"), str) or not entry["path"]:
                errors.append(f"{prefix}.path must be a non-empty string")
            if entry.get("review_status") not in ALLOWED_REVIEW_STATUSES:
                errors.append(
                    f"{prefix}.review_status must be one of "
                    f"{sorted(ALLOWED_REVIEW_STATUSES)} "
                    f"(got {entry.get('review_status')!r})"
                )
            if entry.get("source_audit_status") not in ALLOWED_AUDIT_STATUSES:
                errors.append(
                    f"{prefix}.source_audit_status must be one of "
                    f"{sorted(ALLOWED_AUDIT_STATUSES)} "
                    f"(got {entry.get('source_audit_status')!r})"
                )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to a specific config file (default: <root>/user-config.json).",
    )
    args = parser.parse_args(argv)

    config_path = args.config or (args.root / "user-config.json")
    if not config_path.exists():
        print(f"SKIP: {config_path} not present (fresh clone or pre-onboard)")
        return 0

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: {config_path}: invalid JSON ({exc})", file=sys.stderr)
        return 1

    errors = validate(data)
    if errors:
        for line in errors:
            print(f"FAIL: {config_path}: {line}", file=sys.stderr)
        return 1

    print(f"OK: {config_path} valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Verify the example passes**

```bash
python3 scripts/check-user-config.py --config templates/user-config.example.json
```

Expected: `OK: templates/user-config.example.json valid`.

- [ ] **Step 3: Verify the absent-file case**

```bash
python3 scripts/check-user-config.py
```

Expected: `SKIP: …/user-config.json not present (fresh clone or pre-onboard)`,
exit 0.

- [ ] **Step 4: Commit**

```bash
git add scripts/check-user-config.py
git commit -m "Add user-config schema validator (skips when file absent)"
```

### Task 4: Add unit test + invalid fixtures

**Files:**

- Create: `tests/test_user_config.py`
- Create: `tests/fixtures/user-config/kr-game-only.json`
- Create: `tests/fixtures/user-config/kr-fintech-multi.json`
- Create: `tests/fixtures/user-config/en-us-corporate.json`
- Create: `tests/fixtures/user-config/invalid-missing-jurisdictions.json`

- [ ] **Step 1: Write the three valid fixtures**

`kr-game-only.json` — minimal KR game preference, no generated knowledge.

`kr-fintech-multi.json` — KR fintech, KR primary + JP/SG secondary,
with one entry in `generated_knowledge_directories` showing
`review_status: "draft"` and `source_audit_status: "live_passed"`.

`en-us-corporate.json` — `industry: other` with freetext, US primary +
EU secondary, English output, no generated knowledge.

(Schema example matches the example in the Architecture section above.)

- [ ] **Step 2: Write the invalid fixture**

`invalid-missing-jurisdictions.json` — primary list empty.

- [ ] **Step 3: Write the test**

```python
#!/usr/bin/env python3
"""Validate user-config schema fixtures."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = REPO_ROOT / "scripts" / "check-user-config.py"


def _run(config: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), "--config", str(config)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class UserConfigTest(unittest.TestCase):
    def test_skip_when_absent(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECK_SCRIPT), "--config", "/nonexistent/user-config.json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("SKIP", result.stdout)

    def test_example_valid(self) -> None:
        result = _run(REPO_ROOT / "templates" / "user-config.example.json")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_valid_fixtures_pass(self) -> None:
        for name in ("kr-game-only.json", "kr-fintech-multi.json", "en-us-corporate.json"):
            with self.subTest(fixture=name):
                result = _run(REPO_ROOT / "tests" / "fixtures" / "user-config" / name)
                self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_invalid_fixture_fails(self) -> None:
        result = _run(REPO_ROOT / "tests" / "fixtures" / "user-config" / "invalid-missing-jurisdictions.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("primary must be a non-empty list", result.stderr)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run the test**

```bash
python3 tests/test_user_config.py
```

Expected: 4 tests, all PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_user_config.py tests/fixtures/user-config/
git commit -m "Add user-config schema fixtures and validator tests"
```

### Task 5: Register validator in `run-local-checks.py`

**Files:**

- Modify: `scripts/run-local-checks.py`

- [ ] **Step 1: Add the entry**

Insert next to other `check-*.py` entries:

```python
{
    "id": "user_config",
    "description": "Validate user-config.json schema when the file is present.",
    "cmd": ["python3", "scripts/check-user-config.py"],
},
```

- [ ] **Step 2: Run the preflight**

```bash
python3 scripts/run-local-checks.py
```

Expected: `user_config: PASS` (skips because the file is absent on a
clean repo). Total now 22/22.

- [ ] **Step 3: Commit**

```bash
git add scripts/run-local-checks.py
git commit -m "Register user-config validator in local preflight"
```

## Chunk 2: Wizard skill, slash command, knowledge file

### Task 6: Add `knowledge/onboarding/wizard-flow.md`

**Files:**

- Create: `knowledge/onboarding/wizard-flow.md`

This file is the **question catalog**, kept separate from the skill body
so future contributors can adjust the vocabulary without touching skill
instructions.

- [ ] **Step 1: Write the catalog**

Required sections:

- `## Question 1 — Industry` with the 7 controlled values
- `## Question 2 — Area of law focus` with the 10 controlled values
- `## Question 3 — Primary jurisdictions`
- `## Question 4 — Secondary jurisdictions`
- `## Question 5 — Output preference` with 3-5 shortcut bundles
- `## Question 6 — Build starter knowledge directory now?`
  (`yes` / `no` / `later`; `yes` triggers recipe execution)
- `## Derivation rules` — `default_research_mode` from `industry` +
  `area_of_law`
- `## Skip rules` — when secondary jurisdictions can be skipped, when
  the wizard short-circuits if `user-config.json` already exists

Cross-link the controlled-vocabulary lists to the matching values in
`scripts/check-user-config.py` so the validator and wizard never drift.

- [ ] **Step 2: Commit**

```bash
git add knowledge/onboarding/wizard-flow.md
git commit -m "Add onboarding wizard question catalog"
```

### Task 7: Add `skills/onboarding.md`

**Files:**

- Create: `skills/onboarding.md`

- [ ] **Step 1: Write the skill**

Frontmatter follows the existing convention (`name`, `description`,
`disable-model-invocation: true`). Body covers:

- Inputs: existing `user-config.json` (offer to update vs. replace),
  question catalog from `knowledge/onboarding/wizard-flow.md`,
  recipe document from `docs/knowledge-construction-recipe.md`.
- Workflow: load existing config if present → run questions →
  derive defaults → write `user-config.json` → run
  `check-user-config.py` → optionally execute recipe (Question 6
  branch) → update config with `generated_knowledge_directories`
  entry.
- Quality floor: never invent industry or area-of-law values; never
  collect personal identifiers; never write the config until every
  required question is answered.
- Precedence rules: standalone vs. subagent (per Locked design
  decisions above).

Note: the recipe-execution step **does not** belong in this skill body
in detail. The skill calls into the recipe document; recipe specifics
are owned by `docs/knowledge-construction-recipe.md` (created in
Chunk 3).

- [ ] **Step 2: Run the conventions check**

```bash
python3 scripts/check-claude-conventions.py
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add skills/onboarding.md
git commit -m "Add /onboard wizard skill"
```

### Task 8: Add `.claude/commands/onboard.md`

**Files:**

- Create: `.claude/commands/onboard.md`

- [ ] **Step 1: Write the slash command**

```markdown
---
description: Run the onboarding wizard to create or update user-config.json with industry, area-of-law, jurisdictions, and output preferences. Optionally builds a starter knowledge directory.
argument-hint: "[--reset] [--build-knowledge] [--skip-knowledge]"
---

Apply `skills/onboarding.md`.

Argument handling:

- `--reset`: replace any existing `user-config.json` after confirmation.
- `--build-knowledge`: run the recipe-driven knowledge construction
  step even if Question 6 was previously answered `no` or `later`.
- `--skip-knowledge`: run the wizard but skip Question 6; useful when
  the user just wants to refresh preferences.

After the wizard finishes, summarize the active config (industry,
primary jurisdictions, default output mode, language) and (when a
knowledge directory was built) the audit status. Remind the user
that `user-config.json` is gitignored.
```

- [ ] **Step 2: Run the conventions check**

```bash
python3 scripts/check-claude-conventions.py
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/onboard.md
git commit -m "Add /onboard slash command with --build-knowledge flag"
```

## Chunk 3: Knowledge construction recipe document

### Task 9: Write `docs/knowledge-construction-recipe.md`

**Files:**

- Create: `docs/knowledge-construction-recipe.md`

The recipe is the single source of truth for "how to build a
`knowledge/<industry>-<area>/` directory." It is read by both human
contributors and the wizard's agent execution.

- [ ] **Step 1: Write the recipe**

Required sections (validator-enforced in Task 11):

```markdown
# Knowledge Construction Recipe

## Status and Audience

Canonical recipe for building `knowledge/<industry>-<area>/`
directories — used by `/onboard --build-knowledge` and by human
contributors writing knowledge by hand.

## Required Files

Every `knowledge/<industry>-<area>/` directory must contain four
Markdown files plus one JSON gate file:

- `issue-taxonomy.md`
- `regulatory-map.md`
- `source-map.md`
- `library-index.md`
- `review-status.json`

## Per-File Structure

### `issue-taxonomy.md`
- Banner block (see Verification Metadata).
- YAML frontmatter (industry, area_of_law, jurisdiction, recipe_version).
- `## Issue Categories` section with at least 5 categories specific to
  the industry-area pair.
- For each category: scope sentence, key sub-issues, applicable
  output_mode default, source URL or `[Unverified]` for any
  jurisdiction-specific reference.

### `regulatory-map.md`
- Banner block + frontmatter.
- `## Regulators` section listing each regulator with name (verbatim
  from official source), official URL, jurisdiction, scope of
  authority, and a source URL backing the entry.
- `## Statutes and Rules` section listing controlling statutes and
  delegated rules with citation, effective date (when verifiable), and
  source URL.

### `source-map.md`
- Banner block + frontmatter.
- `## Primary Sources` section listing official portals, statute
  databases, and case databases for the jurisdiction-area pair.
- `## Secondary Sources` section listing trusted commentary, regulator
  press release feeds, and practitioner publications.
- Every source has a Grade (A-D per the project's existing source
  grading vocabulary) and a source URL.

### `library-index.md`
- Banner block + frontmatter.
- `## Index` section. Empty list is acceptable when no library files
  have been ingested yet.

### `review-status.json`
- Tracks the gate state and audit summary:

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

## Verification Metadata

### Banner block

The first line of every generated `.md` file is a banner that the
agent's source-collection skill recognizes as a draft gate:

```
> **[GENERATED — REQUIRES HUMAN REVIEW]** This file was built by the
> /onboard wizard from live research. Lift the gate with
> `/review-knowledge knowledge/<industry>-<area>/` after editing.
```

When the user lifts the gate, the banner is replaced with:

```
> **[VERIFIED]** Reviewed on YYYY-MM-DD by the user.
```

### YAML frontmatter

```yaml
---
industry: fintech
area_of_law: regulatory
jurisdiction: KR
recipe_version: 1.0
generated_at: 2026-05-08
verification_status: draft
sources:
  - url: https://...
    grade: A
    accessed_at: 2026-05-08
---
```

The `sources` array lists every URL the agent fetched while building
this file. Each fact in the body must reference at least one entry
from this array.

## Live-Research Protocol

Per file, in this run order:

1. **`source-map.md` first.** The wizard's first task is to enumerate
   official portals for the jurisdiction-area pair. This builds the
   source registry that subsequent files will draw from.
   - For `jurisdiction: KR`, prefer `mcp__claude_ai_Korean-law__*`
     tool calls over `WebFetch`.
   - For other jurisdictions, use `WebFetch` against whitelisted
     official portals (`law.go.kr`, `eur-lex.europa.eu`, `congress.gov`,
     `legislation.gov.uk`, `laws-lois.justice.gc.ca`, etc.).
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
   Each fact must record the source URL it came from.
3. **`issue-taxonomy.md`.** Using both prior files, enumerate at
   least 5 issue categories specific to the industry-area pair.
   Examples: for `fintech-regulatory` in KR, categories like "Virtual
   asset custody", "Lending platform licensing", "AML/KYC compliance",
   "Consumer credit consumer protection", "Algorithmic trading
   oversight". For each category, identify:
   - Scope (one paragraph)
   - Key sub-issues (bullet list)
   - Default output_mode (e.g., `executive_brief` for compliance
     overviews, `comparative_matrix` for cross-jurisdiction work)
   - At least one source URL backing the category's existence.
4. **`library-index.md`.** Empty `## Index` is acceptable.
5. **`review-status.json`.** After all four `.md` files are generated,
   write `review-status.json` with `review_status: "draft"`,
   counts of verified vs. unverified facts, and `source_audit_status`
   set after the citation auditor runs.

## Hallucination Mitigation Rules

Mandatory rules for both human contributors and the wizard:

- **Every fact is sourced.** Regulator names, statute numbers, and
  effective dates always cite a source URL. Any fact without a source
  is marked `[Unverified]` inline.
- **Cite verbatim.** Regulator names and statute citations come
  verbatim from the source — no paraphrasing the regulator's name.
- **Date format.** Effective dates use ISO `YYYY-MM-DD` and only when
  the source explicitly states the date; otherwise `[Effective date
  unverified]`.
- **No primary-law text generation.** This recipe builds metadata
  (regulator names, statute citations, source URLs). It does not write
  out statute text. For statute text, the agent fetches the source
  live during research runs.
- **Citation audit before review.** After all files are generated,
  the wizard runs the vendored `citation-auditor` over the directory.
  The audit's per-claim verdicts populate `audit_summary` in
  `review-status.json`.
- **Banner gate.** Files always start with the banner; the gate is
  lifted only by `/review-knowledge`.

## Run Order

```
source-map.md → regulatory-map.md → issue-taxonomy.md → library-index.md → review-status.json
```

The wizard runs the citation auditor as the last step before
reporting back to the user.

## Recipe Version

`1.0` (this document). Version is recorded in each generated file's
frontmatter so future recipe upgrades can identify and migrate older
generated directories.
```

- [ ] **Step 2: Commit**

```bash
git add docs/knowledge-construction-recipe.md
git commit -m "Add knowledge construction recipe document (v1.0)"
```

### Task 10: Add `scripts/check-generated-knowledge.py`

**Files:**

- Create: `scripts/check-generated-knowledge.py`

The validator enforces the recipe's structural requirements on any
generated `knowledge/<industry>-<area>/` directory. It is **optional**
— it runs only when the directory exists.

- [ ] **Step 1: Write the script**

```python
#!/usr/bin/env python3
"""Validate generated knowledge directories against the construction recipe.

Skips when no generated directories exist. Validates:
- All four required Markdown files present
- review-status.json present and valid
- Banner block on every Markdown file
- YAML frontmatter with required fields
- Recipe version compatibility
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_MARKDOWN_FILES = [
    "issue-taxonomy.md",
    "regulatory-map.md",
    "source-map.md",
    "library-index.md",
]
REQUIRED_REVIEW_STATUS_FIELDS = {
    "industry", "area_of_law", "jurisdiction",
    "review_status", "source_audit_status",
    "created_at", "recipe_version",
}
ALLOWED_REVIEW_STATUSES = {"draft", "verified"}
ALLOWED_AUDIT_STATUSES = {
    "not_required", "not_run_session_unavailable",
    "deterministic_smoke", "live_passed", "live_failed",
}
RECIPE_SUPPORTED_VERSIONS = {"1.0"}

DRAFT_BANNER = re.compile(
    r">\s*\*\*\[GENERATED\s+—\s+REQUIRES HUMAN REVIEW\]\*\*"
)
VERIFIED_BANNER = re.compile(
    r">\s*\*\*\[VERIFIED\]\*\*"
)
FRONTMATTER_DELIMITER = "---"
REQUIRED_FRONTMATTER_FIELDS = {
    "industry", "area_of_law", "jurisdiction",
    "recipe_version", "generated_at", "verification_status",
}


def find_generated_dirs(root: Path) -> list[Path]:
    """Find any knowledge/<dash-separated-pair>/ directory."""
    knowledge = root / "knowledge"
    if not knowledge.is_dir():
        return []
    candidates: list[Path] = []
    for child in sorted(knowledge.iterdir()):
        if not child.is_dir():
            continue
        # Skip hand-curated and infrastructure dirs
        if child.name in {"game-regulation", "general", "legal-writing",
                          "onboarding", "output-modes"}:
            continue
        # Generated dirs follow <industry>-<area> naming
        if "-" in child.name:
            candidates.append(child)
    return candidates


def parse_frontmatter(path: Path) -> tuple[str, dict[str, str]]:
    """Return (banner_line, frontmatter_dict)."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    banner_line = lines[0] if lines else ""
    frontmatter: dict[str, str] = {}
    in_fm = False
    for line in lines:
        stripped = line.strip()
        if stripped == FRONTMATTER_DELIMITER:
            if in_fm:
                break
            in_fm = True
            continue
        if in_fm and ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip()
    return banner_line, frontmatter


def validate_dir(path: Path) -> list[str]:
    errors: list[str] = []

    for required in REQUIRED_MARKDOWN_FILES:
        if not (path / required).exists():
            errors.append(f"{path}: missing required file {required}")

    review_path = path / "review-status.json"
    if not review_path.exists():
        errors.append(f"{path}: missing review-status.json")
        return errors

    try:
        review = json.loads(review_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{review_path}: invalid JSON ({exc})")
        return errors

    missing_fields = REQUIRED_REVIEW_STATUS_FIELDS - set(review)
    if missing_fields:
        errors.append(
            f"{review_path}: missing fields {sorted(missing_fields)}"
        )

    if review.get("review_status") not in ALLOWED_REVIEW_STATUSES:
        errors.append(
            f"{review_path}: review_status must be one of "
            f"{sorted(ALLOWED_REVIEW_STATUSES)} "
            f"(got {review.get('review_status')!r})"
        )

    if review.get("source_audit_status") not in ALLOWED_AUDIT_STATUSES:
        errors.append(
            f"{review_path}: source_audit_status must be one of "
            f"{sorted(ALLOWED_AUDIT_STATUSES)} "
            f"(got {review.get('source_audit_status')!r})"
        )

    if review.get("recipe_version") not in RECIPE_SUPPORTED_VERSIONS:
        errors.append(
            f"{review_path}: recipe_version must be one of "
            f"{sorted(RECIPE_SUPPORTED_VERSIONS)} "
            f"(got {review.get('recipe_version')!r})"
        )

    expected_banner = (
        DRAFT_BANNER if review.get("review_status") == "draft"
        else VERIFIED_BANNER
    )

    for md_name in REQUIRED_MARKDOWN_FILES:
        md_path = path / md_name
        if not md_path.exists():
            continue
        banner_line, frontmatter = parse_frontmatter(md_path)
        if not expected_banner.search(banner_line):
            errors.append(
                f"{md_path}: missing or wrong banner for "
                f"review_status={review.get('review_status')!r} "
                f"(got {banner_line!r})"
            )
        missing_fm = REQUIRED_FRONTMATTER_FIELDS - set(frontmatter)
        if missing_fm:
            errors.append(
                f"{md_path}: frontmatter missing fields {sorted(missing_fm)}"
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)

    dirs = find_generated_dirs(args.root)
    if not dirs:
        print("SKIP: no generated knowledge directories present")
        return 0

    all_errors: list[str] = []
    for d in dirs:
        all_errors.extend(validate_dir(d))

    if all_errors:
        for line in all_errors:
            print(f"FAIL: {line}", file=sys.stderr)
        return 1

    print(f"OK: {len(dirs)} generated knowledge directory/directories valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Verify the absent-file case**

```bash
python3 scripts/check-generated-knowledge.py
```

Expected: `SKIP: no generated knowledge directories present`, exit 0.

- [ ] **Step 3: Commit**

```bash
git add scripts/check-generated-knowledge.py
git commit -m "Add generated-knowledge structure validator"
```

### Task 11: Add fixtures and unit test

**Files:**

- Create: `tests/fixtures/generated-knowledge/kr-fintech-regulatory/`
  with all 4 `.md` files + `review-status.json` (valid sample)
- Create: `tests/fixtures/generated-knowledge/invalid-missing-banner/`
  (sample missing the gate banner on `regulatory-map.md`)
- Create: `tests/test_knowledge_construction.py`

- [ ] **Step 1: Write the valid fixture**

`kr-fintech-regulatory/issue-taxonomy.md` starts with the draft banner
and has frontmatter with all 6 required fields. Body has at least 5
issue categories per the recipe. Each category cites a source URL.

`regulatory-map.md`, `source-map.md`, `library-index.md` follow the
same pattern. `library-index.md` may have an empty `## Index` section.

`review-status.json`:

```json
{
  "industry": "fintech",
  "area_of_law": "regulatory",
  "jurisdiction": "KR",
  "review_status": "draft",
  "source_audit_status": "live_passed",
  "audit_summary": {
    "total_facts": 18,
    "verified_facts": 17,
    "unverified_facts": 1
  },
  "created_at": "2026-05-08",
  "lifted_at": null,
  "recipe_version": "1.0"
}
```

- [ ] **Step 2: Write the invalid fixture**

`invalid-missing-banner/regulatory-map.md` starts with `# Regulatory
Map` (no banner). Other files in the dir are valid. The validator
must surface the missing-banner error specifically for that file.

Important: the script's `find_generated_dirs` finds dirs under
`knowledge/`, not `tests/fixtures/`. To exercise the script in tests,
the test will pass `--root` pointing at a temporary directory that
contains a `knowledge/` subtree mirroring the fixture.

Alternative: add a helper in `check-generated-knowledge.py` that
accepts an explicit list of directories via `--dir`. Easier.

Add to the script:

```python
parser.add_argument(
    "--dir",
    action="append",
    type=Path,
    default=[],
    help="Validate the named directory instead of auto-discovering. May be repeated.",
)
```

And:

```python
dirs = list(args.dir) if args.dir else find_generated_dirs(args.root)
```

Then test calls `--dir tests/fixtures/generated-knowledge/kr-fintech-regulatory/`.

- [ ] **Step 3: Write the test**

```python
#!/usr/bin/env python3
"""Validate generated-knowledge fixtures."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = REPO_ROOT / "scripts" / "check-generated-knowledge.py"


def _run(*dirs: Path) -> subprocess.CompletedProcess:
    args = [sys.executable, str(CHECK_SCRIPT)]
    for d in dirs:
        args.extend(["--dir", str(d)])
    return subprocess.run(
        args, cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )


class GeneratedKnowledgeTest(unittest.TestCase):
    def test_skip_when_absent(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECK_SCRIPT), "--root", "/nonexistent"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("SKIP", result.stdout)

    def test_valid_fixture_passes(self) -> None:
        fixture = REPO_ROOT / "tests" / "fixtures" / "generated-knowledge" / "kr-fintech-regulatory"
        result = _run(fixture)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_missing_banner_fixture_fails(self) -> None:
        fixture = REPO_ROOT / "tests" / "fixtures" / "generated-knowledge" / "invalid-missing-banner"
        result = _run(fixture)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing or wrong banner", result.stderr)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run the test**

```bash
python3 tests/test_knowledge_construction.py
```

Expected: 3 tests, all PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/generated-knowledge/ tests/test_knowledge_construction.py scripts/check-generated-knowledge.py
git commit -m "Add generated-knowledge fixtures and unit tests"
```

### Task 12: Register the new validator in `run-local-checks.py`

**Files:**

- Modify: `scripts/run-local-checks.py`

- [ ] **Step 1: Add the entry**

```python
{
    "id": "generated_knowledge",
    "description": "Validate generated knowledge directories against the construction recipe (skips when none exist).",
    "cmd": ["python3", "scripts/check-generated-knowledge.py"],
},
```

- [ ] **Step 2: Run preflight**

```bash
python3 scripts/run-local-checks.py
```

Expected: 23/23 PASS (existing 22 + new `generated_knowledge`).

- [ ] **Step 3: Commit**

```bash
git add scripts/run-local-checks.py
git commit -m "Register generated-knowledge validator in local preflight"
```

## Chunk 4: Wizard knowledge generation flow

### Task 13: Extend `skills/onboarding.md` with recipe execution

**Files:**

- Modify: `skills/onboarding.md`

- [ ] **Step 1: Add the recipe-execution section**

Append to the skill body, before the precedence section:

```markdown
## Knowledge Construction (Question 6 = `yes`)

When the user answers `yes` to Question 6 (or runs
`/onboard --build-knowledge`), execute the recipe in
`docs/knowledge-construction-recipe.md` for the chosen
`industry`-`area_of_law`-`jurisdiction` triple.

Steps:

1. Compute the directory name as `<industry>-<area>` (snake-case the
   area slug). For multi-area users, generate one dir per area.
2. Verify the directory does not already exist. If it does, ask
   whether to replace, skip, or keep both with a numeric suffix.
3. Apply the recipe's run order: `source-map.md` →
   `regulatory-map.md` → `issue-taxonomy.md` → `library-index.md` →
   `review-status.json`.
4. Per file, follow the recipe's live-research protocol. Use
   `mcp__claude_ai_Korean-law__*` for KR; `WebFetch` against
   whitelisted official portals for other jurisdictions.
5. Apply the hallucination mitigation rules. Every regulator name and
   statute citation cites a source URL. Unverifiable facts are marked
   `[Unverified]` inline.
6. Add the draft banner block as the first line of every `.md` file.
7. After all files are generated, run the vendored
   `citation-auditor` over the directory:

   ```bash
   /audit knowledge/<industry>-<area>/
   ```

   Record the per-claim verdict counts in `audit_summary` in
   `review-status.json`.
8. Run `python3 scripts/check-generated-knowledge.py` to verify
   structural conformance. If it fails, surface the errors and roll
   back the directory write.
9. Append a new entry to `user-config.json`'s
   `generated_knowledge_directories` list with `review_status: "draft"`,
   `source_audit_status` from step 7, and timestamps.
10. Print a one-paragraph summary that mentions:
    - the directory path,
    - the audit summary (verified vs. unverified facts),
    - the `[GENERATED — REQUIRES HUMAN REVIEW]` gate,
    - the `/review-knowledge <path>` command to lift the gate.
```

- [ ] **Step 2: Run conventions + knowledge-coverage**

```bash
python3 scripts/check-claude-conventions.py
python3 scripts/check-knowledge-coverage.py
```

Expected: both PASS.

- [ ] **Step 3: Commit**

```bash
git add skills/onboarding.md
git commit -m "Wire recipe execution into onboarding skill"
```

### Task 14: Add `/review-knowledge` slash command

**Files:**

- Create: `.claude/commands/review-knowledge.md`

- [ ] **Step 1: Write the slash command**

```markdown
---
description: Lift the [GENERATED — REQUIRES HUMAN REVIEW] gate on a generated knowledge directory after the user has reviewed and (optionally) edited the contents.
argument-hint: "<path/to/knowledge-dir/>"
---

The user has reviewed (and possibly edited) the generated knowledge
directory in `$ARGUMENTS`. Lift the gate as follows:

1. Confirm the path exists and contains a `review-status.json`.
2. Show the user the current `audit_summary` and ask for explicit
   confirmation that they have verified the content.
3. On confirmation:
   - Replace the `[GENERATED — REQUIRES HUMAN REVIEW]` banner on every
     `.md` file with `[VERIFIED] Reviewed on YYYY-MM-DD by the user.`
   - Update `review-status.json`: set `review_status: "verified"` and
     `lifted_at` to today's date.
   - Update `user-config.json`'s matching
     `generated_knowledge_directories` entry to `review_status: "verified"`.
4. Run `python3 scripts/check-generated-knowledge.py --dir <path>` to
   verify the post-lift state.

Do not proceed if any required `.md` file is missing or if the
`review-status.json` cannot be parsed. Tell the user what to fix.
```

- [ ] **Step 2: Run the conventions check**

```bash
python3 scripts/check-claude-conventions.py
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/review-knowledge.md
git commit -m "Add /review-knowledge slash command"
```

### Task 15: Update `skills/source-collection.md` with the gate-aware loading rule

**Files:**

- Modify: `skills/source-collection.md`

- [ ] **Step 1: Add the gate rule**

Append a new section after the User Config Jurisdiction Priority
section (added in the original Chunk 3 of this plan):

```markdown
## Generated Knowledge Gate

Generated knowledge directories listed in `user-config.json`'s
`generated_knowledge_directories` are loaded with awareness of their
`review_status`:

- `verified` (gate lifted via `/review-knowledge`): treat the
  directory like a hand-curated `knowledge/<area>/` directory.
  Sources cited from these files inherit the grade declared in
  the file's frontmatter.
- `draft` (gate not lifted): the directory may be loaded for
  structural orientation only. Sources cited from `draft` files
  cannot alone support a high-confidence conclusion. Surface a
  `[GENERATED — DRAFT]` warning in `coverage_gaps` whenever a
  `draft` knowledge file is the controlling reference for a
  material proposition.

The `/onboard --build-knowledge` workflow always writes new
directories with `review_status: "draft"`. The user explicitly
lifts the gate after reviewing the content.
```

- [ ] **Step 2: Run the knowledge-coverage check**

```bash
python3 scripts/check-knowledge-coverage.py
```

Expected: PASS (existing markers preserved).

- [ ] **Step 3: Commit**

```bash
git add skills/source-collection.md
git commit -m "Document generated-knowledge gate in source-collection"
```

### Task 16: Update `user-config.json` schema test with generated-knowledge entry

**Files:**

- Modify: `tests/fixtures/user-config/kr-fintech-multi.json`
- Modify: `tests/test_user_config.py`

- [ ] **Step 1: Confirm the kr-fintech-multi fixture has a generated dir entry**

(Was added in Task 4 already; this step verifies it post-Chunk-3.)

- [ ] **Step 2: Add a test asserting the entry parses through**

```python
def test_fixture_with_generated_dir_parses(self) -> None:
    import json
    fixture = REPO_ROOT / "tests" / "fixtures" / "user-config" / "kr-fintech-multi.json"
    data = json.loads(fixture.read_text(encoding="utf-8"))
    self.assertEqual(len(data["generated_knowledge_directories"]), 1)
    entry = data["generated_knowledge_directories"][0]
    self.assertEqual(entry["review_status"], "draft")
    self.assertEqual(entry["source_audit_status"], "live_passed")
```

- [ ] **Step 3: Run tests**

```bash
python3 tests/test_user_config.py
```

Expected: 5 tests, all PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_user_config.py
git commit -m "Test fixture-level generated_knowledge_directories parsing"
```

## Chunk 5: Skill integration (config-aware behavior)

### Task 17: Stage 0 in CLAUDE.md

**Files:**

- Modify: `CLAUDE.md`

- [ ] **Step 1: Insert Stage 0 paragraph**

Insert a `## Stage 0: User Configuration` section between
`## Prerequisites` and `## Operating Rules`:

```markdown
## Stage 0: User Configuration

If `user-config.json` exists at the project root, load it before
Stage 1 intake. Use it as the default source for research mode,
jurisdictions, output mode, packaging, and language.

- **Standalone use:** the config defaults are primary. The user's
  per-question overrides still win.
- **Subagent dispatch:** orchestrator classification stays primary
  per `Operating Rules`. The config fills only fields the
  orchestrator did not specify.

If `user-config.json` lists `generated_knowledge_directories`, load
each one according to its `review_status` (per
`skills/source-collection.md`'s Generated Knowledge Gate rule):
`verified` dirs are treated like hand-curated knowledge; `draft`
dirs surface a `[GENERATED — DRAFT]` warning whenever they are the
controlling reference for a material proposition.

If `user-config.json` is missing on standalone use and the user has
not declared their scope inline, suggest running `/onboard`. Do not
require it — the agent must continue to work without a config when
the user asks a one-off question.
```

- [ ] **Step 2: Run the knowledge-coverage check**

```bash
python3 scripts/check-knowledge-coverage.py
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "Add Stage 0 user-config loading and gate awareness to CLAUDE.md"
```

### Task 18: `classify-research-mode.md` consults config

**Files:**

- Modify: `skills/classify-research-mode.md`

- [ ] **Step 1: Insert the precedence note** (per the original plan
  text)

```markdown
## User Config Precedence

When `user-config.json` is present and the run is standalone:

1. If the user-supplied question explicitly names a research mode,
   use it.
2. Else if `output_preferences.default_research_mode` is set in the
   config, use it as the starting hypothesis.
3. Else self-classify per the rules above.

When the run is a subagent dispatch (orchestrator-supplied intake
payload), the existing rules apply — `user-config.json` is ignored
because the orchestrator owns classification.

If the config-suggested mode is inconsistent with the question facts,
record `classification_warnings: ["config_mismatch"]` and continue
with the routed mode rather than silently switching.
```

- [ ] **Step 2: Run conventions + knowledge-coverage**

```bash
python3 scripts/check-claude-conventions.py
python3 scripts/check-knowledge-coverage.py
```

Expected: both PASS.

- [ ] **Step 3: Commit**

```bash
git add skills/classify-research-mode.md
git commit -m "Wire user-config defaults into classify-research-mode"
```

### Task 19: `output-mode-composition.md` consults config

**Files:**

- Modify: `skills/output-mode-composition.md`

- [ ] **Step 1: Insert the config-default note**

In the existing `## Inputs` section, append:

```markdown
- When `output_mode` is unset on the request and `user-config.json`
  declares `output_preferences.default_output_mode`, use the config
  value as the default. The user's per-request override still wins.
- When `output_preferences.default_packaging` and
  `output_preferences.default_language` are present in the config and
  not overridden by the request, apply them as defaults.
```

- [ ] **Step 2: Run the conventions check**

```bash
python3 scripts/check-claude-conventions.py
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add skills/output-mode-composition.md
git commit -m "Wire user-config defaults into output-mode-composition"
```

### Task 20: `source-collection.md` jurisdiction priority

**Files:**

- Modify: `skills/source-collection.md`

- [ ] **Step 1: Insert the jurisdiction-priority note**

In the existing source-priority section (after Korean Law Strategy
and before EU Law Strategy), append:

```markdown
## User Config Jurisdiction Priority

When `user-config.json` declares `jurisdictions.primary` and
`jurisdictions.secondary`, use them as the source-priority order:
primary jurisdictions first, then secondary, then any explicitly
named jurisdictions in the question. This shapes the order of MCP
calls and `WebFetch` against official portals — not the rule of what
counts as a primary source.
```

(The Generated Knowledge Gate section, added in Task 15, sits below
this one.)

- [ ] **Step 2: Run the knowledge-coverage check**

```bash
python3 scripts/check-knowledge-coverage.py
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add skills/source-collection.md
git commit -m "Document user-config jurisdiction priority in source-collection"
```

## Chunk 6: Documentation and README integration

### Task 21: `docs/{en,ko}/how-to-use.md` add Personal Configuration section

**Files:**

- Modify: `docs/en/how-to-use.md`
- Modify: `docs/ko/how-to-use.md`
- Modify: `scripts/check-knowledge-coverage.py` (add the new section
  to required markers for both files)

- [ ] **Step 1: English version**

Insert a new `## Personal Configuration` section between
`## Quick Start` and `## Research Modes`. Cover:

- What `/onboard` does (5 questions + optional knowledge generation).
- The `user-config.json` schema (link to `templates/user-config.example.json`).
- Precedence rules (standalone vs. subagent).
- Knowledge construction: when Question 6 = `yes`, the wizard executes
  `docs/knowledge-construction-recipe.md` and produces a draft-gated
  `knowledge/<industry>-<area>/` directory. The user reviews and lifts
  the gate via `/review-knowledge <path>`.
- Privacy: preferences only, no personal identifiers.
- File location: project root, gitignored.

- [ ] **Step 2: Korean version**

Mirror with Korean prose. Anchors stay English (`## Personal Configuration`).

- [ ] **Step 3: Add the section to required markers**

Modify `scripts/check-knowledge-coverage.py` `REQUIRED_MARKERS`:

```python
"docs/en/how-to-use.md": [
    "## Prerequisites",
    "## Quick Start",
    "## Personal Configuration",   # NEW
    "## Research Modes",
    ...
],
"docs/ko/how-to-use.md": [
    "## Prerequisites",
    "## Quick Start",
    "## Personal Configuration",   # NEW
    "## Research Modes",
    ...
],
```

- [ ] **Step 4: Run knowledge-coverage**

```bash
python3 scripts/check-knowledge-coverage.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/en/how-to-use.md docs/ko/how-to-use.md scripts/check-knowledge-coverage.py
git commit -m "Document Personal Configuration in how-to-use docs"
```

### Task 22: `README.md` and `README.ko.md` link Personal Configuration

**Files:**

- Modify: `README.md`
- Modify: `README.ko.md`

- [ ] **Step 1: Add a one-line pointer to the Quick Start section**

After the standalone-use paragraph, append (English):

```markdown
For repeated standalone use, capture your default scope once with
`/onboard` (industry, area-of-law focus, jurisdictions, language,
preferred output mode). The wizard can also build a starter
knowledge directory for your domain — see
[Personal Configuration](docs/en/how-to-use.md#personal-configuration).
```

Mirror in Korean (`docs/ko/how-to-use.md#personal-configuration`).

- [ ] **Step 2: Run the conventions and knowledge-coverage checks**

```bash
python3 scripts/check-claude-conventions.py
python3 scripts/check-knowledge-coverage.py
```

Expected: both PASS.

- [ ] **Step 3: Commit**

```bash
git add README.md README.ko.md
git commit -m "Link Personal Configuration from README Quick Start (en/ko)"
```

## Chunk 7: Final verification + push

### Task 23: Full preflight + tests + push

- [ ] **Step 1: Full preflight**

```bash
python3 scripts/run-local-checks.py
```

Expected: 23/23 PASS (existing 21 + `user_config` + `generated_knowledge`).

- [ ] **Step 2: Full unittest discovery**

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

Expected: 175+ tests, all OK (current 168 + 4 new from
`test_user_config.py` + 3 new from `test_knowledge_construction.py`).

- [ ] **Step 3: Footprint diagnostic**

```bash
python3 scripts/measure-prompt-footprint.py
```

Expected: footprint grows by the new skill, command, knowledge file,
recipe document, and CLAUDE.md insertions. Do not update the frozen
Phase 0 snapshot in `docs/prompt-footprint.md` unless the user says so.

- [ ] **Step 4: Push**

```bash
git push origin main
```

## Verification Plan

After Task 23, all of these must pass cleanly:

```bash
python3 scripts/run-local-checks.py
python3 scripts/check-user-config.py
python3 scripts/check-user-config.py --config templates/user-config.example.json
python3 scripts/check-generated-knowledge.py
python3 scripts/check-generated-knowledge.py --dir tests/fixtures/generated-knowledge/kr-fintech-regulatory
python3 scripts/check-claude-conventions.py
python3 scripts/check-knowledge-coverage.py
python3 tests/test_user_config.py
python3 tests/test_knowledge_construction.py
python3 tests/test_claude_conventions.py
python3 tests/test_knowledge_coverage.py
python3 tests/test_run_local_checks.py
python3 tests/test_output_modes.py
python3 -m unittest discover -s tests -p "test_*.py"
```

Manual verification:

- Run `/onboard` in a fresh Claude Code session against a clean repo.
  Expect 6 questions; expect `user-config.json` at the project root
  after completion.
- Answer Question 6 with `yes` for a small jurisdiction-area pair
  (e.g., KR fintech-regulatory). Expect:
  - `knowledge/fintech-regulatory/` created with the four `.md` files
    plus `review-status.json`.
  - Every `.md` file starts with the draft banner.
  - Every `.md` file's frontmatter has the six required fields.
  - `review-status.json` reports `review_status: "draft"` and a
    `source_audit_status` populated by the citation auditor.
  - `user-config.json` has a matching entry in
    `generated_knowledge_directories`.
- Run a research question that targets the generated dir's domain.
  Expect the agent to surface `[GENERATED — DRAFT]` in `coverage_gaps`
  for any controlling proposition that relies on the draft files.
- Run `/review-knowledge knowledge/fintech-regulatory/`. Expect the
  banner replacement on every `.md` file, `review_status` becomes
  `verified`, and the matching `user-config.json` entry updates.
- Re-run the same research question. Expect the `[GENERATED — DRAFT]`
  warning to disappear because the gate is lifted.
- Run `/onboard --reset` and confirm the file is replaced after
  confirmation.

## Risk and Rollback

The risk surface is moderate-to-high because Layer 2 (knowledge
construction) introduces auto-generated content into a research
agent. Mitigations are layered:

- **Banner gate** prevents draft content from supporting
  high-confidence conclusions.
- **Per-fact source URLs** keep every claim traceable. Citation audit
  surfaces unverifiable claims.
- **`source_audit_status` in `review-status.json`** is the same
  vocabulary as the standalone deliverable manifest's audit status,
  giving the user a familiar trust signal.
- **Generated dirs are gitignored by default**; the user explicitly
  opts in to share by removing the dir from the ignore list.
- **Recipe is versioned**. Future recipe changes can detect older
  generated dirs via `recipe_version` and ask the user to regenerate.

Rollback: each task commits independently. The new chunks 3 and 4
sit on top of an existing functional system (config-only wizard);
if knowledge generation proves unreliable in practice, revert the
Chunk 3 + 4 commits and the wizard reverts to config-only mode
without further fixup.

## Done Definition

This plan is done when:

- `/onboard` runs end-to-end in a clean Claude Code session and writes
  a valid `user-config.json` at the project root.
- Question 6 = `yes` produces a `knowledge/<industry>-<area>/`
  directory that passes `python3 scripts/check-generated-knowledge.py`,
  contains the draft banner on every `.md` file, and includes a
  `review-status.json` with `review_status: "draft"` plus a real
  `source_audit_status` from a citation-auditor run.
- `/review-knowledge <path>` flips `review_status` to `verified`,
  replaces the banner on every `.md` file, updates `user-config.json`,
  and re-validates cleanly.
- `python3 scripts/run-local-checks.py` exits 0 with both new
  checks (`user_config` and `generated_knowledge`) passing in
  skip-when-absent mode on a fresh clone and in valid-when-present
  mode against the test fixtures.
- `CLAUDE.md` documents Stage 0 config loading + the gate rule;
  `classify-research-mode`, `output-mode-composition`, and
  `source-collection` document the config-aware precedence rules
  including the Generated Knowledge Gate.
- `docs/en/how-to-use.md` and `docs/ko/how-to-use.md` have a
  Personal Configuration section enforced by knowledge-coverage,
  including instructions for `/onboard --build-knowledge` and
  `/review-knowledge`.
- `README.md` and `README.ko.md` link Personal Configuration from
  the Quick Start area.
- `docs/knowledge-construction-recipe.md` is in place at version
  `1.0`, and the wizard skill explicitly references it as the
  canonical recipe.
- No regression appears in any pre-existing test or quality gate.
