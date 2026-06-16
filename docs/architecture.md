# Architecture

Agent Context Ops is intentionally small and file-based.

## Components

- `context_pack`: reads selected project files and generates a redacted Markdown
  handoff for another AI agent.
- `backup_check`: verifies that critical files have recent backup candidates.
- `graph_check`: checks whether a generated knowledge graph is older than source
  files.
- `obsidian_log`: writes structured Markdown notes into an Obsidian-compatible
  vault folder.
- `redact`: best-effort secret redaction for generated context.

## Design choices

- No database required.
- No network required.
- No provider-specific API required.
- No secrets are read intentionally.
- Human-readable output is preferred over hidden state.

## Intended workflow

1. Maintainer runs `context-pack` before handing work to another agent.
2. Agent reads the handoff and project docs.
3. Maintainer runs `backup-check` and `graph-check` before risky work.
4. Decisions and incidents are saved through `obsidian-log`.
5. The generated notes become durable project memory.

