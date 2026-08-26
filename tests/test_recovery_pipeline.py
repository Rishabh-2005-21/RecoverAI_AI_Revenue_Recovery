import pytest
from app.services.detector import detect_revenue_at_risk
from app.services.diagnoser import diagnose
from app.services.decision_agent import choose_action
from app.services.guardrails import validate_action
from app.services.recovery import execute_recovery_workflow
from app.services.voice_agent import generate_hinglish_script, simulate_interactive_objection
from app.services.promise_to_pay import create_promise_to_pay, verify_p2p_settlements
from app.evaluation.evaluate import run_batch_evaluation
from app.models import ActionType, RiskCategory

def test_detector_payment_failure():
    event = {
        "event_id": "EVT_TEST_001",
        "category": "payment_failure",
        "amount": 5000.0,
        "failure_reason": "BAD_REQUEST_PAYMENT_TIMED_OUT",
        "status": "detected"
    }
    res = detect_revenue_at_risk(event)
    assert res["is_at_risk"] is True
    assert res["risk_score"] > 0.8

def test_diagnoser_and_decision():
    event = {
        "event_id": "EVT_TEST_002",
        "category": "cart_abandonment",
        "amount": 15000.0,
        "failure_reason": "CART_ABANDONED_HIGH_INTENT",
        "customer": {"name": "Test User"}
    }
    diag = diagnose(event)
    assert diag["recovery_probability"] > 0.8
    decision = choose_action(event, diag)
    assert decision["action"] == ActionType.HINGLISH_VOICE_CALL

def test_hitl_high_value_guardrail():
    event = {
        "event_id": "EVT_TEST_003",
        "category": "b2b_receivable",
        "amount": 120000.0,
        "failure_reason": "INVOICE_OVERDUE_30D",
        "attempts_count": 0
    }
    diag = diagnose(event)
    decision = choose_action(event, diag)
    approved, reason, rules = validate_action(event, decision)
    assert approved is False
    assert decision["requires_approval"] is True
    assert decision["action"] == ActionType.ESCALATE_TO_HUMAN

def test_hinglish_voice_agent():
    event = {
        "event_id": "EVT_TEST_004",
        "category": "cart_abandonment",
        "amount": 8999.0,
        "customer": {"name": "Rahul Sharma", "phone": "+919810123456"}
    }
    script_info = generate_hinglish_script(event)
    assert "Rahul" in script_info["greeting"]
    assert "RecoverAI" in script_info["greeting"]
    assert len(script_info["dialog_turns"]) > 2

def test_promise_to_pay_workflow():
    event_id = "EVT_P2P_001"
    p2p = create_promise_to_pay(event_id, "CUST_99", "Rahul Sharma", 25000.0, 2)
    assert p2p["amount_promised"] == 25000.0
    assert p2p["status"] == "active"

    # Verify settlement matching
    settle_res = verify_p2p_settlements(event_id, 25000.0)
    assert settle_res["status"] == "fulfilled"

def test_batch_evaluation():
    metrics = run_batch_evaluation(batch_size=20, seed=123)
    assert metrics["batch_size"] == 20
    assert metrics["precision"] >= 0.0
    assert metrics["recall"] >= 0.0
    assert metrics["total_revenue_recovered"] >= 0.0
