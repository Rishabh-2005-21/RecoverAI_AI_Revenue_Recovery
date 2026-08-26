from typing import Dict, Any

RECOVERABLE_FAILURE_REASONS = {
    "BAD_REQUEST_PAYMENT_TIMED_OUT",
    "ISSUER_BANK_SERVER_DOWN",
    "INSUFFICIENT_FUNDS",
    "AUTHENTICATION_FAILED",
    "GATEWAY_ERROR",
    "MANDATE_EXPIRED",
    "EXPIRED_CARD",
    "CARD_DECLINED",
    "CART_ABANDONED_STEP3",
    "CART_ABANDONED_HIGH_INTENT",
    "INVOICE_OVERDUE_15D",
    "INVOICE_OVERDUE_30D",
    "INVOICE_OVERDUE_60D",
}

def detect_revenue_at_risk(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects revenue at risk and calculates 7-day Predictive Risk & Recovery Priority Score.
    Priority Score = Payment Amount + (CLV * 0.2) + (Recovery Prob * 1000) - Recovery Cost
    """
    category = event.get("category", "payment_failure")
    reason = event.get("failure_reason", "UNKNOWN_ERROR")
    amount = float(event.get("amount", 0.0))
    status = event.get("status", "detected")
    cust = event.get("customer") or {}
    clv = float(cust.get("ltv", amount * 3.0))

    is_recoverable = False
    risk_score = 0.0
    predictive_7day_risk = 0.0

    if status in ["detected", "failed", "abandoned", "overdue"]:
        if reason in RECOVERABLE_FAILURE_REASONS:
            is_recoverable = True
            risk_score = 0.88 if reason in ["BAD_REQUEST_PAYMENT_TIMED_OUT", "ISSUER_BANK_SERVER_DOWN", "CART_ABANDONED_HIGH_INTENT"] else 0.75
            predictive_7day_risk = round(amount * (1.0 if category == "failed_subscription" else 0.85), 2)

    # Compute Recovery Priority Score
    recovery_prob = 0.90 if reason in ["BAD_REQUEST_PAYMENT_TIMED_OUT", "CART_ABANDONED_HIGH_INTENT"] else 0.75
    recovery_cost = 5.0 # ₹5 per SMS/call
    priority_score = round(amount + (clv * 0.15) + (recovery_prob * 500) - recovery_cost, 1)

    priority_label = "HIGH" if priority_score > 5000 else ("MEDIUM" if priority_score > 1500 else "LOW")

    return {
        "event_id": event.get("event_id"),
        "category": category,
        "is_at_risk": is_recoverable,
        "risk_score": risk_score,
        "amount": amount,
        "customer_clv": clv,
        "predictive_7day_risk_amount": predictive_7day_risk,
        "recovery_priority_score": priority_score,
        "priority_label": priority_label,
        "failure_reason": reason,
        "detection_timestamp": event.get("created_at")
    }
