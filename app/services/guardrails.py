from datetime import datetime
from typing import Dict, Any, Tuple, List
from app.models import ActionType

def validate_action(event: Dict[str, Any], decision: Dict[str, Any]) -> Tuple[bool, str, List[str]]:
    """
    Validates a proposed recovery decision against strict financial and compliance guardrails.
    Returns (is_approved, reason, list_of_applied_guardrail_rules).
    """
    applied_rules = []
    attempts = event.get("attempts_count", 0)
    status = event.get("status", "detected")
    amount = float(event.get("amount", 0.0))
    action = decision.get("action")

    # 1. Stopping Rule: Stop immediately if already recovered, disputed, or customer opted out
    if status in ["recovered", "opt_out", "disputed", "canceled"]:
        rule = f"STOPPING_RULE: Event status is '{status}'. All recovery actions halted."
        applied_rules.append(rule)
        return False, rule, applied_rules

    # 2. Maximum Attempts Rule: Max 2 automatic retries for payment degradation
    if action == ActionType.SMART_RETRY and attempts >= 2:
        rule = "MAX_ATTEMPTS_EXCEEDED: Maximum 2 automatic retries allowed to prevent bank bounce charges."
        applied_rules.append(rule)
        return False, rule, applied_rules

    # 3. Maximum Touches Rule: Max 3 total recovery touchpoints per event
    if attempts >= 3:
        rule = "MAX_TOUCHPOINTS_EXCEEDED: Limit of 3 recovery touchpoints reached to enforce TRAI compliance."
        applied_rules.append(rule)
        return False, rule, applied_rules

    # 4. Anti-Harassment Quiet Hours Rule: No automated voice calls between 9 PM (21:00) and 9 AM (09:00)
    now = datetime.now()
    current_hour = now.hour
    if action == ActionType.HINGLISH_VOICE_CALL and (current_hour >= 21 or current_hour < 9):
        rule = f"QUIET_HOURS_ENFORCED: Voice call blocked during quiet hours ({current_hour}:00). Converted to soft WhatsApp/SMS nudge."
        applied_rules.append(rule)
        # We don't block the recovery completely, but force fallback action
        decision["action"] = ActionType.UPI_LINK_NUDGE
        decision["reason"] += " (Converted from Voice Call due to 9 PM-9 AM Quiet Hours rule)"

    # 5. High-Value HITL Gatekeeper: B2B/Payments > ₹50,000 require manual supervisor approval
    if amount > 50000.0 and not decision.get("human_approved", False):
        rule = f"HITL_APPROVAL_REQUIRED: High value transaction (₹{amount:,.2f} > ₹50,000 threshold) routed to Human-In-The-Loop queue."
        applied_rules.append(rule)
        decision["requires_approval"] = True
        decision["action"] = ActionType.ESCALATE_TO_HUMAN
        return False, rule, applied_rules

    applied_rules.append("GUARDRAILS_PASSED: Compliant with financial, TRAI & RBI regulations.")
    return True, "Action approved by compliance policy", applied_rules
