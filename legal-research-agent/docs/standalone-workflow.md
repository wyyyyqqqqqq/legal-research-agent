# Standalone Deliverable Workflow

This workflow applies when `legal-research-agent` is used by itself rather than
only as an orchestrator research component.

The mandatory research contract remains:

```text
{OUTPUT_DIR}/legal-research-agent-result.md
{OUTPUT_DIR}/legal-research-agent-meta.json
```

Standalone deliverables are additional artifacts produced after the research
contract and quality gates are complete.

## Artifact Layout

Use this layout for standalone runs:

```text
{OUTPUT_DIR}/
  legal-research-agent-result.md
  legal-research-agent-meta.json
  standalone-deliverable-manifest.json
  deliverables/
    {YYYYMMDD}_{slug}_{mode}_{language}_v{N}.md
    {YYYYMMDD}_{slug}_{mode}_{language}_v{N}.docx
    {YYYYMMDD}_{slug}_{mode}_{language}_v{N}.docx.render.json
    {YYYYMMDD}_{slug}_{mode}_{language}_v{N}.audit.md
```

The `.docx` and `.docx.render.json` files are generated only when binary DOCX
rendering actually runs. The `.audit.md` sidecar is generated only when an audit
workflow actually runs. Do not create empty or implied sidecars.

## Naming Rules

Deliverable filenames must follow:

```text
{YYYYMMDD}_{slug}_{mode}_{language}_v{N}.md
```

Rules:

- `YYYYMMDD` is the local run date.
- `slug` is a short ASCII matter or question slug.
- `mode` is one of:
  - `standalone`
  - `handoff`
  - `docx-ready`
- `language` is one of:
  - `ko`
  - `en`
  - `bilingual`
- `v{N}` starts at `v1`.
- Never overwrite an existing deliverable. Increment the version instead.

Examples:

```text
20260506_kr-loot-box-probability_standalone_ko_v1.md
20260506_kr-loot-box-probability_docx-ready_ko_v2.md
20260506_jp-us-launch_handoff_en_v1.md
```

## Manifest

Every standalone run should include `standalone-deliverable-manifest.json`.

Required fields:

```json
{
  "workflow_version": "1.0",
  "case_id": "kr_loot_box_probability",
  "research_output_dir": ".",
  "deliverables": [
    {
      "mode": "standalone_markdown",
      "language": "ko",
      "path": "deliverables/20260506_kr-loot-box-probability_standalone_ko_v1.md",
      "meta_path": "legal-research-agent-meta.json",
      "result_path": "legal-research-agent-result.md",
      "audit": {
        "required": true,
        "status": "deterministic_smoke",
        "claim": "..."
      },
      "docx": {
        "status": "not_requested",
        "path": null,
        "render_report_path": null
      }
    }
  ]
}
```

`audit.status` values:

- `not_required`
- `not_run_session_unavailable`
- `deterministic_smoke`
- `live_passed`
- `live_failed`

Use `not_run_session_unavailable` when live verifier dispatch is unavailable in
the current Claude Code session. Do not call that a passed audit.

`docx.status` values:

- `not_requested`
- `not_generated`
- `generated`
- `generated_and_extracted`

Use `generated_and_extracted` only when the generated DOCX has been extracted
again and material source anchors survived extraction.

## Workflow Steps

1. Research output
   - Produce `legal-research-agent-result.md`.
   - Produce `legal-research-agent-meta.json`.
   - Preserve source IDs, issue map, key findings, coverage gaps, and handoffs.
2. Research validation
   - Run `scripts/validate-output.py`.
   - Run `scripts/check-result-structure.py`.
   - Run `scripts/evaluate-quality.py` with the relevant case spec when
     available.
3. Formatting
   - Apply `skills/legal-writing-formatter.md`.
   - Load only the selected profile from `knowledge/legal-writing/`.
   - For `docx_ready_markdown`, also load
     `knowledge/legal-writing/docx-ready-markdown-profile.md`.
4. Formatter validation
   - Run `scripts/check-formatter-output.py`.
   - Fix missing sections, source-table drift, unanchored material paragraphs,
     hidden coverage gaps, and handoff omissions before delivery.
5. Binary DOCX generation, when requested
   - Run `scripts/render-docx.py` on the validated Markdown deliverable.
   - Save the render report next to the DOCX when possible.
   - Run DOCX extraction with `citation_auditor.docx` or
     `scripts/check-docx-generation.py` for the local fixture path.
   - Treat the DOCX as MVP rendering: headings, simple tables, lists, block
     quotes, and visible text are supported; native footnotes, tracked changes,
     comments, and complex page layout are not.
6. Citation audit
   - Run citation audit on the formatted deliverable, not only on the internal
     result memo, when the deliverable is intended for external or client-facing
     use.
   - Deterministic smoke confirms local integration only.
   - Live verifier audit, when available, is the meaningful final-deliverable
     audit.
7. Finalization
   - Record all generated deliverables in the manifest.
   - Record DOCX generation and extraction status when a binary was requested.
   - Record whether audit was live, deterministic-only, not required, or not
     available.
   - Do not label the output final if a required audit failed or was not run.

## Citation Audit Integration

Run the audit after formatter validation and before external delivery.

The citation audit does not replace the source-first legal research quality
gates. It checks whether formatted claims remain connected to evidence and
source anchors. If the audit flags a material unsupported claim, return to the
formatter or research step rather than editing only the audit report.

For `docx_ready_markdown`, audit the Markdown source before any later DOCX
conversion. If binary DOCX generation is added later, audit the DOCX extraction
report as a separate post-conversion check.

Binary DOCX generation is currently implemented by `scripts/render-docx.py`.
For external delivery, audit the Markdown source first, then extract the DOCX and
verify that material source anchors and source-table text survived conversion.

## Completion Criteria

A standalone deliverable is complete only when:

- research output contract exists;
- research quality gates pass or limitations are explicitly marked;
- formatted deliverable passes `check-formatter-output.py`;
- manifest points to every deliverable;
- binary DOCX, when requested, was rendered and extracted without losing
  material source anchors;
- required audit status is `live_passed` or the output is clearly marked as
  draft/source-limited with `not_run_session_unavailable`;
- no build log, planning note, private matter file, or generated report is
  staged for commit.
