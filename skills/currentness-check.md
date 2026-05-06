---
name: currentness-check
description: Use whenever statutes, regulations, or agency guidance support a controlling proposition — prevents stale, pending, or superseded law from supporting confident answers.
disable-model-invocation: true
---

# Currentness Check

Use this skill whenever statutes, regulations, delegated rules, agency guidance,
official notices, cases, or agency decisions support a controlling proposition.

The goal is to prevent stale law, not-yet-effective law, pending amendments, or
superseded guidance from silently supporting a confident answer.

## Status Vocabulary

Use these values in `sources[*].currentness.status` when currentness metadata is
available:

- `checked_current`
- `effective_date_checked`
- `pending_change`
- `stale_or_superseded`
- `not_checked`
- `not_applicable`

Prefer `checked_current` for controlling law verified against an official
current source. Use `effective_date_checked` when the decisive question is
timing, transition, or commencement. Use `not_applicable` only for sources where
current legal force is not relevant, such as historical background or a
non-legal context source.

## Metadata Shape

Add currentness as an optional source-level field:

```json
{
  "id": "src_001",
  "title": "Official source title",
  "grade": "A",
  "citation": "Article 12",
  "pinpoint": "Article 12(1)",
  "url_or_access": "official database",
  "currentness": {
    "status": "checked_current",
    "checked_as_of": "2026-05-06",
    "effective_date": null,
    "notes": "Official current version checked."
  }
}
```

When status is `checked_current` or `effective_date_checked`,
`checked_as_of` must be present.

## Required Checks

For controlling authority:

1. Verify the current official version.
2. Check effective dates and supplementary or transitional provisions when
   timing matters.
3. Check pending amendments, repeals, consolidations, and supersession.
4. Check whether guidance, FAQs, notices, or enforcement positions have been
   replaced by newer material.
5. Carry any currentness uncertainty into `coverage_gaps` and issue confidence.

## Confidence Consequences

Do not mark an issue `high` confidence when all controlling authority sources
are `not_checked`, `pending_change`, or `stale_or_superseded`.

If a controlling authority source is `pending_change`, `stale_or_superseded`, or
`not_checked`, the result must include at least one of:

- a `coverage_gaps` entry with type `temporal_status`;
- visible limiting language in the result memo;
- a lower issue confidence that reflects the currentness problem.

## Visible Caveat Language

Use direct caveats rather than burying currentness uncertainty in metadata:

- source currentness not checked;
- pending amendment may change the answer;
- source appears stale or superseded;
- effective date must be verified;
- current official version should be confirmed before relying on this answer.

## Stop Conditions

Pause before finalizing a high-confidence issue when:

- the controlling source has no currentness check;
- the source has a pending amendment that may affect the answer;
- the source is stale or superseded;
- the effective date is uncertain;
- the answer turns on a transitional or supplementary provision that was not
  checked.

If the stop condition cannot be resolved in the current run, lower confidence
and record the temporal limitation.
