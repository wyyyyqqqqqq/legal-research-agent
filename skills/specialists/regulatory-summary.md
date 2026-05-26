---
name: regulatory-summary
description: Generates structured, citation-grounded summaries of regulatory documents (agency rules, guidance, enforcement actions, compliance frameworks). Extracts provisions, requirements, deadlines, penalties, safe harbors, and compliance actions with pinpoint citations. Use when summarizing regulations, rulemaking notices, enforcement orders, or administrative decisions.
disable-model-invocation: true
---

# Regulatory Document Summarization

Produces a structured summary of regulatory documents grounded in pinpoint citations, serving as both a standalone reference and a compliance roadmap.

Use this file as the compact workflow. Load
`references/packs/regulatory-summary.md` when drafting, tailoring, or
quality-checking a regulatory summary, or when document-type handling,
provision extraction, deadline tracking, safe-harbor analysis, enforcement
tables, or procedural-posture checks are needed.

## Quick Start

1. Collect the regulatory document(s) — final/proposed rules, guidance, enforcement actions, no-action letters, compliance frameworks, or administrative decisions
2. Note any available context: client industry, compliance posture, specific questions
3. Generate summary following the output structure below

## Output Structure

### 1. Executive Overview (2–3 sentences)

- Issuing authority, document type, core purpose
- Most significant takeaway
- Effective date or comment deadline

### 2. Document Metadata

| Field | Detail |
|---|---|
| Issuing Agency | |
| Document Type | Final rule / Proposed rule / Guidance / Enforcement / Other |
| Citation / Docket No. | |
| Effective Date | |
| Comment Deadline | (if applicable) |
| Compliance Deadline(s) | |
| Regulated Entities | |
| Supersedes / Amends | |

### 3. Key Provisions

| # | Provision | Requirement / Prohibition | Citation (§, ¶, p.) | Compliance Action |
|---|---|---|---|---|
| 1 | | | | |

- Quote operative definitions and critical language verbatim
- Flag ambiguity or discretionary interpretation with `[AMBIGUOUS]`

### 4. Changes from Prior Framework

| Area | Prior Rule | New Rule | Impact |
|---|---|---|---|

Omit if document does not amend a prior framework.

### 5. Safe Harbors & Exemptions

- Each safe harbor, exemption, or de minimis threshold with citation
- Qualifying conditions

### 6. Enforcement & Penalties

| Violation Type | Penalty Range | Enforcement Mechanism | Citation |
|---|---|---|---|

### 7. Cross-References

- **[Citation]** — relevance to this document

### 8. Compliance Action Items

| Priority | Action | Deadline | Notes |
|---|---|---|---|
| Immediate | | | |
| Near-term | | | |
| Ongoing | | | |

### 9. Open Questions & Ambiguities

- Unclear or interpretation-dependent regulatory text
- Expected future guidance or rulemaking
- Issues requiring specialist follow-up

## Guardrails

- **Source-grounded**: Never infer requirements absent from the document
- **Pinpoint citations**: Section, paragraph, or page for every substantive claim
- **Verbatim quoting**: Definitions, operative requirements, deadlines
- **Plain language**: Pair with technical regulatory terminology
- **`[AMBIGUOUS]` flag**: Mark interpretive uncertainty — do not guess agency intent
- **Scale appropriately**: ~1 page for simple guidance, up to ~3 pages for complex final rules
- **Procedural posture**: Note NPRM, interim final rule, or final rule when part of broader rulemaking
- **Analytical neutrality**: Do not editorialize on policy merits

## Reference Pack

- `references/packs/regulatory-summary.md` - document-type matrix, metadata
  table, provision extraction template, prior-framework delta, deadline
  tracker, safe harbors, enforcement/penalty tables, action plan, checklist,
  and pitfalls.
