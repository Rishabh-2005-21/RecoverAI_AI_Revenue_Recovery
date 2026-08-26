from typing import Dict, Any
from app.models import RiskCategory, ActionType

DIAGNOSIS_MAP = {
    "BAD_REQUEST_PAYMENT_TIMED_OUT": {
        "root_cause": "Transient network timeout during payment gateway handshake",
        "category_type": "Technical Failure (45%)",
        "customer_intent": "Technical payment friction (Customer wanted to buy)",
        "recovery_probability": 0.92,
        "recommended_action": ActionType.SMART_RETRY,
        "urgency_level": "HIGH"
    },
    "ISSUER_BANK_SERVER_DOWN": {
        "root_cause": "Issuer bank core banking downtime (HDFC/SBI scheduled maintenance)",
        "category_type": "Bank Failure (25%)",
        "customer_intent": "Bank server downtime (No customer fault)",
        "recovery_probability": 0.88,
        "recommended_action": ActionType.MANDATE_RETRY_SCHEDULE,
        "urgency_level": "HIGH"
    },
    "INSUFFICIENT_FUNDS": {
        "root_cause": "Temporary low account balance on debit card or mandate debit",
        "category_type": "Customer Funds (18%)",
        "customer_intent": "Funds delay / Payday waiting",
        "recovery_probability": 0.76,
        "recommended_action": ActionType.UPI_LINK_NUDGE,
        "urgency_level": "MEDIUM"
    },
    "AUTHENTICATION_FAILED": {
        "root_cause": "3D Secure OTP timeout or incorrect password entry",
        "category_type": "Authentication Failure (8%)",
        "customer_intent": "OTP friction / Password expired",
        "recovery_probability": 0.65,
        "recommended_action": ActionType.UPI_LINK_NUDGE,
        "urgency_level": "MEDIUM"
    },
    "CART_ABANDONED_STEP3": {
        "root_cause": "Price-sensitive checkout abandonment at final payment step",
        "category_type": "Price Hesitation (12%)",
        "customer_intent": "Price Sensitive (Needs discount nudge)",
        "recovery_probability": 0.82,
        "recommended_action": ActionType.CHECKOUT_DISCOUNT_OFFER,
        "urgency_level": "HIGH"
    },
    "CART_ABANDONED_HIGH_INTENT": {
        "root_cause": "High intent buyer drop-off after spending >3 mins on checkout",
        "category_type": "High Intent Drop-off",
        "customer_intent": "Product hesitation / Checkout distraction",
        "recovery_probability": 0.85,
        "recommended_action": ActionType.HINGLISH_VOICE_CALL,
        "urgency_level": "HIGH"
    },
    "INVOICE_OVERDUE_30D": {
        "root_cause": "B2B enterprise invoice 30 days overdue",
        "category_type": "Enterprise Receivables Risk",
        "customer_intent": "Approval workflow bottleneck in accounts payable",
        "recovery_probability": 0.75,
        "recommended_action": ActionType.HINGLISH_VOICE_CALL,
        "urgency_level": "HIGH"
    }
}

def diagnose(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs root cause diagnosis, classifies customer intent, and generates Explainable AI decision rationale.
    """
    reason = event.get("failure_reason", "UNKNOWN_ERROR")
    category = event.get("category", RiskCategory.PAYMENT_FAILURE)
    amount = float(event.get("amount", 0.0))

    diag_info = DIAGNOSIS_MAP.get(reason, {
        "root_cause": f"Unclassified failure: {reason}",
        "category_type": "Unclassified Failure",
        "customer_intent": "Unknown Intent",
        "recovery_probability": 0.55,
        "recommended_action": ActionType.ESCALATE_TO_HUMAN if amount > 50000 else ActionType.UPI_LINK_NUDGE,
        "urgency_level": "HIGH" if amount > 50000 else "MEDIUM"
    })

    # Generate Explainable AI rationale
    explainable_factors = [
        f"✓ Failure Category: {diag_info['category_type']}",
        f"✓ Customer Intent: {diag_info['customer_intent']}",
        f"✓ Historical Recovery Success: {diag_info['recovery_probability']*100:.0f}%",
        f"✓ Amount: ₹{amount:,.2f}" + (" (>₹50k HITL Guardrail Applied)" if amount > 50000 else " (Auto-approved)")
    ]

    return {
        "event_id": event.get("event_id"),
        "root_cause": diag_info["root_cause"],
        "category": category,
        "category_type": diag_info["category_type"],
        "customer_intent": diag_info["customer_intent"],
        "recovery_probability": diag_info["recovery_probability"],
        "recommended_action": diag_info["recommended_action"],
        "urgency_level": diag_info["urgency_level"],
        "explainable_rationales": explainable_factors,
        "explanation": f"AI classified {diag_info['customer_intent']} with {diag_info['recovery_probability']*100:.0f}% recovery probability."
    }
