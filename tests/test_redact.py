from agent_context_ops.redact import redact_text


def test_redacts_key_value_secret():
    key = "OPENAI_" + "API_" + "KEY"
    prefix = "s" + "k-"
    secret = prefix + "secretsecretsecretsecret"  # allow-secret
    text = f"{key}={secret}"  # allow-secret
    assert prefix + "secret" not in redact_text(text)  # allow-secret
    assert f"{key}=<REDACTED>" in redact_text(text)  # allow-secret


def test_redacts_bearer_token():
    token = "abcdefghijklmnopqrstuvwxyz" + "123456"  # allow-secret
    bearer = "Bear" + "er "
    text = f"Authorization: {bearer}{token}"  # allow-secret
    assert "abcdefghijklmnopqrstuvwxyz" not in redact_text(text)
