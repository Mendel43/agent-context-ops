from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class BackupFinding:
    file: Path
    ok: bool
    message: str
    latest_backup: Path | None = None


def check_backups(root: Path, files: list[str], backup_dir: Path, max_age_days: int) -> list[BackupFinding]:
    root = root.resolve()
    backup_dir = backup_dir.resolve()
    findings: list[BackupFinding] = []
    now = datetime.now(timezone.utc).timestamp()
    max_age_seconds = max_age_days * 86400

    for item in files:
        target = (root / item).resolve()
        candidates = _backup_candidates(backup_dir, target.name)
        latest = candidates[0] if candidates else None
        if not target.exists():
            findings.append(BackupFinding(target, False, "critical file is missing", latest))
            continue
        if latest is None:
            findings.append(BackupFinding(target, False, "no backup candidate found", None))
            continue
        age = now - latest.stat().st_mtime
        if age > max_age_seconds:
            days = age / 86400
            findings.append(BackupFinding(target, False, f"latest backup is stale ({days:.1f} days)", latest))
            continue
        findings.append(BackupFinding(target, True, "backup is fresh", latest))
    return findings


def render_backup_report(findings: list[BackupFinding]) -> str:
    lines = ["# Backup Check", ""]
    for finding in findings:
        status = "OK" if finding.ok else "FAIL"
        lines.append(f"- `{status}` `{finding.file}` - {finding.message}")
        if finding.latest_backup:
            lines.append(f"  backup: `{finding.latest_backup}`")
    return "\n".join(lines) + "\n"


def _backup_candidates(backup_dir: Path, filename: str) -> list[Path]:
    if not backup_dir.exists():
        return []
    candidates = [
        path
        for path in backup_dir.rglob("*")
        if path.is_file() and (path.name == filename or path.name.startswith(f"{filename}.") or filename in path.name)
    ]
    return sorted(candidates, key=lambda path: path.stat().st_mtime, reverse=True)

