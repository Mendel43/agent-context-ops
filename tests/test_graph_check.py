from pathlib import Path

from agent_context_ops.graph_check import check_graph


def test_missing_graph_is_not_fresh(tmp_path: Path):
    status = check_graph(tmp_path, tmp_path / "graphify-out" / "graph.json", (".py",))
    assert not status.exists
    assert not status.is_fresh

