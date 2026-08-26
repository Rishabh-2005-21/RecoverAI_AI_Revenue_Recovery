from app.services.guardrails import validate_action

def test_retry_limit():
    event = {"attempts_count": 2, "status": "detected", "amount": 1000.0}
    decision = {"action": "smart_retry", "max_attempts": 2}
    ok, reason, rules = validate_action(event, decision)
    assert ok is False
    assert "MAX_ATTEMPTS_EXCEEDED" in rules[0]

def test_stopping_rule_already_recovered():
    event = {"attempts_count": 1, "status": "recovered", "amount": 1000.0}
    decision = {"action": "upi_link_nudge", "max_attempts": 2}
    ok, reason, rules = validate_action(event, decision)
    assert ok is False
    assert "STOPPING_RULE" in rules[0]
