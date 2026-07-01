# Changelog

## v0.2.1 - 2026-07-01

Patch release for release hygiene and package metadata.

### Changed

- Bumped package version to `0.2.1`.
- Added release notes for the patch release.
- Republished release history after removing an unintended co-author trailer from `v0.2.0`.

## v0.2.0 - 2026-06-22

Smart context packs: the handoff now adapts to the agent and can be compared run over run.

### Added

- Agent profiles for `context-pack`: `generic`, `codex`, `claude` and `hermes`, each with its own include set and byte budget. Select with `--profile` or the `profile` key in config.
- Machine-readable manifest embedded in every pack (profile, file count, total bytes, and a sha256 per file).
- Per-area summary table grouping included files by top-level directory.
- `--compare PREVIOUS_PACK` flag that diffs the new pack against a prior one and reports added, removed and changed files.
- Tests covering profiles, manifest extraction, area grouping and diffing.

### Changed

- `context-pack` output now adds `Profile`, `Files`, `## Areas` and `## Manifest` sections alongside the existing git and file sections.

## v0.1.2 - 2026-06-18

Small compatibility and release-quality update.

### Added

- `--version` support for both `agent-context-ops` and `aco`.
- Cross-platform CI coverage for Windows and Linux on Python 3.11 and 3.12.
- CLI version regression test.
- v0.1.2 release notes.

### Changed

- Made the smoke-test command portable across supported CI platforms.
- Updated the public roadmap with the v0.1.2 maintenance milestone.

## v0.1.1 - 2026-06-16

Documentation and demo polish for the first public release.

### Added

- `doctor` command for local readiness checks before sharing context.
- Demo screenshot/GIF assets for the README.
- v0.1.1 release notes.

### Changed

- Improved README structure, quick start and command table.
- Expanded CLI reference and demo docs.
- Updated release checklist to include doctor and demo asset checks.
- Hid absolute local root paths in context packs by default.

## v0.1.0 - 2026-06-15

First public release.

### Added

- `context-pack` for redacted Markdown handoffs.
- `backup-check` for critical file backup freshness.
- `graph-check` for local knowledge graph freshness.
- `obsidian-log` for structured Markdown notes.
- `init` for creating a minimal agent context structure.
- `scan-secrets` for secret-looking content checks.
- `council-log` for read-only multi-agent review logs.
- CI, tests, security docs, examples, and smoke tests.
