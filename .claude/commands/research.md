---
description: Run a source-first legal research task using the legal-research-agent workflow.
argument-hint: "<jurisdiction or topic> <question text> [mode=executive_brief|comparative_matrix|enforcement_case_law|black_letter_commentary|canonical]"
---

Run the legal-research-agent workflow described in `CLAUDE.md` for the user
question in `$ARGUMENTS`.

If `$ARGUMENTS` is empty, ask the user for:

- the legal question;
- jurisdiction(s) when relevant;
- whether they want a research-contract result only, a polished standalone
  memo, a handoff packet, or DOCX-ready Markdown;
- the desired output mode (`executive_brief`, `comparative_matrix`,
  `enforcement_case_law`, `black_letter_commentary`, or `canonical`)
  when a standalone deliverable is requested.

When the user wants a standalone deliverable, follow
`docs/standalone-workflow.md` and apply
`skills/legal-writing-formatter.md` after the two contract files are
complete. Do not promise advanced DOCX features beyond MVP rendering.

If the user names a mode (e.g. `mode=comparative_matrix`), apply
`skills/output-mode-composition.md` after the canonical research record
is complete and use the matching template under `templates/output-modes/`.
The orchestrator-compatible `legal-research-agent-result.md` keeps its
9-section structure regardless of the selected mode; the mode-shaped
deliverable is written separately under `deliverables/` and recorded in
`standalone-deliverable-manifest.json`.
