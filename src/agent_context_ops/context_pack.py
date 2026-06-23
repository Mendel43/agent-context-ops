from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import tomllib

from .fs_safety import DEFAULT_EXCLUDES, is_sensitive_path, resolve_inside, should_skip
from .redact import redact_text


DEFAULT_INCLUDE = [
    "README.md",
    "ROADMAP.md",
    "AGENTS.md",
    "CLAUDE.md",
    "docs",
    "examples",
    "pyproject.toml",
]

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".py",
    ".sh",
    ".ps1",
    ".cmd",
}

# Marks the machine-readable manifest block so `--compare` can find it again.
MANIFEST_MARKER = "<!-- agent-context-ops:manifest -->"


@dataclass(frozen=True)
class Profile:
    """A named preset that tunes which files ship and how big the pack may grow."""

    name: str
    description: str
    include: list[str]
    max_file_bytes: int
    max_total_bytes: int


# Agent-specific presets. Each profile picks an include set and a byte budget that
# fits how that agent consumes a handoff: codex wants code, hermes wants it lean.
PROFILES: dict[str, Profile] = {
    "generic": Profile(
        "generic",
        "Balanced handoff that fits any agent.",
        list(DEFAULT_INCLUDE),
        20_000,
        180_000,
    ),
    "codex": Profile(
        "codex",
        "Code-heavy pack for Codex / open-source sessions.",
        ["AGENTS.md", "README.md", "ROADMAP.md", "docs", "examples", "src", "tests", "pyproject.toml"],
        24_000,
        260_000,
    ),
    "claude": Profile(
        "claude",
        "Intent and docs pack for Claude Code.",
        ["CLAUDE.md", "README.md", "ROADMAP.md", "AGENTS.md", "docs", "examples", "pyproject.toml"],
        20_000,
        200_000,
    ),
    "hermes": Profile(
        "hermes",
        "Lean handoff for a cheap worker model.",
        ["README.md", "ROADMAP.md", "AGENTS.md", "CLAUDE.md"],
        8_000,
        60_000,
    ),
}

DEFAULT_PROFILE = "generic"


def profile_names() -> list[str]:
    return list(PROFILES)


@dataclass
class ContextConfig:
    include: list[str] = field(default_factory=lambda: list(DEFAULT_INCLUDE))
    exclude: set[str] = field(default_factory=lambda: set(DEFAULT_EXCLUDES))
    max_file_bytes: int = 20_000
    max_total_bytes: int = 180_000
    show_absolute_root: bool = False
    profile: str = DEFAULT_PROFILE

    @classmethod
    def for_profile(cls, name: str) -> "ContextConfig":
        try:
            profile = PROFILES[name]
        except KeyError:
            raise ValueError(
                f"unknown profile: {name!r}. choose from {', '.join(PROFILES)}"
            ) from None
        return cls(
            include=list(profile.include),
            max_file_bytes=profile.max_file_bytes,
            max_total_bytes=profile.max_total_bytes,
            profile=name,
        )

    @classmethod
    def from_file(cls, path: Path | None) -> "ContextConfig":
        if path is None or not path.exists():
            return cls()
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        context = data.get("context", {})
        profile_name = context.get("profile", DEFAULT_PROFILE)
        # Seed defaults from the chosen profile, then let explicit keys override them.
        base = cls.for_profile(profile_name) if profile_name in PROFILES else cls()
        return cls(
            include=list(context.get("include", base.include)),
            exclude=set(context.get("exclude", DEFAULT_EXCLUDES)),
            max_file_bytes=int(context.get("max_file_bytes", base.max_file_bytes)),
            max_total_bytes=int(context.get("max_total_bytes", base.max_total_bytes)),
            show_absolute_root=bool(context.get("show_absolute_root", False)),
            profile=profile_name,
        )


@dataclass
class FileEntry:
    rel: str
    area: str
    bytes: int
    sha256: str
    body: str


def build_context_pack(root: Path, config: ContextConfig) -> str:
    root = root.resolve()
    generated = datetime.now(timezone.utc).isoformat()

    entries: list[FileEntry] = []
    truncated = False
    total = 0
    for file_path in _iter_included_files(root, config):
        if total >= config.max_total_bytes:
            truncated = True
            break
        try:
            raw = file_path.read_bytes()
        except OSError as exc:
            rel = file_path.relative_to(root).as_posix()
            body = f"\n### `{rel}`\n\nCould not read: {exc}\n"
            entries.append(FileEntry(rel, _area_of(rel), len(body.encode("utf-8")), "", body))
            continue
        if len(raw) > config.max_file_bytes:
            raw = raw[: config.max_file_bytes]
            suffix = "\n\n[File truncated by agent-context-ops]\n"
        else:
            suffix = ""
        try:
            text = raw.decode("utf-8") + suffix
        except UnicodeDecodeError:
            continue
        text = redact_text(text)
        rel = file_path.relative_to(root).as_posix()
        body = _format_file(rel, text)
        section_bytes = len(body.encode("utf-8"))
        total += section_bytes
        entries.append(
            FileEntry(
                rel=rel,
                area=_area_of(rel),
                bytes=section_bytes,
                sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                body=body,
            )
        )

    manifest = _build_manifest(generated, config.profile, entries, truncated)
    return _render(root, config, generated, manifest, entries, truncated)


def _render(
    root: Path,
    config: ContextConfig,
    generated: str,
    manifest: dict,
    entries: list[FileEntry],
    truncated: bool,
) -> str:
    lines: list[str] = []
    lines.append("# Agent Context Pack")
    lines.append("")
    lines.append(f"- Generated: `{generated}`")
    lines.append(f"- Profile: `{config.profile}`")
    lines.append(f"- Root: `{_display_root(root, config)}`")
    lines.append(f"- Files: {manifest['file_count']} · {manifest['total_bytes']} bytes")
    lines.append("")
    lines.append("## Git")
    lines.append("")
    lines.append(_git_summary(root))
    lines.append("")
    lines.append("## Areas")
    lines.append("")
    lines.append(_render_areas(entries))
    lines.append("")
    lines.append("## Manifest")
    lines.append("")
    lines.append(MANIFEST_MARKER)
    lines.append("```json")
    lines.append(json.dumps(manifest, indent=2, sort_keys=True))
    lines.append("```")
    lines.append("")
    lines.append("## Files")
    lines.append("")
    for entry in entries:
        lines.append(entry.body)
    if truncated:
        lines.append("\n> Context truncated: max total bytes reached.\n")
    return "\n".join(lines).rstrip() + "\n"


def _build_manifest(
    generated: str, profile: str, entries: list[FileEntry], truncated: bool
) -> dict:
    return {
        "generated": generated,
        "profile": profile,
        "truncated": truncated,
        "file_count": len(entries),
        "total_bytes": sum(entry.bytes for entry in entries),
        "files": [
            {"path": entry.rel, "bytes": entry.bytes, "sha256": entry.sha256}
            for entry in entries
        ],
    }


def _render_areas(entries: list[FileEntry]) -> str:
    if not entries:
        return "No files included."
    areas: dict[str, list[FileEntry]] = {}
    for entry in entries:
        areas.setdefault(entry.area, []).append(entry)
    rows = ["| Area | Files | Bytes |", "|---|---:|---:|"]
    for area in sorted(areas):
        items = areas[area]
        rows.append(f"| `{area}` | {len(items)} | {sum(i.bytes for i in items)} |")
    return "\n".join(rows)


def extract_manifest(text: str) -> dict | None:
    """Pull the embedded manifest back out of a previously generated pack."""
    marker = text.find(MANIFEST_MARKER)
    if marker == -1:
        return None
    fence = text.find("```json", marker)
    if fence == -1:
        return None
    body_start = text.find("\n", fence)
    if body_start == -1:
        return None
    body_start += 1
    fence_end = text.find("```", body_start)
    if fence_end == -1:
        return None
    try:
        return json.loads(text[body_start:fence_end])
    except json.JSONDecodeError:
        return None


def diff_manifests(old: dict, new: dict) -> dict:
    old_files = {f["path"]: f.get("sha256", "") for f in old.get("files", [])}
    new_files = {f["path"]: f.get("sha256", "") for f in new.get("files", [])}
    added = sorted(path for path in new_files if path not in old_files)
    removed = sorted(path for path in old_files if path not in new_files)
    changed = sorted(
        path
        for path in new_files
        if path in old_files and old_files[path] != new_files[path]
    )
    return {"added": added, "removed": removed, "changed": changed}


def render_diff(diff: dict) -> str:
    lines = ["## Changes since previous pack", ""]
    for title, key in (("Added", "added"), ("Removed", "removed"), ("Changed", "changed")):
        items = diff.get(key, [])
        if not items:
            lines.append(f"- {title}: none")
            continue
        lines.append(f"- {title}:")
        lines.extend(f"  - `{path}`" for path in items)
    return "\n".join(lines) + "\n"


def _display_root(root: Path, config: ContextConfig) -> str:
    if config.show_absolute_root:
        return str(root)
    return root.name or "."


def _area_of(rel: str) -> str:
    parts = rel.split("/")
    return parts[0] if len(parts) > 1 else "(root)"


def _iter_included_files(root: Path, config: ContextConfig) -> list[Path]:
    files: list[Path] = []
    for item in config.include:
        try:
            target = resolve_inside(root, root / item)
        except ValueError:
            continue
        if not target.exists() or should_skip(target, root, config.exclude):
            continue
        if target.is_file():
            if _is_exportable(target):
                files.append(target)
            continue
        for path in sorted(target.rglob("*")):
            if path.is_file() and not should_skip(path, root, config.exclude) and _is_exportable(path):
                files.append(path)
    return sorted(set(files))


def _is_exportable(path: Path) -> bool:
    return not is_sensitive_path(path) and path.suffix.lower() in TEXT_SUFFIXES


def _format_file(rel: str, text: str) -> str:
    fence = "```"
    if "```" in text:
        fence = "````"
    return f"\n### `{rel}`\n\n{fence}\n{text.rstrip()}\n{fence}\n"


def _git_summary(root: Path) -> str:
    try:
        status = subprocess.run(
            ["git", "-C", str(root), "status", "--short"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "Git status unavailable."
    if status.returncode != 0:
        return "Not a git repository yet."
    output = status.stdout.strip()
    return f"```text\n{output or 'clean'}\n```"
