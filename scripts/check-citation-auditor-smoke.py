#!/usr/bin/env python3
"""Run a deterministic citation-auditor smoke test on a legal result fixture."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from citation_auditor.aggregation import aggregate_verdicts
from citation_auditor.chunking import chunk_markdown
from citation_auditor.models import AuditReason, Claim, ClaimType, Evidence, SentenceSpan, Verdict, VerdictLabel
from citation_auditor.render import render_markdown


DEFAULT_RESULT = ROOT / "tests" / "fixtures" / "output" / "valid" / "legal-research-agent-result.md"
SMOKE_CLAIM = "This fixture uses src_001 as the official-source marker."


def run_smoke(result_path: Path = DEFAULT_RESULT, claim_text: str = SMOKE_CLAIM) -> list[str]:
    errors: list[str] = []
    if not result_path.exists():
        return [f"missing result fixture: {result_path}"]

    md_text = result_path.read_text(encoding="utf-8")
    chunks = chunk_markdown(md_text, max_tokens=3000)
    if not chunks:
        errors.append("citation-auditor chunking produced no chunks")

    start = md_text.find(claim_text)
    if start == -1:
        errors.append(f"smoke claim not found in result fixture: {claim_text!r}")
        return errors
    end = start + len(claim_text)

    if not any(
        segment.document_start <= start and end <= segment.document_end
        for chunk in chunks
        for segment in chunk.segments
    ):
        errors.append("smoke claim span is not covered by a citation-auditor chunk segment")

    claim = Claim(
        text=claim_text,
        sentence_span=SentenceSpan(start=start, end=end),
        claim_type=ClaimType.CITATION,
        suggested_verifier="local-smoke",
        audit_reason=AuditReason.CITATION,
    )
    lower_authority_candidate = Verdict(
        claim=claim,
        label=VerdictLabel.UNKNOWN,
        verifier_name="low-authority-smoke",
        authority=0.1,
        rationale="Lower-authority candidate used to verify aggregation ordering.",
        evidence=[],
    )
    higher_authority_candidate = Verdict(
        claim=claim,
        label=VerdictLabel.VERIFIED,
        verifier_name="local-smoke",
        authority=0.9,
        rationale="Deterministic smoke verdict; no live source verification performed.",
        evidence=[
            Evidence(
                url="tests/fixtures/output/valid/legal-research-agent-result.md",
                title="Local valid legal research fixture",
            )
        ],
    )

    aggregated = aggregate_verdicts(claim, [lower_authority_candidate, higher_authority_candidate])
    if aggregated.label != VerdictLabel.VERIFIED:
        errors.append(f"aggregation selected unexpected label: {aggregated.label!r}")
    if aggregated.verifier_name != "local-smoke":
        errors.append(f"aggregation selected unexpected verifier: {aggregated.verifier_name!r}")

    rendered = render_markdown(md_text, [aggregated])
    expected_badge = "**[✅ local-smoke]**"
    if expected_badge not in rendered:
        errors.append(f"rendered markdown missing audit badge {expected_badge!r}")
    if "## Audit Report" not in rendered:
        errors.append("rendered markdown missing Audit Report section")
    if claim_text not in rendered:
        errors.append("rendered markdown missing smoke claim text")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--claim", default=SMOKE_CLAIM)
    args = parser.parse_args(argv)

    errors = run_smoke(args.result, args.claim)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: citation-auditor deterministic smoke valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
