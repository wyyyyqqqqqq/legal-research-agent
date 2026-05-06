#!/usr/bin/env python3
"""Validate orchestrator-to-legal-research-agent intake payloads."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CANONICAL_RESEARCH_MODES = {"general", "game_regulation", "game_plus_general", "fallback"}
COMPOSITE_ROUTE_MODES = {"game_and_data_protection"}
ACTIVE_PROFILES = {"merged"}
CLASSIFICATION_CONFIDENCE = {"high", "medium", "low", "uncertain"}
LEGACY_AGENT_IDS = {"general-legal-research", "game-legal-research"}
CANONICAL_AGENT_ID = "legal-research-agent"
DATA_PROTECTION_DOMAINS = {"data_protection", "privacy"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_string_list(
    data: dict[str, Any],
    key: str,
    required: bool = True,
    allow_empty: bool = False,
) -> list[str]:
    errors: list[str] = []
    if key not in data:
        if required:
            errors.append(f"{key}: missing")
        return errors

    value = data[key]
    if not isinstance(value, list):
        return [f"{key}: expected list"]
    if not value and not allow_empty:
        return [f"{key}: expected non-empty list"]

    for index, item in enumerate(value):
        if not non_empty_string(item):
            errors.append(f"{key}[{index}]: expected non-empty string")
    return errors


def normalized_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def validate_agents(payload: dict[str, Any], key: str) -> list[str]:
    errors = validate_string_list(payload, key, required=False, allow_empty=True)
    agents = normalized_list(payload.get(key, []))
    for legacy_id in sorted(LEGACY_AGENT_IDS & set(agents)):
        errors.append(f"{key}: must not include legacy agent {legacy_id!r}")
    if agents.count(CANONICAL_AGENT_ID) > 1:
        errors.append(f"{key}: duplicate {CANONICAL_AGENT_ID!r} entries must be deduplicated")
    return errors


def effective_research_mode(classification: dict[str, Any]) -> str | None:
    agent_mode = classification.get("agent_research_mode")
    if isinstance(agent_mode, str) and agent_mode in CANONICAL_RESEARCH_MODES:
        return agent_mode

    route_mode = classification.get("route_mode")
    if isinstance(route_mode, str) and route_mode in CANONICAL_RESEARCH_MODES:
        return route_mode

    return None


def validate_classification(classification: Any) -> list[str]:
    if not isinstance(classification, dict):
        return ["orchestrator_classification: expected object"]

    errors: list[str] = []
    errors.extend(validate_string_list(classification, "domains"))
    errors.extend(validate_string_list(classification, "jurisdictions"))

    route_mode = classification.get("route_mode")
    if not non_empty_string(route_mode):
        errors.append("orchestrator_classification.route_mode: expected non-empty string")
    elif route_mode not in CANONICAL_RESEARCH_MODES and route_mode not in COMPOSITE_ROUTE_MODES:
        errors.append(f"orchestrator_classification.route_mode: unsupported value {route_mode!r}")

    agent_mode = classification.get("agent_research_mode")
    if agent_mode is not None and agent_mode not in CANONICAL_RESEARCH_MODES:
        errors.append(
            "orchestrator_classification.agent_research_mode: "
            f"expected canonical research mode, got {agent_mode!r}"
        )

    if (
        isinstance(route_mode, str)
        and route_mode in CANONICAL_RESEARCH_MODES
        and isinstance(agent_mode, str)
        and agent_mode in CANONICAL_RESEARCH_MODES
        and route_mode != agent_mode
    ):
        errors.append(
            "orchestrator_classification: canonical route_mode and "
            "agent_research_mode must match"
        )

    if route_mode in COMPOSITE_ROUTE_MODES and agent_mode not in CANONICAL_RESEARCH_MODES:
        errors.append(
            "orchestrator_classification: composite route_mode requires "
            "canonical agent_research_mode"
        )

    confidence = classification.get("confidence")
    if confidence is not None and confidence not in CLASSIFICATION_CONFIDENCE:
        errors.append(f"orchestrator_classification.confidence: invalid value {confidence!r}")

    return errors


def validate_payload(payload: Any, allow_self_classified: bool = False) -> list[str]:
    if not isinstance(payload, dict):
        return ["payload: expected object"]

    errors: list[str] = []
    for key in ("user_question", "output_dir", "active_profile"):
        if not non_empty_string(payload.get(key)):
            errors.append(f"{key}: expected non-empty string")

    active_profile = payload.get("active_profile")
    if non_empty_string(active_profile) and active_profile not in ACTIVE_PROFILES:
        errors.append(f"active_profile: expected one of {sorted(ACTIVE_PROFILES)}, got {active_profile!r}")

    if "orchestrator_classification" not in payload:
        if not allow_self_classified:
            errors.append("orchestrator_classification: missing")
    else:
        errors.extend(validate_classification(payload["orchestrator_classification"]))

    errors.extend(validate_agents(payload, "co_running_agents"))
    errors.extend(validate_agents(payload, "selected_agents"))

    classification = payload.get("orchestrator_classification")
    if isinstance(classification, dict):
        domains = set(normalized_list(classification.get("domains", [])))
        route_mode = classification.get("route_mode")
        mode = effective_research_mode(classification)
        co_running_agents = normalized_list(payload.get("co_running_agents", []))

        if domains & DATA_PROTECTION_DOMAINS or route_mode == "game_and_data_protection":
            if not co_running_agents:
                errors.append("co_running_agents: required for data-protection composite payloads")
            if mode != "game_regulation":
                errors.append(
                    "orchestrator_classification.agent_research_mode: "
                    "data-protection composite payloads should use game_regulation"
                )

    return errors


def expand_payload_paths(paths: list[Path]) -> list[Path]:
    expanded: list[Path] = []
    for path in paths:
        if path.is_dir():
            expanded.extend(sorted(path.glob("*.json")))
        else:
            expanded.append(path)
    return expanded


def validate_paths(paths: list[Path], allow_self_classified: bool = False) -> dict[str, Any]:
    payload_paths = expand_payload_paths(paths)
    results: list[dict[str, Any]] = []
    for path in payload_paths:
        if not path.exists():
            results.append({"path": str(path), "status": "fail", "errors": ["path: missing"]})
            continue
        try:
            payload = load_json(path)
            errors = validate_payload(payload, allow_self_classified=allow_self_classified)
        except Exception as exc:
            errors = [f"json: {exc}"]
        results.append({"path": str(path), "status": "fail" if errors else "pass", "errors": errors})

    failed = sum(1 for result in results if result["status"] == "fail")
    return {
        "status": "fail" if failed else "pass",
        "total": len(results),
        "failed": failed,
        "passed": len(results) - failed,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--allow-self-classified", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only.")
    args = parser.parse_args(argv)

    result = validate_paths(args.paths, allow_self_classified=args.allow_self_classified)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"Intake payloads: {result['status'].upper()} ({result['passed']}/{result['total']} passed)")
        for item in result["results"]:
            print(f"- {item['path']}: {item['status'].upper()}")
            for error in item["errors"]:
                print(f"  FAIL: {error}")

    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
