# Demo

Run the preflight check:

```bash
agent-context-ops doctor --root .
```

Example output:

```text
# Agent Context Ops Doctor

- `OK` Project root: example-project
- `OK` Config: agent-context-ops.toml
- `OK` Secret scan: no sensitive-looking content found
- `OK` Context pack: dry run generated 4096 bytes
- `WARN` Graph freshness: graphify-out/graph.json not found
- `WARN` Backup directory: no backups directory found

Summary: 0 failure(s), 2 warning(s).
```

Generate a handoff:

```bash
agent-context-ops context-pack --root . --output handoff.md
```

Example output shape:

````markdown
# Agent Context Pack

- Generated: `2026-06-15T20:00:00+00:00`
- Root: `/repo`

## Git

```text
clean
```

## Files

### `README.md`

...
````

Check graph freshness:

```bash
agent-context-ops graph-check --root . --graph graphify-out/graph.json
```

Write an Obsidian note:

```bash
echo "Reviewed release blockers." | agent-context-ops obsidian-log \
  --vault ~/Notes \
  --folder "Maintenance" \
  --title "Release Review"
```
