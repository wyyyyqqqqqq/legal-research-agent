---
description: Run a source-first legal research task using the legal-research-agent workflow.
argument-hint: "<jurisdiction or topic> <question text>"
---

Run the legal-research-agent workflow described in `CLAUDE.md` for the user
question in `$ARGUMENTS`.

If `$ARGUMENTS` is empty, ask the user for:

- the legal question;
- jurisdiction(s) when relevant;
- whether they want a research-contract result only, a polished standalone
  memo, a handoff packet, or DOCX-ready Markdown.

When the user wants a standalone deliverable, follow
`docs/standalone-workflow.md` and apply
`skills/legal-writing-formatter.md` after the two contract files are
complete. Do not promise advanced DOCX features beyond MVP rendering.
