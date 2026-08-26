from datetime import datetime
from typing import Dict, Any, List
from app.database import log_audit, get_audit_logs

def audit_event(event_type: str, payment_id: str, details: Dict[str, Any], actor: str = "AI_AGENT", money_recovered: float = 0.0):
    return log_audit(
        event_id=payment_id,
        category=details.get("category", "payment_failure"),
        event_type=event_type,
        details=details,
        actor=actor,
        money_recovered=money_recovered
    )

def fetch_audit_trail(limit: int = 100) -> List[Dict[str, Any]]:
    return get_audit_logs(limit)
