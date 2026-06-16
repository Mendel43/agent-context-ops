from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
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


@dataclass
class ContextConfig:
    include: list[str] = field(default_factory=lambda: list(DEFAULT_INCLUDE))
    exclude: set[str] = field(default_factory=lambda: set(DEFAULT_EXCLUDES))
    max_file_bytes: int = 20_000
    max_total_bytes: int = 180_000

    @classmethod
    def from_file(cls, path: Path | None) -> "ContextConfig":
        if path is None or not path.exists():
            return cls()
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        context = data.get("context", {})
        return cls(
            include=list(context.get("include", DEFAULT_INCLUDE)),
            exclude=set(context.get("exclude", DEFAULT_EXCLUDES)),
            max_file_bytes=int(context.get("max_file_bytes", 20_000)),
            max_total_bytes=int(context.get("max_total_bytes", 180_000)),
        )


def build_context_pack(root: Path, config: ContextConfig) -> str:
    root = root.resolve()
    chunks: list[str] = []
    chunks.append("# Agent Context Pack")
    chunks.append("")
    chunks.append(f"- Generated: `{datetime.now(timezone.utc).isoformat()}`")
    chunks.append(f"- Root: `{root}`")
    chunks.append("")
    chunks.append("## Git")
    chunks.append("")
    chunks.append(_git_summary(root))
    chunks.append("")
    chunks.append("## Files")
    chunks.append("")

    total = sum(len(chunk.encode("utf-8")) for chunk in chunks)
    for file_path in _iter_included_files(root, config):
        if total >= config.max_total_bytes:
            chunks.append("\n> Context truncated: max total bytes reached.\n")
            break
        try:
            raw = file_path.read_bytes()
        except OSError as exc:
            chunks.append(f"\n### `{file_path.relative_to(root)}`\n\nCould not read: {exc}\n")
            continue
        if len(raw) > config.max_file_bytes:
            raw = raw[: config.max_file_bytes]
            suffix = b"\n\n[File truncated by agent-context-ops]\n"
        else:
            suffix = b""
        try:
            text = raw.decode("utf-8") + suffix.decode("utf-8")
        except UnicodeDecodeError:
            continue
        text = redact_text(text)
        section = _format_file(root, file_path, text)
        total += len(section.encode("utf-8"))
        chunks.append(section)
    return "\n".join(chunks).rstrip() + "\n"


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


def _format_file(root: Path, path: Path, text: str) -> str:
    rel = path.relative_to(root)
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

