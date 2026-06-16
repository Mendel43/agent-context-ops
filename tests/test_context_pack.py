from pathlib import Path

from agent_context_ops.context_pack import ContextConfig, build_context_pack


def test_context_pack_skips_env_and_redacts(tmp_path: Path):
    key = "TO" + "KEN"
    (tmp_path / "README.md").write_text(f"hello\n{key}=secretsecretsecretsecret\n", encoding="utf-8")  # allow-secret
    password = "PASS" + "WORD"  # allow-secret
    (tmp_path / ".env").write_text(f"{password}=super-secret\n", encoding="utf-8")
    config = ContextConfig(include=["README.md", ".env"])
    output = build_context_pack(tmp_path, config)
    assert "README.md" in output
    assert ".env" not in output
    assert "secretsecret" not in output  # allow-secret
    assert "<REDACTED>" in output
