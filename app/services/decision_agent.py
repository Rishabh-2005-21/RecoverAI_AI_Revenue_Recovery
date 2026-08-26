from typing import Dict, Any
from app.models import ActionType, RiskCategory

def choose_action(event: Dict[str, Any], diagnosis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bounded policy decision layer. LLM proposals are bounded by these strict rules.
    """
    category = event.get("category", RiskCategory.PAYMENT_FAILURE)
    reason = event.get("failure_reason", "")
    amount = float(event.get("amount", 0.0))
    rec_action = diagnosis.get("recommended_action", ActionType.UPI_LINK_NUDGE)
    cust = event.get("customer") or {}

    payload = {
        "customer_name": cust.get("name", "Customer"),
        "customer_phone": cust.get("phone", "+919876543210"),
        "customer_email": cust.get("email", "customer@example.com"),
        "amount": amount
    }

    # B2B Invoice Receivables > ₹50,000 always require HITL approval
    if amount > 50000.0 and category == RiskCategory.B2B_RECEIVABLE:
        return {
            "event_id": event.get("event_id"),
            "action": ActionType.ESCALATE_TO_HUMAN,
            "reason": f"High value enterprise invoice (₹{amount:,.2f} > ₹50,000 threshold) routed to supervisor queue.",
            "confidence": 0.95,
            "max_attempts": 1,
            "requires_approval": True,
            "payload": payload
        }

    # Policy Routing by Scenario
    if category == RiskCategory.PAYMENT_FAILURE:
        if reason in ["BAD_REQUEST_PAYMENT_TIMED_OUT", "GATEWAY_ERROR"]:
            return {
                "event_id": event.get("event_id"),
                "action": ActionType.SMART_RETRY,
                "reason": "Transient gateway failure. Executing smart automated payment retry via secondary route.",
                "confidence": 0.92,
                "max_attempts": 2,
                "requires_approval": False,
                "payload": payload
            }
        elif reason == "ISSUER_BANK_SERVER_DOWN":
            return {
                "event_id": event.get("event_id"),
                "action": ActionType.MANDATE_RETRY_SCHEDULE,
                "reason": "Bank core servers down. Scheduling delayed retry in optimal 45-min uptime window.",
                "confidence": 0.88,
                "max_attempts": 2,
                "requires_approval": False,
                "payload": payload
            }
        else:
            return {
                "event_id": event.get("event_id"),
                "action": ActionType.UPI_LINK_NUDGE,
                "reason": "Soft payment failure. Sending 1-click Razorpay UPI Payment Link via WhatsApp/SMS.",
                "confidence": 0.82,
                "max_attempts": 2,
                "requires_approval": False,
                "payload": payload
            }

    elif category == RiskCategory.CART_ABANDONMENT:
        if amount > 10000.0:
            return {
                "event_id": event.get("event_id"),
                "action": ActionType.HINGLISH_VOICE_CALL,
                "reason": "High-value cart drop-off. Triggering personalized Hinglish AI Voice call & instant WhatsApp checkout link.",
                "confidence": 0.85,
                "max_attempts": 2,
                "requires_approval": False,
                "payload": payload
            }
        else:
            payload["discount_pct"] = 5.0
            return {
                "event_id": event.get("event_id"),
                "action": ActionType.CHECKOUT_DISCOUNT_OFFER,
                "reason": "Abandoned cart. Generating 5% instant cashback Razorpay link to trigger conversion.",
                "confidence": 0.84,
                "max_attempts": 2,
                "requires_approval": False,
                "payload": payload
            }

    elif category == RiskCategory.FAILED_SUBSCRIPTION:
        if reason == "MANDATE_EXPIRED":
            return {
                "event_id": event.get("event_id"),
                "action": ActionType.CARD_UPDATE_PORTAL,
                "reason": "e-Mandate tenure expired. Sending mandate renewal portal link.",
                "confidence": 0.80,
                "max_attempts": 2,
                "requires_approval": False,
                "payload": payload
            }
        else:
            return {
                "event_id": event.get("event_id"),
                "action": ActionType.DUNNING_REMINDER,
                "reason": "Subscription recurring payment failed. Initiating smart dunning sequence with zero-friction portal link.",
                "confidence": 0.78,
                "max_attempts": 3,
                "requires_approval": False,
                "payload": payload
            }

    elif category == RiskCategory.B2B_RECEIVABLE:
        if "60D" in reason:
            return {
                "event_id": event.get("event_id"),
                "action": ActionType.ESCALATE_TO_HUMAN,
                "reason": "60+ days severely overdue B2B invoice. Escalated to Account Executive.",
                "confidence": 0.60,
                "max_attempts": 1,
                "requires_approval": True,
                "payload": payload
            }
        else:
            return {
                "event_id": event.get("event_id"),
                "action": ActionType.HINGLISH_VOICE_CALL,
                "reason": "Overdue enterprise invoice. AI Receivables Chaser Hinglish call to negotiate Promise-to-Pay.",
                "confidence": 0.82,
                "max_attempts": 2,
                "requires_approval": False,
                "payload": payload
            }

    return {
        "event_id": event.get("event_id"),
        "action": ActionType.ESCALATE_TO_HUMAN,
        "reason": "Unspecified pattern. Escalating to human supervisor.",
        "confidence": 0.50,
        "max_attempts": 1,
        "requires_approval": True,
        "payload": payload
    }
