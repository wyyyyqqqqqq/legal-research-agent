---
description: Lift the [GENERATED — REQUIRES HUMAN REVIEW] gate on a generated knowledge directory after the user has reviewed and (optionally) edited the contents.
argument-hint: "<path/to/knowledge-dir/>"
---

The user has reviewed (and possibly edited) the generated knowledge
directory in `$ARGUMENTS`. Lift the gate as follows:

1. Confirm the path exists, is under `knowledge/`, and contains a
   `review-status.json`. If not, stop and tell the user what is
   missing.

2. Run `python3 scripts/check-generated-knowledge.py --dir
   <path>` to confirm the directory currently passes the recipe's
   structural check. If it fails, surface the validator output
   and ask the user to fix the issues before lifting the gate.

3. Show the user the current `audit_summary` from
   `review-status.json` (verified vs. unverified facts, audit
   status). Ask for explicit confirmation that they have verified
   every `[Unverified]` fact and accept the directory as trusted.

4. On confirmation:
   - Replace the `> **[GENERATED — REQUIRES HUMAN REVIEW]** ...`
     banner on every `.md` file under the directory with
     `> **[VERIFIED]** Reviewed on YYYY-MM-DD by the user.` (use
     today's local ISO date).
   - Update `review-status.json`:
     - `review_status: "verified"`
     - `lifted_at: "<today>"`
   - Update each `.md` file's frontmatter `verification_status` to
     `verified`.
   - Update the matching entry in `user-config.json`'s
     `generated_knowledge_directories` list:
     - `review_status: "verified"`
     - `lifted_at: "<today>"`

5. Re-run `python3 scripts/check-generated-knowledge.py --dir
   <path>` to verify the post-lift state. Both the banner and
   `review_status` must now be the verified form.

6. Re-run `python3 scripts/check-user-config.py` to confirm the
   updated `user-config.json` still validates.

7. Print a summary that lists the directory path, the
   `audit_summary`, and a reminder that subsequent research runs
   will treat the directory as trusted (no `[GENERATED — DRAFT]`
   warning in `coverage_gaps`).

Do not proceed with the gate lift if:

- The directory's audit status is `live_failed` (ask the user to
  re-run citation audit and resolve issues first).
- Required `.md` files are missing or have invalid frontmatter.
- `review-status.json` cannot be parsed.

If `$ARGUMENTS` is empty, ask for the directory path.
