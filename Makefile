.PHONY: smoke scan context

smoke:
	PYTHONPATH=src python3 -m compileall -q src tests scripts
	PYTHONPATH=src python3 scripts/smoke.py
	PYTHONPATH=src python3 -m agent_context_ops.cli doctor --root .

scan:
	PYTHONPATH=src python3 -m agent_context_ops.cli scan-secrets --root .

context:
	PYTHONPATH=src python3 -m agent_context_ops.cli context-pack --root . --config examples/agent-context-ops.toml --output handoff.md
