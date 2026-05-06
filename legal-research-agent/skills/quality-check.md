# Quality Check

Run this check before finalizing result and metadata.

## Quality Supremacy

Token savings never compensate for legal-quality regression. If the answer needs
more source collection, claim verification, or analysis to avoid a material
omission, do the extra work and record why.

## Contract Check

- Result file exists.
- Metadata file exists.
- Required metadata fields are present.
- Metadata validates with `scripts/validate-output.py` when possible.
- Result memo structure validates with `scripts/check-result-structure.py` when
  possible.

## Source Check

- No invented source IDs.
- Every key finding maps to at least one source.
- Every `key_findings[*]` item cites at least one known `sources[*].id`.
- Every `issue_map[*].authority_ids` entry exists in `sources[*].id`.
- Source grades are valid.
- Controlling legal propositions use primary or official sources where
  reasonably available.
- Every material legal anchor was spot-checked or explicitly marked unverified.
- `claim_checks` is internally consistent when present.
- Every `claim_checks[*].authority_ids[*]` entry exists in `sources[*].id`.
- Every high-confidence issue has at least one direct claim check when
  `claim_checks` is present.
- `background` and `unsupported` claim checks do not carry high-confidence
  conclusions.
- Temporal status is checked for statutes, regulations, and agency rules.
- `sources[*].currentness` uses `currentness-check.md` status values when
  present.
- High confidence is blocked when controlling authority is only
  `not_checked`, `pending_change`, or `stale_or_superseded`.
- Pending, stale, superseded, or unchecked controlling sources require a visible
  caveat or a `temporal_status` coverage gap.
- Source laundering risks are resolved, re-attributed, or marked `[Unverified]`.
- Grade C does not alone support a high-confidence conclusion.
- Grade D is not cited for legal propositions.

## Mode Check

- `research_mode` follows orchestrator classification unless unavailable or
  uncertain.
- `mode_source` is set.
- `classification_mismatch` is recorded if route and question diverge.
- `fallback_reason` is populated for fallback results.
- `coverage_gaps` is populated when `error` is non-null or mode is `fallback`.
- Each coverage gap has a type and a concrete description.
- High confidence is not allowed when the output has a fallback mode, non-null
  error, or material coverage gap such as source coverage, source access,
  jurisdiction, temporal status, or classification mismatch.

## Game Check

For game-regulation results:

- Relevant taxonomy categories are covered.
- Adjacent law does not sprawl beyond the game question.
- Privacy is a handoff issue when data-protection specialists are co-running.
- Multi-jurisdiction answers include jurisdiction-specific findings and
  synthesis.

## Practical Check

- The memo answers the user question directly.
- Source limitations and coverage gaps are explicit.
- Confidence levels are conservative where sources are incomplete.
- No material issue is omitted merely to keep the memo short.
