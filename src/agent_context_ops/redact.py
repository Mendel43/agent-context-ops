from __future__ import annotations

import re


SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd|pwd)\s*=\s*['\"]?[^'\"\s]+"),
    re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-.]{20,}"),
)


def redact_text(text: str) -> str:
    """Redact common secret-looking values from text."""
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(lambda match: _replacement(match.group(0)), redacted)
    return redacted


def _replacement(value: str) -> str:
    if "=" in value:
        key = value.split("=", 1)[0].strip()
        return f"{key}=<REDACTED>"
    if value.lower().startswith("bearer "):
        return "Bearer <REDACTED>"
    return "<REDACTED>"

