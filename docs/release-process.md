# Release Process

This document defines the release preflight workflow for
`legal-research-agent`. Use it whenever cutting a tagged release.

The release process is intentionally lean: the agent does not publish
to PyPI or npm, so the only release artifact is the git tag plus a
release note in the repository.

---

## Pre-Release Checklist

Run the following from a clean working tree on `main`. All steps must
pass before tagging.

1. **Sync with origin**

   ```bash
   git status
   git fetch origin
   git pull --ff-only origin main
   ```

   `git status` must report a clean tree. `git pull --ff-only` must
   succeed without merge conflicts.

2. **Run the full local preflight**

   ```bash
   python3 scripts/run-local-checks.py
   python3 scripts/run-local-checks.py --report
   ```

   All checks must pass (currently 21/21). The `--report` form writes
   `reports/local-checks-latest.json` for archival.

3. **Run the full unittest discovery**

   ```bash
   python3 -m unittest discover -s tests -p "test_*.py"
   ```

   All tests must pass with zero failures and zero errors.

4. **Measure prompt footprint**

   ```bash
   python3 scripts/measure-prompt-footprint.py
   python3 scripts/measure-prompt-footprint.py --include-vendor
   ```

   Compare the footprint to the frozen Phase 0 baseline in
   `docs/prompt-footprint.md`. A material increase (e.g., > 20% over
   baseline) without an accompanying quality change requires a
   release-note explanation.

5. **Token comparison gate**

   ```bash
   python3 scripts/compare-token-runs.py \
     tests/fixtures/token-comparison/token-comparison-manifest.json
   ```

   The manifest's `quality_status` and per-route delta must match the
   release expectation. A merged-run token regression without a
   `quality_reason` blocks the release.

6. **Verify Claude Code conventions**

   ```bash
   python3 scripts/check-claude-conventions.py
   python3 scripts/check-output-modes.py
   ```

   Both must exit `0`. These are also part of step 2 but are listed
   here for visibility.

7. **Verify the citation-auditor vendor stamp**

   ```bash
   python3 scripts/check-citation-auditor-vendor.py
   ```

   If the vendor stamp is older than the sibling source repo, decide
   whether to refresh before tagging.

---

## Version Tagging

After the checklist passes:

1. **Pick a version** following [SemVer](https://semver.org/):

   - `MAJOR` — backward-incompatible orchestrator contract or skill
     reorganization;
   - `MINOR` — new modes, new docs, new validators (additive);
   - `PATCH` — fixes that do not change the public contract.

2. **Tag the merge commit** (not a separate tag commit):

   ```bash
   VERSION=v1.0.0
   git tag -a "$VERSION" -m "Release $VERSION"
   git push origin "$VERSION"
   ```

3. **Verify the tag**

   ```bash
   git show "$VERSION" --stat
   ```

   The tag must point at the same SHA the preflight ran against.

---

## Release Notes

Write the release note as a Markdown file under `docs/releases/` (create
the directory on first release):

```text
docs/releases/<VERSION>.md
```

Required sections in every release note:

- `## Summary` — one paragraph of what changed and why
- `## Highlights` — 3-7 bullet points covering user-visible changes
- `## Compatibility` — orchestrator-contract impact, breaking changes,
  migration notes
- `## Quality Status` — preflight result (PASS / FAIL count), token
  comparison status, prompt-footprint delta vs baseline
- `## Acknowledgements` — optional

Cross-link the release note from:

- the README's Roadmap section (mark items checked-off);
- `docs/migration-notes.md` if any migration step is required.

---

## Post-Release

After tagging:

1. **Push the tag** (if not already done):

   ```bash
   git push origin "$VERSION"
   ```

2. **Create the GitHub release** (if the repo is hosted on GitHub):

   ```bash
   gh release create "$VERSION" \
     --title "$VERSION" \
     --notes-file "docs/releases/$VERSION.md"
   ```

3. **Update the README's Roadmap** — check off completed items, add new
   ones for the next cycle.

4. **Archive the preflight report**

   ```bash
   cp reports/local-checks-latest.json reports/local-checks-$VERSION.json
   ```

   The `reports/` directory is gitignored, so archive externally if the
   organization requires durable retention.

5. **Open a follow-up plan** under `docs/` for the next workstream if
   one is queued.

---

## Hotfix Workflow

For urgent fixes that cannot wait for the full preflight cycle:

1. Branch from the tag of the affected release.
2. Apply the minimal fix.
3. Run **at least** these subset checks:

   ```bash
   python3 scripts/run-local-checks.py
   python3 -m unittest discover -s tests -p "test_*.py"
   ```

4. Tag as `MAJOR.MINOR.(PATCH+1)`.
5. Backport to `main` if applicable.
6. Document the hotfix scope in the release note's `## Hotfix` section.

Hotfix releases should still document the abbreviated preflight in the
release note so future release auditors can see exactly what ran.
