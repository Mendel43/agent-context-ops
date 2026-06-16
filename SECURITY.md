# Security

Agent Context Ops is designed to make AI-assisted maintenance safer, but it can
still expose sensitive project context if configured carelessly.

## Do not export

- `.env` files
- API keys, tokens, passwords or cookies
- private business strategy
- customer data
- private logs
- SSH keys or cloud credentials

The context pack redacts common secret patterns, but redaction is best-effort.
Treat every generated handoff as something you should review before sharing.

## Reporting issues

Open a GitHub issue for non-sensitive bugs. For sensitive reports, use the private
security contact configured on the repository.

