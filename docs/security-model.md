# Security Model

Agent Context Ops assumes maintainers may paste generated output into AI tools.
That makes context generation a security boundary.

## Protected by default

- `.env` and common environment files are skipped.
- SSH keys and PEM/key files are skipped.
- Secret-looking strings are redacted from included text.
- Common heavy/private folders are excluded.

## Not guaranteed

Redaction is best-effort. It cannot understand every custom credential format or
every private business detail. Maintainers should review handoffs before sharing
them outside a trusted environment.

## Recommended practice

- Use explicit include lists.
- Keep private notes outside public repositories.
- Add project-specific excludes.
- Review generated handoffs before pasting them into third-party tools.

