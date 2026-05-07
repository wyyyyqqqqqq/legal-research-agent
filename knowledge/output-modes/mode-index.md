# Output Mode Index

Maps each `output_mode` slug to its template, framework dependencies,
default packaging mode, and audience profile.

| Slug | Label | Template | Required Frameworks | Default Packaging | Audience |
|---|---|---|---|---|---|
| `executive_brief` | Executive Brief (Mode A) | `templates/output-modes/executive-brief.md` | counter-analysis | `standalone_markdown` | Decision-makers, C-suite |
| `comparative_matrix` | Comparative Matrix (Mode B) | `templates/output-modes/comparative-matrix.md` | counter-analysis, comparative-framework | `standalone_markdown` | Multi-jurisdiction compliance |
| `enforcement_case_law` | Enforcement and Case Law (Mode C) | `templates/output-modes/enforcement-case-law.md` | counter-analysis | `standalone_markdown` | Litigation, enforcement strategy |
| `black_letter_commentary` | Black-letter and Commentary (Mode D) | `templates/output-modes/black-letter-commentary.md` | counter-analysis | `docx_ready_markdown` | Statute or regulation deep dive |
| `canonical` | Canonical research memo | `templates/result.md` | (existing skill chain) | `standalone_markdown` | Orchestrator-compatible record |

## Selection Rules

- If the user explicitly names a mode (slug or label), use it.
- If the user requests "executive brief", "summary for executives", or
  similar, select `executive_brief`.
- If the user requests a comparison or asks about more than one
  jurisdiction with comparison framing, select `comparative_matrix`.
- If the user asks about enforcement, litigation, regulator decisions,
  or case law trends, select `enforcement_case_law`.
- If the user asks for an article-by-article analysis, statute deep
  dive, or regulatory commentary, select `black_letter_commentary`.
- Otherwise default to `canonical`.

If the user requests a `.docx` deliverable and does not name a mode,
default to `black_letter_commentary` plus `docx_ready_markdown` packaging.
