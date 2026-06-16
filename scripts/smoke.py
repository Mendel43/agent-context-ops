from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from agent_context_ops.backup_check import check_backups
from agent_context_ops.context_pack import ContextConfig, build_context_pack
from agent_context_ops.graph_check import check_graph
from agent_context_ops.redact import redact_text
from agent_context_ops.scan import scan_for_sensitive_content


def main() -> int:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        key = "TO" + "KEN"
        password = "PASS" + "WORD"  # allow-secret
        (root / "README.md").write_text(f"{key}=secretsecretsecretsecret\n", encoding="utf-8")  # allow-secret
        (root / ".env").write_text(f"{password}=abc\n", encoding="utf-8")  # allow-secret
        (root / "backups").mkdir()
        (root / "backups" / "README.md.bak").write_text("backup\n", encoding="utf-8")

        context = build_context_pack(root, ContextConfig(include=["README.md", ".env"]))
        assert "secretsecret" not in context
        assert ".env" not in context
        bearer = "Bear" + "er "
        token = "abcdefghijklmnopqrstuvwxyz" + "123456"  # allow-secret
        assert "abcdefghijklmnopqrstuvwxyz" not in redact_text(bearer + token)  # allow-secret
        assert scan_for_sensitive_content(root)
        assert check_backups(root, ["README.md"], root / "backups", max_age_days=1)[0].ok
        assert not check_graph(root, root / "graphify-out" / "graph.json", (".md",)).is_fresh

    print("smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
