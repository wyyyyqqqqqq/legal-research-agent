# Legal Writing Formatter Index

This directory contains compact formatter profiles for standalone
`legal-research-agent` deliverables.

Use these profiles only after the research output contract is complete, or when
the user explicitly asks for a standalone legal research memo, opinion-style
note, client-ready research summary, or DOCX-ready Markdown source.

## Selection Rule

| Requested Output | Load |
|---|---|
| Korean legal research memo or opinion-style note (non-DOCX) | `ko-formatter-profile.md` |
| Korean polished legal-opinion DOCX deliverable | `ko-legal-opinion-profile.md` (paired with `scripts/render-legal-opinion-docx.py`) |
| English legal research memo | `en-formatter-profile.md` |
| Bilingual deliverable | Load both profiles only for the final formatting step |
| DOCX-ready Markdown (general) | Selected language profile plus `docx-ready-markdown-profile.md` |
| Orchestrator-only research output | Do not load formatter profiles |

For Korean DOCX deliverables, the default routing is `ko-legal-opinion-profile.md`
because it pairs with the polished renderer (`scripts/render-legal-opinion-docx.py`)
that supplies cover page, hierarchical numbering, statutory block quotes,
superscript footnote markers, and a master 각주 (Endnotes) section. Override to
`ko-formatter-profile.md` for quick drafts, internal memos, or handoff packets.

Do not load both profiles by default. Do not load any broad bilingual formatting
guide by default.

## Formatter Boundary

The formatter may reorganize, compress, and polish the completed research
result. It may not:

- create new legal conclusions;
- add authorities not present in the research output;
- hide coverage gaps or fallback limits;
- remove source IDs needed for auditability;
- duplicate specialist analysis delegated to another agent.

For source-first quality, the formatted deliverable must remain auditable back
to `legal-research-agent-result.md` and `legal-research-agent-meta.json`.
