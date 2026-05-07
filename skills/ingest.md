---
name: ingest
description: Use when /ingest is invoked or when files are dropped into library/inbox/ — converts PDF/DOCX/PPTX/XLSX/HTML to Markdown via markitdown MCP, classifies Grade A/B/C, generates frontmatter, and updates the library index.
disable-model-invocation: true
---

# Library Ingest

Use this skill when the `/ingest` slash command runs.

## Inputs

- Files in `library/inbox/`. Supported formats: PDF, DOCX, PPTX,
  XLSX, HTML, MD, TXT. (HWP/HWPX is not supported by markitdown
  MCP; surface as a fallback gap.)

## Workflow

1. List files in `library/inbox/` (excluding `_processed/` and
   `_failed/` subdirectories). Stop with a friendly message if empty.
2. For each file:
   a. Determine target format via extension. If unsupported (HWP,
      HWPX, others), move to `library/inbox/_failed/` and record the
      reason.
   b. For supported formats, call
      `mcp__markitdown__convert_to_markdown` to extract Markdown.
      For `.md`/`.txt`, pass through.
   c. Classify Grade A / B / C / D based on content signals:
      - Grade A: official government domain in source URL or
        `legislation` / `regulation` / `decree` / `statute`
        keywords in the first 500 characters.
      - Grade B: court decisions, regulator decisions, law-firm
        newsletters, regulator press releases.
      - Grade C: academic papers, journal articles, treatises.
      - Grade D: news articles, AI summaries, generic web posts —
        rejected with a note in `_failed/` rather than ingested.
   d. Generate YAML frontmatter:
      ```yaml
      ---
      title: <extracted title>
      source_url: <if known, else null>
      ingested_at: <today ISO date>
      grade: <A/B/C>
      classification_signals: [<keywords that drove classification>]
      ---
      ```
   e. Move the original to `library/inbox/_processed/` and write the
      converted Markdown into `library/grade-{a,b,c}/<slug>.md`.
3. Regenerate `library/_index.md` listing every file under each
   Grade folder.
4. Print a summary: count per Grade, list of rejected files with
   reasons.

## Quality Floor

- Do not auto-grade D-grade material as A/B/C. Reject with a clear
  message.
- Do not silently drop unsupported file formats — move them to
  `_failed/` with a `.reason` sidecar explaining the limitation.
- Do not modify files already in `grade-{a,b,c}/` directories.
  Re-ingestion requires explicit user instruction.
- Do not commit any ingested file. The directory is gitignored.

## Fallback Gaps

- HWP / HWPX: markitdown MCP does not cover these formats. Document
  the gap in the rejected-file `.reason` sidecar.
- Files larger than markitdown's limit (currently ~10 MB per file):
  move to `_failed/` with a `.reason` sidecar.
