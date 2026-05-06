#!/usr/bin/env python3
"""Check Claude Code conventions: skill frontmatter, subagent definition,
settings allowlist, slash command, CLAUDE.md prerequisites, and AGENTS.md
shim. Designed to fail loudly with one error line per missing surface so the
scaffolding plan can be applied incrementally."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SKILLS_DIR = ROOT / "skills"
AGENT_FILE = ROOT / ".claude" / "agents" / "legal-research-agent.md"
SETTINGS_FILE = ROOT / ".claude" / "settings.json"
COMMAND_FILE = ROOT / ".claude" / "commands" / "research.md"
CLAUDE_FILE = ROOT / "CLAUDE.md"
AGENTS_FILE = ROOT / "AGENTS.md"

REQUIRED_AGENT_TOOLS = {
    "Read",
    "Write",
    "Edit",
    "Bash",
    "Grep",
    "Glob",
    "WebFetch",
    "WebSearch",
    "Task",
}

DESCRIPTION_MIN_CHARS = 30


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Tiny YAML-frontmatter parser. Returns None when no frontmatter is
    present. Returns a flat ``dict[str, str]`` mapping for scalar values.
    Inline list values (e.g. ``tools: [Read, Write]``) are returned as
    comma-joined raw strings; callers split as needed."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    collected: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return collected
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        collected[key.strip()] = value.strip()
    return None


def split_inline_list(value: str) -> list[str]:
    raw = value.strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    return [item.strip().strip("'\"") for item in raw.split(",") if item.strip()]


def check_skills(root: Path) -> list[str]:
    errors: list[str] = []
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return [f"skills/: directory missing"]
    for path in sorted(skills_dir.glob("*.md")):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        front = parse_frontmatter(text)
        if front is None:
            errors.append(f"{rel}: missing YAML frontmatter")
            continue
        name = front.get("name", "")
        description = front.get("description", "")
        dmi = front.get("disable-model-invocation", "")
        expected_name = path.stem
        if name != expected_name:
            errors.append(
                f"{rel}: frontmatter name {name!r} does not match filename "
                f"stem {expected_name!r}"
            )
        if len(description) < DESCRIPTION_MIN_CHARS:
            errors.append(
                f"{rel}: frontmatter description must be at least "
                f"{DESCRIPTION_MIN_CHARS} characters (got {len(description)})"
            )
        if dmi.lower() != "true":
            errors.append(
                f"{rel}: frontmatter disable-model-invocation must be true "
                f"(got {dmi!r})"
            )
    return errors


def check_agent_definition(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / ".claude" / "agents" / "legal-research-agent.md"
    rel = path.relative_to(root).as_posix()
    if not path.exists():
        return [f"{rel}: file missing"]
    text = path.read_text(encoding="utf-8")
    front = parse_frontmatter(text)
    if front is None:
        return [f"{rel}: missing YAML frontmatter"]
    if front.get("name", "") != "legal-research-agent":
        errors.append(
            f"{rel}: frontmatter name must be 'legal-research-agent' "
            f"(got {front.get('name', '')!r})"
        )
    description = front.get("description", "")
    if len(description) < DESCRIPTION_MIN_CHARS:
        errors.append(
            f"{rel}: frontmatter description must be at least "
            f"{DESCRIPTION_MIN_CHARS} characters (got {len(description)})"
        )
    tools_raw = front.get("tools", "")
    if not tools_raw:
        errors.append(f"{rel}: frontmatter tools must be present and non-empty")
    else:
        tools = set(split_inline_list(tools_raw))
        missing = REQUIRED_AGENT_TOOLS - tools
        if missing:
            errors.append(
                f"{rel}: frontmatter tools missing required entries: "
                f"{sorted(missing)}"
            )
    return errors


def check_settings(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / ".claude" / "settings.json"
    rel = path.relative_to(root).as_posix()
    if not path.exists():
        return [f"{rel}: file missing"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{rel}: invalid JSON ({exc})"]
    permissions = data.get("permissions", {})
    if not isinstance(permissions, dict):
        return [f"{rel}: permissions must be an object"]
    allow = permissions.get("allow", [])
    if not isinstance(allow, list):
        return [f"{rel}: permissions.allow must be a list"]
    has_scripts_bash = any(
        isinstance(item, str) and item.startswith("Bash(python3 scripts/")
        for item in allow
    )
    has_tests_bash = any(
        isinstance(item, str) and item.startswith("Bash(python3 tests/")
        for item in allow
    )
    has_webfetch = "WebFetch" in allow
    has_websearch = "WebSearch" in allow
    has_korean_law_mcp = any(
        isinstance(item, str) and item.startswith("mcp__claude_ai_Korean-law__")
        for item in allow
    )
    if not has_scripts_bash:
        errors.append(
            f"{rel}: permissions.allow missing any 'Bash(python3 scripts/*)' entry"
        )
    if not has_tests_bash:
        errors.append(
            f"{rel}: permissions.allow missing any 'Bash(python3 tests/*)' entry"
        )
    if not has_webfetch:
        errors.append(f"{rel}: permissions.allow missing 'WebFetch'")
    if not has_websearch:
        errors.append(f"{rel}: permissions.allow missing 'WebSearch'")
    if not has_korean_law_mcp:
        errors.append(
            f"{rel}: permissions.allow missing any "
            f"'mcp__claude_ai_Korean-law__*' entry"
        )
    return errors


def check_command(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / ".claude" / "commands" / "research.md"
    rel = path.relative_to(root).as_posix()
    if not path.exists():
        return [f"{rel}: file missing"]
    text = path.read_text(encoding="utf-8")
    front = parse_frontmatter(text)
    if front is None:
        return [f"{rel}: missing YAML frontmatter"]
    description = front.get("description", "")
    if len(description) < DESCRIPTION_MIN_CHARS:
        errors.append(
            f"{rel}: frontmatter description must be at least "
            f"{DESCRIPTION_MIN_CHARS} characters (got {len(description)})"
        )
    if not front.get("argument-hint", ""):
        errors.append(f"{rel}: frontmatter argument-hint must be present and non-empty")
    return errors


def check_prerequisites(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / "CLAUDE.md"
    rel = path.relative_to(root).as_posix()
    if not path.exists():
        return [f"{rel}: file missing"]
    text = path.read_text(encoding="utf-8")
    if "## Prerequisites" not in text:
        return [f"{rel}: missing '## Prerequisites' section"]
    section = text.split("## Prerequisites", 1)[1]
    next_heading = section.find("\n## ")
    if next_heading != -1:
        section = section[:next_heading]
    lower = section.lower()
    if "korean-law" not in lower:
        errors.append(
            f"{rel}: '## Prerequisites' must mention the 'korean-law' MCP server"
        )
    if "webfetch" not in lower and "websearch" not in lower:
        errors.append(
            f"{rel}: '## Prerequisites' must mention 'WebFetch' or 'WebSearch'"
        )
    return errors


def check_agents_md(root: Path) -> list[str]:
    path = root / "AGENTS.md"
    rel = path.relative_to(root).as_posix()
    if not path.exists() and not path.is_symlink():
        return [f"{rel}: file missing"]
    if path.is_symlink():
        target = os.readlink(path)
        target_path = (path.parent / target).resolve()
        if target_path != (root / "CLAUDE.md").resolve():
            return [
                f"{rel}: symlink must point at CLAUDE.md (resolves to "
                f"{target_path})"
            ]
        return []
    text = path.read_text(encoding="utf-8")
    first_line = next(
        (line.strip() for line in text.splitlines() if line.strip()),
        "",
    )
    if first_line != "@CLAUDE.md":
        return [
            f"{rel}: first non-empty line must be '@CLAUDE.md' "
            f"(got {first_line!r})"
        ]
    return []


CHECKS = [
    ("skills frontmatter", check_skills),
    ("subagent definition", check_agent_definition),
    ("settings allowlist", check_settings),
    ("research slash command", check_command),
    ("CLAUDE.md prerequisites", check_prerequisites),
    ("AGENTS.md shim", check_agents_md),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)

    all_errors: list[str] = []
    for label, fn in CHECKS:
        errors = fn(args.root)
        for error in errors:
            all_errors.append(f"[{label}] {error}")

    if all_errors:
        for line in all_errors:
            print(f"FAIL: {line}", file=sys.stderr)
        return 1
    print("OK: Claude Code conventions present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
