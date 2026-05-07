---
description: Ingest source files dropped into library/inbox/ — converts to Markdown, auto-classifies Grade A/B/C, and updates library/_index.md.
argument-hint: ""
---

Apply `skills/ingest.md`.

If `library/inbox/` is empty (excluding `_processed/` and `_failed/`
subdirectories), tell the user there is nothing to ingest and stop.

After ingest completes, summarize:

- count of ingested files per Grade,
- list of rejected files with reasons,
- updated `library/_index.md` summary.

The user is reminded that `library/` is gitignored — ingested
materials live only on this machine.
