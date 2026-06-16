from __future__ import annotations

from pathlib import Path


DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
    "secrets",
    "private",
    "graphify-out",
}

SENSITIVE_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".npmrc",
    ".pypirc",
    "id_rsa",
    "id_ed25519",
}


def resolve_inside(root: Path, target: Path) -> Path:
    root_resolved = root.resolve()
    target_resolved = target.resolve()
    if target_resolved != root_resolved and root_resolved not in target_resolved.parents:
        raise ValueError(f"path escapes root: {target}")
    return target_resolved


def is_sensitive_path(path: Path) -> bool:
    name = path.name.lower()
    if name in SENSITIVE_FILENAMES:
        return True
    if name.endswith(".key") or name.endswith(".pem"):
        return True
    return False


def should_skip(path: Path, root: Path, excludes: set[str] | None = None) -> bool:
    excludes = excludes or DEFAULT_EXCLUDES
    rel_parts = path.relative_to(root).parts
    return any(part in excludes for part in rel_parts)

