# Legal Research Agent

`legal-research-agent` is the merged legal research specialist for the KP Legal
Orchestrator.

It consolidates the previous general and game-regulation research roles into one
canonical Claude Code agent while preserving mode-specific behavior and the
existing orchestrator output contract.

## Goals

- Preserve source-first legal research quality.
- Keep game-regulation expertise explicit through a dedicated mode and taxonomy.
- Avoid wrapper calls to legacy research agents.
- Produce orchestrator-compatible result and metadata files.
- Support legacy-vs-merged golden-set evaluation before default rollout.

Token reduction is a secondary optimization. It matters only when the merged
agent preserves or improves legal research quality.

## Runtime Contract

Required output files:

```text
{OUTPUT_DIR}/legal-research-agent-result.md
{OUTPUT_DIR}/legal-research-agent-meta.json
```

The metadata contract is additive. Existing orchestrator readers should continue
to rely only on:

- `summary`
- `issue_map`
- `key_findings`
- `sources`
- `error`

## Modes

- `general`: ordinary legal research where no narrower specialist is required.
- `game_regulation`: game-industry regulation and adjacent game-law issues.
- `game_plus_general`: game-industry question plus a distinct non-game legal
  issue.
- `fallback`: ambiguous, undersourced, or out-of-scope research where a
  conservative memo is still useful.

## Key Design Rules

- Orchestrator classification is primary.
- Use `agent_research_mode` when provided; otherwise use canonical `route_mode`.
- Do not silently override a conflicting route. Record
  `classification_mismatch`.
- Deduplicated merged-agent routes should dispatch this agent at most once per
  route branch.
- When data-protection specialists are co-running, this agent performs privacy
  handoff and game-law framing, not duplicate deep privacy analysis.
- Do not save tokens by skipping material issue spotting, current-law checks,
  primary-source verification, or citation integrity checks.

## Local Checks

Run the full local preflight:

```bash
python3 scripts/run-local-checks.py
python3 scripts/run-local-checks.py --report
```

Individual checks:

```bash
python3 scripts/smoke-check.py
python3 scripts/check-fixture-consistency.py
python3 tests/test_output_contract.py
python3 tests/test_quality_evaluation.py
python3 tests/test_golden_set_evaluation.py
python3 tests/test_knowledge_coverage.py
python3 tests/test_result_structure.py
python3 tests/test_run_local_checks.py
python3 tests/test_fixture_consistency.py
python3 tests/test_citation_auditor_vendor.py
python3 tests/test_citation_auditor_smoke.py
python3 scripts/check-knowledge-coverage.py
python3 scripts/check-citation-auditor-vendor.py
python3 scripts/check-citation-auditor-smoke.py
python3 scripts/check-result-structure.py tests/fixtures/output/valid
python3 scripts/evaluate-golden-set.py
python3 scripts/measure-tokens.py path/to/events.jsonl
bash tests/lint_no_legacy_invocation.sh
```

`scripts/validate-output.py` validates a generated output directory:

```bash
python3 scripts/validate-output.py /path/to/output
```

Use `--schema /path/to/orchestrator/schemas/agent-meta.schema.json` when the
orchestrator repository is available.

`scripts/evaluate-quality.py` checks legal-quality gates beyond JSON shape:

```bash
python3 scripts/check-result-structure.py /path/to/output
python3 scripts/evaluate-quality.py /path/to/output \
  --case-spec tests/fixtures/quality/kr_loot_box-quality-spec.json
```

Quality evaluation is mandatory before comparing token savings.

`scripts/evaluate-golden-set.py` runs all local golden-set quality specs against
their matching output directories:

```bash
python3 scripts/evaluate-golden-set.py
python3 scripts/evaluate-golden-set.py --case-id kr_general_basic
```

## Citation Auditor Vendor

`citation-auditor` is vendored into this agent rather than symlinked:

```text
.claude/commands/audit.md
.claude/skills/citation-auditor/
.claude/skills/verifiers/
citation_auditor/
```

The vendor stamp is `.claude/skills/citation-auditor/VENDOR.md`. Refresh it
from the sibling source repo only when intentionally upgrading:

```bash
../citation-auditor/scripts/vendor-into.sh "$PWD"
```

The local preflight checks the vendored file set, runs a CLI help smoke test,
and runs a deterministic chunk/aggregate/render smoke against a legal research
result fixture. Live verifier dispatch and web/MCP-backed audits are not part
of preflight because they depend on the surrounding Claude Code session.
