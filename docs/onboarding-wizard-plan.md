# Onboarding Wizard Implementation Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development`
> (if subagents are available) or `superpowers:executing-plans` to implement
> this plan. Steps use checkbox (`- [ ]`) syntax so progress can be tracked
> in the file itself.

**Goal:** Add an interactive `/onboard` slash command that asks the user
about their **industry**, **area-of-law focus**, **jurisdictions**, and
**output preferences**, then writes a project-local `user-config.json`
that the agent consults for defaults on every subsequent standalone run.

**Approach:** Runtime configuration only — the wizard does **not** generate
`knowledge/<custom-area>/` files dynamically. Existing skills
(`classify-research-mode`, `source-collection`, `output-mode-composition`)
read `user-config.json` for defaults. The agent stays honest about the
limit: hand-curated knowledge directories like `knowledge/game-regulation/`
deliver the highest quality; runtime config gets a standalone user roughly
70% of that depth without any code changes per matter.

**Tech Stack:** Python 3.11+, JSON (no schema library — manual validation
matches existing `scripts/validate-*.py` style), Markdown, Claude Code
slash commands and skills.

## What "match game_regulation quality" really means

The user's question — "결과물은 game mode 정도로 나오게…이게 가능하려나?"
— deserves a direct answer. The current `game_regulation` mode delivers
its quality from four layers:

1. The right **research mode** is picked at intake.
2. The right **knowledge files** are loaded (`knowledge/game-regulation/`
   issue taxonomy, regulator map, source map, library index).
3. The **counter-analysis discipline** is applied per the per-mode
   minimum.
4. The right **output mode** is selected for the deliverable shape.

Layers 1, 3, and 4 are reproducible at runtime from a config. Layer 2 is
not — those knowledge files are hand-curated artifacts that encode domain
expertise (regulator names, statutory hierarchy, agency precedents,
similar-statute confusion traps). A wizard cannot fabricate them safely
without becoming a hallucination factory.

**Realistic outcome:** the wizard captures the user's intent and the agent
uses it consistently across sessions. For arbitrary industry/area
combinations the deliverables will match `game_regulation` on **process
and structure**, but not on **domain depth**. To reach full parity for
a new domain, a contributor still has to write `knowledge/<area>/`
files by hand. That contribution path stays separate (and is documented
in `docs/source-playbook-authoring.md` for general-law domains today).

## Out of scope

- Auto-generating `knowledge/<custom-area>/` files. The wizard never
  writes domain-knowledge content; it only writes configuration.
- Personal identifiers (name, firm, bar admissions). Preferences only.
- Cross-session or cross-machine config sync.
- Onboarding for the orchestrator subagent dispatch path. The wizard
  is for standalone users; orchestrator dispatch keeps using its
  classification payload.
- Web search or live MCP calls during the wizard itself. The wizard is
  pure local interaction.

## Locked design decisions

| Decision | Value | Reason |
|:---|:---|:---|
| Config location | `./user-config.json` (project root) | Matches `general-legal-research` convention; easy to find and edit. |
| Personal info | None — preferences only | Mitigates accidental commit risk; user-supplied scoping is enough. |
| Precedence (standalone) | User config wins over inferred defaults | The user explicitly stated their scope; respect it. |
| Precedence (subagent) | Orchestrator classification stays primary; config is fallback | Subagent dispatch must remain orchestrator-driven for predictable token costs. |
| Auto-generation of knowledge | None — config writes only `user-config.json` | Quality risk. Hand-curated `knowledge/` is the only path to high-depth domain coverage. |

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
    user-config.example.json                    # CREATE: schema example, gitignored false
  knowledge/
    onboarding/
      wizard-flow.md                            # CREATE: question catalog + selection logic
  skills/
    onboarding.md                               # CREATE: /onboard skill (interactive wizard)
    classify-research-mode.md                   # MODIFY: consult config when present
    output-mode-composition.md                  # MODIFY: default output_mode from config
    source-collection.md                        # MODIFY: jurisdiction priority from config
  .claude/
    commands/
      onboard.md                                # CREATE: /onboard slash command
  scripts/
    check-user-config.py                        # CREATE: optional config schema validator
    run-local-checks.py                         # MODIFY: register check_user_config (optional)
  tests/
    test_user_config.py                         # CREATE
    fixtures/
      user-config/
        kr-game-only.json                       # CREATE: minimal KR game preference
        kr-fintech-multi.json                   # CREATE: KR fintech, multi-jurisdiction
        en-us-corporate.json                    # CREATE: US corporate, English
        invalid-missing-jurisdictions.json      # CREATE: invalid sample
  docs/
    en/how-to-use.md                            # MODIFY: add Personal Configuration section
    ko/how-to-use.md                            # MODIFY: mirror
    onboarding-wizard-plan.md                   # THIS FILE
```

### `user-config.json` schema

```json
{
  "schema_version": "1.0",
  "industry": "game",
  "industry_freetext": null,
  "area_of_law": ["regulatory", "consumer_protection"],
  "jurisdictions": {
    "primary": ["KR"],
    "secondary": ["JP", "US"]
  },
  "output_preferences": {
    "default_research_mode": "game_regulation",
    "default_output_mode": "canonical",
    "default_packaging": "standalone_markdown",
    "default_language": "ko"
  },
  "specialist_handoff_owners": [],
  "created_at": "2026-05-08",
  "updated_at": "2026-05-08"
}
```

Field semantics:

- `industry` — one of the controlled vocabulary: `game`, `fintech`,
  `healthcare`, `platform`, `e_commerce`, `media`, `other`. When `other`,
  `industry_freetext` carries the user's description.
- `area_of_law` — list of: `general`, `regulatory`, `contract`, `consumer_protection`,
  `intellectual_property`, `employment`, `privacy`, `tax`, `competition`,
  `other`. Multi-select.
- `jurisdictions.primary` and `jurisdictions.secondary` — non-empty
  primary list; secondary may be empty. Values are ISO country codes
  (`KR`, `US`, `JP`, `EU`, `UK`, `DE`, `FR`, `JP`, `SG`, `AU`, `CA`, `CN`, etc.).
- `output_preferences.default_research_mode` — derived from `industry` + `area_of_law`,
  but explicitly stored so the agent doesn't re-infer every session. The
  agent can still override per-question.
- `output_preferences.default_output_mode` — one of the five output mode
  slugs (`canonical`, `executive_brief`, `comparative_matrix`,
  `enforcement_case_law`, `black_letter_commentary`).
- `output_preferences.default_packaging` — one of the three packaging
  slugs (`standalone_markdown`, `handoff_packet`, `docx_ready_markdown`).
- `output_preferences.default_language` — `ko`, `en`, or `bilingual`.
- `specialist_handoff_owners` — list of agent IDs the user routinely
  co-runs (e.g., `PIPA-expert`, `GDPR-expert`). When non-empty, the
  agent records handoff boundaries automatically.
- `created_at` and `updated_at` — ISO date strings.

### Wizard question flow

The wizard asks 5 questions, each with controlled-vocabulary answers
plus an "other / free text" escape:

1. **Industry** — single-select from 7 options.
2. **Area-of-law focus** — multi-select from 10 options.
3. **Primary jurisdiction(s)** — multi-select; at least one required.
4. **Secondary jurisdictions** — optional multi-select.
5. **Output preference** — single-select with mode + packaging + language
   shortcuts (e.g. "Quick brief in Korean", "Multi-jurisdiction comparison
   in English", "DOCX-ready statute deep dive in Korean").

After answers, the wizard derives `default_research_mode` (game →
`game_regulation`; otherwise `general`; both flags set → `game_plus_general`)
and writes `user-config.json` plus a one-line confirmation summary.

The question catalog and selection logic live in
`knowledge/onboarding/wizard-flow.md` so future contributors can adjust
the vocabulary without changing the skill body.

### Skill integration

| Skill | Change |
|:---|:---|
| `skills/classify-research-mode.md` | Stage 0: load `user-config.json` if present. In standalone use, treat `output_preferences.default_research_mode` as primary and the question itself as override. In subagent use, orchestrator classification stays primary. |
| `skills/output-mode-composition.md` | When `output_mode` is unset on the request and `user-config.json` declares one, use the declared mode as default. |
| `skills/source-collection.md` | When `user-config.json` declares jurisdictions, use them as the source-priority order. |

`CLAUDE.md` adds a Stage 0 paragraph: "If `user-config.json` exists at
the project root, load it before Stage 1 intake. Use it as the default
source for research mode, jurisdictions, output mode, packaging, and
language. Orchestrator classification still wins for orchestrated
subagent dispatch."

## Chunk 1: Schema, example, validator, gitignore

### Task 1: Add `templates/user-config.example.json`

**Files:**

- Create: `templates/user-config.example.json`

- [ ] **Step 1: Write the example**

Use the schema in the Architecture section above. Set `industry` to
`game`, `area_of_law` to `["regulatory", "consumer_protection"]`,
`jurisdictions.primary` to `["KR"]`, `default_research_mode` to
`game_regulation`, `default_output_mode` to `canonical`,
`default_language` to `ko`. The example doubles as a validator-friendly
sample.

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
!user-config.example.json
!templates/user-config.example.json
```

The negation lines preserve any committed example file.

- [ ] **Step 2: Verify**

```bash
echo '{"test":1}' > user-config.json
git status --short user-config.json
rm user-config.json
```

Expected: empty output (file ignored).

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "Gitignore user-config.json (local-only runtime config)"
```

### Task 3: Add `scripts/check-user-config.py`

**Files:**

- Create: `scripts/check-user-config.py`

The validator is **optional** — it runs only if `user-config.json`
exists. The local preflight passes when the file is absent (the standard
case for fresh clones). When present, it must conform to the schema.

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

`kr-game-only.json`:

```json
{
  "schema_version": "1.0",
  "industry": "game",
  "industry_freetext": null,
  "area_of_law": ["regulatory"],
  "jurisdictions": {"primary": ["KR"], "secondary": []},
  "output_preferences": {
    "default_research_mode": "game_regulation",
    "default_output_mode": "canonical",
    "default_packaging": "standalone_markdown",
    "default_language": "ko"
  },
  "specialist_handoff_owners": [],
  "created_at": "2026-05-08",
  "updated_at": "2026-05-08"
}
```

`kr-fintech-multi.json`:

```json
{
  "schema_version": "1.0",
  "industry": "fintech",
  "industry_freetext": null,
  "area_of_law": ["regulatory", "consumer_protection", "privacy"],
  "jurisdictions": {"primary": ["KR"], "secondary": ["JP", "SG"]},
  "output_preferences": {
    "default_research_mode": "general",
    "default_output_mode": "comparative_matrix",
    "default_packaging": "standalone_markdown",
    "default_language": "ko"
  },
  "specialist_handoff_owners": ["PIPA-expert"],
  "created_at": "2026-05-08",
  "updated_at": "2026-05-08"
}
```

`en-us-corporate.json`:

```json
{
  "schema_version": "1.0",
  "industry": "other",
  "industry_freetext": "US-listed SaaS company, M&A focus",
  "area_of_law": ["general", "contract", "competition"],
  "jurisdictions": {"primary": ["US"], "secondary": ["EU"]},
  "output_preferences": {
    "default_research_mode": "general",
    "default_output_mode": "executive_brief",
    "default_packaging": "standalone_markdown",
    "default_language": "en"
  },
  "specialist_handoff_owners": [],
  "created_at": "2026-05-08",
  "updated_at": "2026-05-08"
}
```

- [ ] **Step 2: Write the invalid fixture**

`invalid-missing-jurisdictions.json` — primary list empty:

```json
{
  "schema_version": "1.0",
  "industry": "game",
  "industry_freetext": null,
  "area_of_law": ["regulatory"],
  "jurisdictions": {"primary": [], "secondary": []},
  "output_preferences": {
    "default_research_mode": "game_regulation",
    "default_output_mode": "canonical",
    "default_packaging": "standalone_markdown",
    "default_language": "ko"
  },
  "specialist_handoff_owners": [],
  "created_at": "2026-05-08",
  "updated_at": "2026-05-08"
}
```

- [ ] **Step 3: Write the test**

```python
#!/usr/bin/env python3
"""Validate user-config schema fixtures."""

from __future__ import annotations

import importlib.util
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

Insert next to the other `check-*.py` entries:

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
so future contributors can adjust the vocabulary or add an industry
without touching skill instructions.

- [ ] **Step 1: Write the catalog**

Required sections:

- `## Question 1 — Industry` with the 7 controlled values
- `## Question 2 — Area of law focus` with the 10 controlled values
- `## Question 3 — Primary jurisdictions`
- `## Question 4 — Secondary jurisdictions`
- `## Question 5 — Output preference` with 3-5 shortcut bundles
  (e.g., "Quick KR brief", "Multi-jurisdiction comparison", "DOCX-ready
  statute deep dive")
- `## Derivation rules` describing how `default_research_mode` is
  inferred from `industry` (`game` → `game_regulation`; `industry` is
  one of the others AND `area_of_law` includes `regulatory` related
  to game → `game_plus_general`; otherwise `general`)
- `## Skip rules` — when secondary jurisdictions can be skipped, when
  the wizard short-circuits if `user-config.json` already exists

Cross-link the controlled vocabulary lists to the matching values in
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

Required content (frontmatter follows the existing convention):

```markdown
---
name: onboarding
description: Use when /onboard is invoked or when user-config.json is missing on standalone use — runs the wizard, writes user-config.json, and reports the resulting defaults.
disable-model-invocation: true
---

# Onboarding Wizard

Use this skill when the `/onboard` slash command runs, or when a
standalone session starts without `user-config.json` and the user
has not declared their scope inline.

## Inputs

- Optional existing `user-config.json` (offer to update vs. replace).
- Question catalog from `knowledge/onboarding/wizard-flow.md`.

## Workflow

1. Check whether `user-config.json` exists at the project root.
   - If it exists, summarize the current config and ask whether to
     update or replace.
   - If it does not exist, proceed to the question flow.
2. Apply the question catalog from
   `knowledge/onboarding/wizard-flow.md`. Use the host's structured
   question facility (e.g., `AskUserQuestion`) when available;
   otherwise fall back to plain prompts.
3. Apply the derivation rules to compute `default_research_mode`,
   `default_output_mode`, `default_packaging`, and `default_language`.
4. Write `user-config.json` at the project root with `schema_version`
   `"1.0"`, the user's answers, and `created_at` / `updated_at` set
   to the current local date.
5. Run `python3 scripts/check-user-config.py` and surface the result.
   If validation fails, restart the failing question or roll back
   the write.
6. Print a one-paragraph summary of the active config (industry,
   primary jurisdictions, default output mode, language).

## Quality Floor

- Do not invent industry or area-of-law values outside the controlled
  vocabulary. Use `industry: other` + `industry_freetext` for anything
  that does not fit.
- Do not collect personal identifiers (name, firm, bar admissions).
- Do not write to `user-config.json` until every required question is
  answered.
- Do not promise that the wizard generates `knowledge/<custom-area>/`
  files. It does not.

## Precedence

- Standalone: `user-config.json` defaults are primary; per-question
  overrides win when explicit.
- Subagent dispatch: orchestrator classification is primary; the
  config is a fallback default for fields the orchestrator did not
  specify.
```

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
description: Run the onboarding wizard to create or update user-config.json with industry, area-of-law, jurisdictions, and output preferences.
argument-hint: "[--reset]"
---

Apply `skills/onboarding.md`.

If `$ARGUMENTS` contains `--reset`, replace any existing
`user-config.json` after confirmation. Otherwise offer to update the
existing config field-by-field.

After the wizard finishes, summarize the active config (industry,
primary jurisdictions, default output mode, language) and remind the
user that the file is gitignored — it lives only on this machine.
```

- [ ] **Step 2: Run the conventions check**

```bash
python3 scripts/check-claude-conventions.py
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/onboard.md
git commit -m "Add /onboard slash command"
```

## Chunk 3: Skill integration (config-aware behavior)

### Task 9: Stage 0 in CLAUDE.md

**Files:**

- Modify: `CLAUDE.md`

- [ ] **Step 1: Insert Stage 0 paragraph**

Insert a `## Stage 0: User Configuration` section between
`## Prerequisites` and `## Operating Rules`.

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

If `user-config.json` is missing on standalone use and the user has
not declared their scope inline, suggest running `/onboard`. Do not
require it — the agent must continue to work without a config when
the user asks a one-off question.
```

- [ ] **Step 2: Run the knowledge-coverage check**

```bash
python3 scripts/check-knowledge-coverage.py
```

Expected: PASS (existing markers preserved).

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "Add Stage 0 user-config loading to CLAUDE.md"
```

### Task 10: `classify-research-mode.md` consults config

**Files:**

- Modify: `skills/classify-research-mode.md`

- [ ] **Step 1: Insert the precedence note**

After the existing `## Precedence` section (or equivalent), add:

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

- [ ] **Step 2: Run the conventions check**

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

### Task 11: `output-mode-composition.md` consults config

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
  not overridden by the request, apply them as defaults to the
  packaging and language selections respectively.
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

### Task 12: `source-collection.md` consults jurisdiction priority

**Files:**

- Modify: `skills/source-collection.md`

- [ ] **Step 1: Insert the jurisdiction-priority note**

In the existing source-priority section (after Korean Law Strategy
and before EU Law Strategy), append a paragraph:

```markdown
## User Config Jurisdiction Priority

When `user-config.json` declares `jurisdictions.primary` and
`jurisdictions.secondary`, use them as the source-priority order:
primary jurisdictions first, then secondary, then any explicitly
named jurisdictions in the question. This shapes the order of MCP
calls and `WebFetch` against official portals — not the rule of what
counts as a primary source.
```

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

## Chunk 4: Documentation and README integration

### Task 13: `docs/{en,ko}/how-to-use.md` add Personal Configuration section

**Files:**

- Modify: `docs/en/how-to-use.md`
- Modify: `docs/ko/how-to-use.md`

- [ ] **Step 1: English version**

Insert a new `## Personal Configuration` section between
`## Quick Start` and `## Research Modes`.

```markdown
## Personal Configuration

Standalone users can capture their default scope (industry,
area-of-law focus, jurisdictions, language, preferred output mode)
in `user-config.json` so the agent reuses those defaults across
sessions.

Run the wizard:

\`\`\`text
/onboard
\`\`\`

The wizard asks five questions (industry, area-of-law focus, primary
jurisdictions, secondary jurisdictions, output preference) and
writes `user-config.json` at the project root. The file is
gitignored — it stays on your machine.

To replace an existing config:

\`\`\`text
/onboard --reset
\`\`\`

The full schema is documented in
\[`templates/user-config.example.json`\](../../templates/user-config.example.json).

**Precedence:**

- Standalone use: config defaults are primary; per-question overrides win.
- Subagent dispatch: orchestrator classification stays primary; config
  is a fallback for fields the orchestrator did not specify.

The wizard never collects personal identifiers (name, firm, bar
admissions). It writes preferences only.
```

- [ ] **Step 2: Korean version**

Mirror with Korean prose. Section heading stays `## Personal Configuration`.

- [ ] **Step 3: Run the knowledge-coverage check**

```bash
python3 scripts/check-knowledge-coverage.py
```

Expected: PASS.

- [ ] **Step 4: Add the section to required markers**

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

- [ ] **Step 5: Run knowledge-coverage**

```bash
python3 scripts/check-knowledge-coverage.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add docs/en/how-to-use.md docs/ko/how-to-use.md scripts/check-knowledge-coverage.py
git commit -m "Document Personal Configuration in how-to-use docs"
```

### Task 14: `README.md` and `README.ko.md` link Personal Configuration

**Files:**

- Modify: `README.md`
- Modify: `README.ko.md`

- [ ] **Step 1: Add a one-line pointer to the Quick Start section**

After the standalone-use paragraph, append:

```markdown
For repeated standalone use, capture your default scope once with
`/onboard` (industry, area-of-law focus, jurisdictions, language,
preferred output mode). See
[Personal Configuration](docs/en/how-to-use.md#personal-configuration).
```

Mirror in Korean. Korean version links to `docs/ko/how-to-use.md#personal-configuration`.

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

## Chunk 5: Final verification + push

### Task 15: Full preflight + tests + push

- [ ] **Step 1: Full preflight**

```bash
python3 scripts/run-local-checks.py
```

Expected: 22/22 PASS.

- [ ] **Step 2: Full unittest discovery**

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

Expected: 172+ tests, all OK (current 168 + new 4 from `test_user_config.py`).

- [ ] **Step 3: Footprint + token-comparison spot-check**

```bash
python3 scripts/measure-prompt-footprint.py
```

Expected: footprint grows by the size of new skill, command, knowledge
file, and CLAUDE.md insertion. Do not update the frozen Phase 0
snapshot in `docs/prompt-footprint.md` unless the user says so.

- [ ] **Step 4: Push**

```bash
git push origin main
```

## Verification Plan

After Task 15, all of these must pass cleanly:

```bash
python3 scripts/run-local-checks.py
python3 scripts/check-user-config.py
python3 scripts/check-user-config.py --config templates/user-config.example.json
python3 scripts/check-claude-conventions.py
python3 scripts/check-knowledge-coverage.py
python3 tests/test_user_config.py
python3 tests/test_claude_conventions.py
python3 tests/test_knowledge_coverage.py
python3 tests/test_run_local_checks.py
python3 tests/test_output_modes.py
python3 -m unittest discover -s tests -p "test_*.py"
```

Manual verification:

- Run `/onboard` in a fresh Claude Code session against a clean repo.
  Expect 5 questions; expect `user-config.json` at the project root
  after completion; expect `python3 scripts/check-user-config.py` to
  exit 0 against the new file.
- Without re-running `/onboard`, ask a question that aligns with the
  config (e.g., for a `kr-game-only` config, "한국 모바일 게임 광고
  심의 절차 알려줘"). Expect the agent to pick `game_regulation`
  research mode and `ko` language without re-asking.
- Run `/onboard --reset` and confirm the file is replaced after
  confirmation.
- Run `/audit user-config.json` — the citation auditor should
  recognize the file is non-narrative and skip rather than try to
  audit it. (If this is awkward, no action is needed — auditing a
  config file is not a supported flow.)

## Risk and Rollback

The risk surface is moderate but additive.

- The orchestrator-compatible `result.md` and the existing metadata
  contract are untouched.
- Existing skills gain "consult config when present" paragraphs but
  do not change behavior when the config is absent. Every existing
  fixture and test continues to pass.
- The new validator is permissive (skips when file absent), so a
  fresh clone preflight is unaffected.

Rollback: each task commits independently, and chunks are sequenced so
the system stays runnable at every commit boundary. `git revert` of
the relevant task commits restores prior behavior. Removing the
wizard skill, command, validator, and Stage 0 paragraph leaves the
agent in its pre-onboarding state with no leftover references.

## Done Definition

This plan is done when:

- `/onboard` runs end-to-end in a clean Claude Code session and writes
  a valid `user-config.json` at the project root.
- `python3 scripts/check-user-config.py` exits 0 against the example,
  the four fixtures, and any wizard-produced config.
- `python3 scripts/run-local-checks.py` exits 0 and includes the new
  `user_config` check (skipping cleanly on a fresh clone).
- `CLAUDE.md` documents Stage 0 config loading; `classify-research-mode`,
  `output-mode-composition`, and `source-collection` document the
  config-aware precedence rules.
- `docs/en/how-to-use.md` and `docs/ko/how-to-use.md` have a
  Personal Configuration section enforced by knowledge-coverage.
- README and README.ko both link Personal Configuration from the
  Quick Start area.
- No regression appears in any pre-existing test or quality gate.
