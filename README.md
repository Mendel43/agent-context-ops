# Agent Context Ops

Open-source toolkit for keeping AI coding agents grounded in real project context.

Agent Context Ops helps maintainers share durable context across tools such as Codex,
Claude Code, Hermes, Obsidian and local knowledge graphs without copying private
conversation history by hand.

## What it does

- Generates clean handoff files for another AI agent or coding session.
- Keeps operational notes, reports and decisions in Markdown.
- Provides a safe pattern for indexing code/project context with Graphify-style outputs.
- Encourages backup-first maintenance workflows.
- Separates public agent context from private secrets, `.env` files and commercial data.

## Why it exists

AI agents are powerful, but long-running projects lose time when every session starts
from zero. Maintainers need a lightweight way to preserve decisions, operational
status, useful commands, architecture notes and pending work in files that any agent
can read.

This project is designed for real-world maintainer workflows:

- issue and PR triage;
- release notes and changelog drafts;
- context recovery after long sessions;
- automation audits;
- safer handoffs between coding agents;
- project memory that lives in the repo, not only in chat history.

## Planned modules

- `context-pack`: builds a compact project state handoff.
- `obsidian-log`: writes structured Markdown reports to an Obsidian vault.
- `graph-check`: verifies whether the local knowledge graph is fresh.
- `backup-check`: checks whether critical files have recent backups.
- `agent-council`: records multi-agent reviews without giving agents write access.
- `scan-secrets`: scans for secret-looking content before sharing context.
- `init`: creates a minimal context structure in another repository.

## Install

```bash
pip install -e .
```

## Quick start

Generate a redacted handoff for another AI agent:

```bash
agent-context-ops context-pack --root . --output handoff.md
```

Check if a local knowledge graph is stale:

```bash
agent-context-ops graph-check --root . --graph graphify-out/graph.json
```

Check that critical files have backups:

```bash
agent-context-ops backup-check --root . --file pyproject.toml --backup-dir backups
```

Scan for secret-looking content:

```bash
agent-context-ops scan-secrets --root .
```

Write an operational note to an Obsidian vault:

```bash
echo "Release prep finished." | agent-context-ops obsidian-log \
  --vault /path/to/vault \
  --folder "AI Logs" \
  --title "Release prep"
```

Short alias:

```bash
aco context-pack --root .
```

## Development smoke test

```bash
make smoke
make scan
```

## Safety principles

- Never export secrets.
- Never include `.env` contents.
- Never mutate cron jobs or deployment configs without explicit command flags.
- Prefer read-only diagnostics by default.
- Keep generated context short enough to paste into another model.

## Status

Early extraction from a private production workflow. The first public release should
ship as a clean, generic CLI with examples and no private project assumptions.
