# CLI Reference

## `context-pack`

Generates a redacted Markdown handoff.

```bash
agent-context-ops context-pack --root . --output handoff.md
```

By default, `context-pack` hides the absolute local root path and reports only
the project folder name. Use `--show-root-path` only when the receiving agent
needs the exact local path on the same machine.

## `doctor`

Runs a local readiness check before sharing context with another agent.

```bash
agent-context-ops doctor --root .
```

The doctor checks whether the root exists, whether a config file is present,
whether secret-looking content is visible, whether a context pack can be built,
whether the graph output is fresh, and whether a backup directory exists.

## `backup-check`

Checks that critical files have backup candidates.

```bash
agent-context-ops backup-check --root . --file pyproject.toml --backup-dir backups
```

## `graph-check`

Checks whether a graph output is older than source files.

```bash
agent-context-ops graph-check --root . --graph graphify-out/graph.json
```

## `obsidian-log`

Writes a Markdown note to an Obsidian vault.

```bash
echo "Done" | agent-context-ops obsidian-log --vault ~/Notes --folder "AI Logs" --title "Daily note"
```

## `init`

Creates a minimal context structure in a project.

```bash
agent-context-ops init --root .
```

## `scan-secrets`

Scans project text files for secret-looking content.

```bash
agent-context-ops scan-secrets --root .
```

## `council-log`

Records read-only multi-agent review outputs.

```bash
agent-context-ops council-log \
  --root . \
  --question "Should we ship this change?" \
  --panel codex=codex.md \
  --panel claude=claude.md \
  --final final.md
```
