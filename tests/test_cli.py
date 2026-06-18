import pytest

from agent_context_ops import __version__
from agent_context_ops.cli import main


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == f"agent-context-ops {__version__}"
