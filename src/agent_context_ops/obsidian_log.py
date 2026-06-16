from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re


def write_obsidian_note(vault: Path, folder: str, title: str, body: str) -> Path:
    vault = vault.resolve()
    folder_path = (vault / folder).resolve()
    if vault != folder_path and vault not in folder_path.parents:
        raise ValueError("folder must be inside vault")
    folder_path.mkdir(parents=True, exist_ok=True)
    filename = f"{datetime.now().strftime('%Y-%m-%d')} - {_slug(title)}.md"
    path = folder_path / filename
    content = f"# {title}\n\n{body.rstrip()}\n"
    path.write_text(content, encoding="utf-8")
    return path


def _slug(value: str) -> str:
    value = re.sub(r"[^\w\s.-]", "", value, flags=re.UNICODE).strip()
    value = re.sub(r"\s+", " ", value)
    return value[:90] or "note"

