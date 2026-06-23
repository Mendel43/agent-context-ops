from pathlib import Path

from agent_context_ops.context_pack import (
    PROFILES,
    ContextConfig,
    build_context_pack,
    diff_manifests,
    extract_manifest,
    render_diff,
)


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


def test_context_pack_hides_absolute_root_by_default(tmp_path: Path):
    (tmp_path / "README.md").write_text("hello\n", encoding="utf-8")
    output = build_context_pack(tmp_path, ContextConfig(include=["README.md"]))
    assert str(tmp_path) not in output
    assert f"Root: `{tmp_path.name}`" in output


def test_for_profile_sets_include_and_budget():
    config = ContextConfig.for_profile("hermes")
    assert config.profile == "hermes"
    assert config.include == list(PROFILES["hermes"].include)
    assert config.max_total_bytes == PROFILES["hermes"].max_total_bytes


def test_for_profile_rejects_unknown_name():
    try:
        ContextConfig.for_profile("nope")
    except ValueError as exc:
        assert "unknown profile" in str(exc)
    else:  # pragma: no cover - guard
        raise AssertionError("expected ValueError")


def test_manifest_and_areas_are_emitted(tmp_path: Path):
    (tmp_path / "README.md").write_text("root doc\n", encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("a guide\n", encoding="utf-8")
    output = build_context_pack(tmp_path, ContextConfig(include=["README.md", "docs"]))

    assert "## Areas" in output
    assert "`docs`" in output
    assert "`(root)`" in output

    manifest = extract_manifest(output)
    assert manifest is not None
    assert manifest["file_count"] == 2
    paths = {f["path"] for f in manifest["files"]}
    assert paths == {"README.md", "docs/guide.md"}
    assert all(f["sha256"] for f in manifest["files"])


def test_diff_detects_added_removed_changed(tmp_path: Path):
    readme = tmp_path / "README.md"
    readme.write_text("v1\n", encoding="utf-8")
    old_pack = build_context_pack(tmp_path, ContextConfig(include=["README.md", "ROADMAP.md"]))

    readme.write_text("v2 changed\n", encoding="utf-8")
    (tmp_path / "ROADMAP.md").write_text("new file\n", encoding="utf-8")
    new_pack = build_context_pack(tmp_path, ContextConfig(include=["README.md", "ROADMAP.md"]))

    diff = diff_manifests(extract_manifest(old_pack), extract_manifest(new_pack))
    assert diff["added"] == ["ROADMAP.md"]
    assert diff["changed"] == ["README.md"]
    assert diff["removed"] == []

    rendered = render_diff(diff)
    assert "Added" in rendered and "ROADMAP.md" in rendered


def test_extract_manifest_returns_none_without_block():
    assert extract_manifest("# just a plain doc\n") is None
