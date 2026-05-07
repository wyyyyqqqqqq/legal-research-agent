---
name: onboarding
description: Use when /onboard is invoked or when user-config.json is missing on standalone use — runs the wizard, writes user-config.json, optionally executes the knowledge construction recipe, and reports the resulting defaults.
disable-model-invocation: true
---

# Onboarding Wizard

Use this skill when the `/onboard` slash command runs, or when a
standalone session starts without `user-config.json` and the user
has not declared their scope inline. The skill walks the user
through a 5-question scope wizard, optionally runs the recipe-driven
knowledge construction step, and writes a project-local
`user-config.json`.

## Inputs

- Optional existing `user-config.json` at the project root.
- Question catalog at `knowledge/onboarding/wizard-flow.md`.
- Knowledge construction recipe at
  `docs/knowledge-construction-recipe.md` (used only when the user
  opts into Question 6 = `yes`).

## Workflow

1. **Detect existing config.** Read `user-config.json` if present.
   - If the user invoked `/onboard --reset`, confirm replacement,
     back up the existing file to `user-config.previous.json`, and
     proceed with all questions.
   - If the user invoked `/onboard` without `--reset` and a config
     exists, offer field-by-field update.
   - Otherwise (no config), proceed with all questions.
2. **Run questions per `knowledge/onboarding/wizard-flow.md`.** Use
   the host's structured question facility (e.g.,
   `AskUserQuestion`) when available; fall back to plain prompts
   otherwise.
3. **Apply derivation rules** from the catalog to compute
   `default_research_mode`.
4. **Write `user-config.json`.** Set `schema_version: "1.0"`,
   `created_at` and `updated_at` to today's ISO date, and
   `generated_knowledge_directories: []` initially.
5. **Validate.** Run `python3 scripts/check-user-config.py`. If
   validation fails, restart the failing question or roll back the
   write.
6. **Knowledge construction (optional).** If Question 6 was
   answered `yes` (or the user invoked `/onboard --build-knowledge`),
   apply the recipe-execution section below.
7. **Summarize.** Print a one-paragraph confirmation listing
   industry, primary jurisdictions, default output mode, and
   language. If a knowledge directory was built, include the
   directory path and audit summary.

## Knowledge Construction (Question 6 = `yes`)

When the user opts into knowledge construction, execute the recipe
in `docs/knowledge-construction-recipe.md` for each
`industry`-`area_of_law` pair the user named.

Steps:

1. Compute the directory name as `<industry>-<area_slug>` where
   `area_slug` is the snake-case area_of_law value. For multi-area
   users, generate one directory per area unless the user opts out
   per area.
2. Verify the directory does not already exist. If it does, ask
   whether to replace, skip, or keep both with a numeric suffix.
3. Apply the recipe's run order:
   `source-map.md` → `regulatory-map.md` →
   `issue-taxonomy.md` → `library-index.md` → `review-status.json`.
4. Per file, follow the recipe's live-research protocol:
   - For `jurisdiction: KR`, prefer `mcp__claude_ai_Korean-law__*`
     tool calls over `WebFetch`.
   - For other jurisdictions, use `WebFetch` against whitelisted
     official portals (`law.go.kr`, `eur-lex.europa.eu`,
     `congress.gov`, `legislation.gov.uk`, etc.).
5. Apply the recipe's hallucination mitigation rules. Every
   regulator name and statute citation must cite a source URL.
   Unverifiable facts are marked `[Unverified]` inline rather than
   silently written as fact.
6. Add the draft banner block as the first line of every generated
   `.md` file:

   ```text
   > **[GENERATED — REQUIRES HUMAN REVIEW]** This file was built by
   > the /onboard wizard from live research. Lift the gate with
   > `/review-knowledge knowledge/<industry>-<area>/` after editing.
   ```

7. After all four `.md` files are generated, run the vendored
   `citation-auditor` over the directory:

   ```text
   /audit knowledge/<industry>-<area>/
   ```

   Record the per-claim verdict counts in `audit_summary` in
   `review-status.json`, and set `source_audit_status` to one of
   `live_passed`, `live_failed`, `deterministic_smoke`,
   `not_run_session_unavailable`, or `not_required` per the
   citation-audit spec.
8. Run `python3 scripts/check-generated-knowledge.py
   --dir knowledge/<industry>-<area>` to verify structural
   conformance. If it fails, surface the errors and offer to roll
   back the directory write.
9. Append a new entry to `user-config.json`'s
   `generated_knowledge_directories` list:

   ```json
   {
     "path": "knowledge/<industry>-<area>/",
     "industry": "<industry>",
     "area_of_law": "<area_of_law>",
     "jurisdiction": "<primary_jurisdiction>",
     "review_status": "draft",
     "source_audit_status": "<from step 7>",
     "created_at": "<today>",
     "lifted_at": null
   }
   ```

10. Re-run `python3 scripts/check-user-config.py` to confirm the
    config remains valid after the new entry.
11. Print a summary that mentions:
    - the directory path,
    - the audit summary (verified vs. unverified facts),
    - the `[GENERATED — REQUIRES HUMAN REVIEW]` gate,
    - the `/review-knowledge <path>` command to lift the gate.

## Quality Floor

- Do not invent industry or area-of-law values outside the
  controlled vocabulary in
  `knowledge/onboarding/wizard-flow.md`. Use `industry: other` +
  `industry_freetext` for anything that does not fit.
- Do not collect personal identifiers (name, firm, bar admissions).
  Preferences only.
- Do not write `user-config.json` until every required question is
  answered and validated.
- Do not promise that the wizard generates `knowledge/<area>/` files
  without verification. Generation is gated by the recipe's source
  verification rules and the `[GENERATED — REQUIRES HUMAN REVIEW]`
  banner; users must run `/review-knowledge` after inspecting.
- Do not mark a generated directory as `verified` automatically.
  The gate is lifted only by the user via `/review-knowledge`.
- Do not generate a knowledge directory when the citation audit
  reports `live_failed` without surfacing the audit findings to the
  user and asking whether to keep the draft or roll back.

## Precedence

- **Standalone use:** `user-config.json` defaults are primary; the
  user's per-question overrides still win when explicit.
- **Subagent dispatch:** orchestrator classification is primary per
  `CLAUDE.md` Operating Rules. The config is a fallback default for
  fields the orchestrator did not specify.

When the wizard finishes, remind the user that:

- `user-config.json` is gitignored — it lives only on this machine.
- Generated knowledge directories are gitignored by default;
  the user removes them from `.gitignore` only when intentionally
  committing reviewed knowledge to share.
- The wizard can be re-run any time with `/onboard` (update),
  `/onboard --reset` (replace), or `/onboard --build-knowledge`
  (rebuild knowledge for the existing config).
