**Language:** [한국어](../ko/mcp-setup-guide.md) | [**English**](mcp-setup-guide.md)

# MCP Setup Guide

> **[README](../../README.md)** | **[How to Use](how-to-use.md)** | **[Disclaimer](disclaimer.md)**

This guide covers the Model Context Protocol (MCP) setup
`legal-research-agent` actually depends on. The agent is designed to
degrade gracefully when MCP is unavailable — see [Degradation Behavior](#degradation-behavior).

## Korean Law MCP Server

The `korean-law` MCP server provides 60+ native tools backed by the
Korean Open Law API at law.go.kr (statutes, enforcement decrees,
ministerial rules, court decisions, agency interpretations, tribunal
decisions, and chain-research workflows). It is the controlling primary
source path for `general` mode in Korean and for the Korean leg of
`game_regulation` mode.

The agent calls these tools with the namespaced prefix
`mcp__claude_ai_Korean-law__*`, which is how Claude.ai surfaces an
MCP server registered against the user's Claude account.

### Two ways to register

| Path | Best for | How to set up |
|:---|:---|:---|
| Claude.ai-managed | Standalone use on Claude Code with a Claude.ai account | Add the `korean-law` server in your Claude.ai integrations panel; the agent automatically sees `mcp__claude_ai_Korean-law__*` tools |
| Self-hosted via `.mcp.json` | Air-gapped or self-hosted setups; orchestrator integration | Place an `.mcp.json` at the repo root pointing at the upstream `korean-law-mcp` package |

This repository does not commit a personal `.mcp.json` because the
recommended path is the Claude.ai-managed integration.

## Configuration

### Claude.ai-managed (recommended)

1. Open the Claude.ai integrations or connectors panel.
2. Add the **Korean Law** MCP server.
3. Authenticate with your Open Law API OC key when prompted. Your OC key
   is the local-part of the email ID registered at
   <https://open.law.go.kr/> (free signup).
4. Restart Claude Code so the MCP connection is picked up cleanly.

The agent will see tools such as
`mcp__claude_ai_Korean-law__search_law`,
`mcp__claude_ai_Korean-law__get_law_text`, and
`mcp__claude_ai_Korean-law__chain_full_research`.

### Self-hosted alternative

If you need the same toolset without the Claude.ai-managed path, place
an `.mcp.json` at the repo root:

```json
{
  "mcpServers": {
    "korean-law": {
      "command": "npx",
      "args": ["-y", "korean-law-mcp@latest"],
      "env": {
        "LAW_OC": "your_openlaw_oc"
      }
    }
  }
}
```

Replace `your_openlaw_oc` with your own OC key locally. Do not commit
personal identifiers. With self-hosted MCP, tools surface under a
different namespace (e.g. `mcp__korean-law__search_law`); update the
allowlist in `.claude/settings.json` accordingly.

## Verification

After setup, verify the connection:

1. Restart Claude Code.
2. In a new session, ask a Korean-law question. The agent should call
   `mcp__claude_ai_Korean-law__*` tools (visible in the tool-call log).
3. Or, run the local preflight:

   ```bash
   python3 scripts/run-local-checks.py
   ```

   The preflight does not call MCP tools (it must work offline). It
   does verify that the agent's settings allowlist is well-formed via
   `scripts/check-claude-conventions.py`.

## Degradation Behavior

When the `korean-law` MCP server is unavailable, the agent degrades
gracefully rather than fabricating Korean primary law:

| Condition | Agent behavior |
|:---|:---|
| MCP fully available | Use MCP for statutes, decrees, decisions, and chain workflows |
| MCP unavailable | Fall back to `WebSearch` and `WebFetch` against `law.go.kr` and `supremecourt.go.kr`; lower confidence; record `mcp_unavailable` |
| Material limitation | Add a `coverage_gaps` entry of type `source_access` with a concrete description |
| Critical Korean primary-source coverage missing | Set `error` to `mcp_unavailable` or `partial_sources`; do not produce high-confidence conclusions on secondary sources alone |

Vocabulary and rules live in `skills/source-collection.md` (Korean Law
Strategy) and `skills/output-contract.md` (Error Vocabulary).

## Troubleshooting

| Symptom | Likely cause | Fix |
|:---|:---|:---|
| No `mcp__claude_ai_Korean-law__*` tools visible | MCP not registered or session not restarted | Re-add in Claude.ai integrations panel; restart Claude Code |
| `401`/`403` from MCP | OC key missing or invalid | Re-enter the OC key; verify at <https://open.law.go.kr/> |
| Permission prompt every Korean-law call | `.claude/settings.json` allowlist missing the namespace | Confirm `mcp__claude_ai_Korean-law__*` is present; if self-hosted, update the prefix |
| Tools time out on chain workflows | Underlying API throttling | Retry; chain calls run in parallel, occasional throttling is expected |
| Output records `mcp_unavailable` even when MCP works | Naming mismatch between Claude.ai-managed and self-hosted prefixes | Verify the actual tool prefix the agent invokes against the allowlist |

## Other MCP Servers

`legal-research-agent` does not require any other MCP server. The
vendored [`citation-auditor`](../../citation_auditor/) skill dispatches
verifier subagents that may call MCP tools when available, but the
standalone deterministic smoke
(`scripts/check-citation-auditor-smoke.py`) does not depend on any MCP
server.

### Optional MCP Servers (when available)

These are not required, but the agent will use them when registered:

| MCP Server | Toolset prefix | Purpose | Status |
|:---|:---|:---|:---|
| `markitdown` | `mcp__markitdown__convert_to_markdown` | PDF / DOCX / PPTX / XLSX / HTML → Markdown for source ingestion | Recommended; allowlisted in `.claude/settings.json` |
| `eur-lex` (community) | `mcp__eur-lex__*` (when registered) | EUR-Lex SOAP/REST → consolidated text, effective dates | Plug-in pattern; the agent currently uses `WebFetch` against `eur-lex.europa.eu` |
| `us-law` (community) | `mcp__us-law__*` or similar | Congress.gov, eCFR, Federal Register, CourtListener | Plug-in pattern; not widely available as of 2026-05 |

**Plug-in pattern.** When you add a new MCP server in your Claude.ai
integrations panel or `.mcp.json`, also add its toolset prefix to the
`permissions.allow` list in `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "mcp__claude_ai_Korean-law__*",
      "mcp__markitdown__*",
      "mcp__eur-lex__*"
    ]
  }
}
```

The agent's source-collection skill (`skills/source-collection.md`)
already prefers MCP-backed retrieval over `WebFetch` when the server is
present. For Korean primary law, the dedicated Korean Law strategy
applies; for other jurisdictions, the agent falls back to `WebSearch`
and `WebFetch` against the whitelisted official portals listed in the
project README.

### When NOT to add an MCP server

- Subscription-gated tools (e.g., commercial legal-AI platforms) only
  add value if every team member has a seat. Otherwise the agent
  produces inconsistent results across users.
- General-purpose web-search MCPs (`tavily`, `brave`) are largely
  redundant with `WebSearch` and `WebFetch` for legal research; add
  them only when you have a specific reason (rate limits, regional
  blocking, etc.).

For the standalone deliverable workflow (DOCX rendering, citation audit
sequencing, manifest validation), see
[`docs/standalone-workflow.md`](../standalone-workflow.md).
