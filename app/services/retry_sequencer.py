from datetime import datetime, timedelta
from typing import Dict, Any

BANK_UPTIME_MATRIX = {
    "HDFC": {"peak_uptime": "08:00 - 20:00", "maintenance_window": "00:00 - 02:30", "success_rate": 0.96},
    "SBI": {"peak_uptime": "09:00 - 18:00", "maintenance_window": "01:00 - 04:00", "success_rate": 0.91},
    "ICICI": {"peak_uptime": "08:00 - 21:00", "maintenance_window": "02:00 - 03:30", "success_rate": 0.97},
    "AXIS": {"peak_uptime": "08:30 - 20:30", "maintenance_window": "01:30 - 03:00", "success_rate": 0.94},
    "DEFAULT": {"peak_uptime": "09:00 - 19:00", "maintenance_window": "01:00 - 03:00", "success_rate": 0.90}
}

SALARY_DAYS = {1, 2, 3, 4, 5, 7, 30, 31}

def calculate_optimal_retry_schedule(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes optimal e-mandate / payment retry timing based on salary cycle & bank uptime heuristics.
    """
    now = datetime.now()
    bank_name = event.get("bank_name", "HDFC").upper()
    bank_info = BANK_UPTIME_MATRIX.get(bank_name, BANK_UPTIME_MATRIX["DEFAULT"])

    # Check if today/tomorrow is a salary day
    current_day = now.day
    is_salary_week = current_day in SALARY_DAYS or (current_day + 1) in SALARY_DAYS

    # Recommend target time
    if is_salary_week:
        target_date = now + timedelta(days=1 if now.hour >= 18 else 0)
        target_time = target_date.replace(hour=8, minute=30, second=0)
        reason = f"High-confidence Salary Day slot ({target_time.strftime('%b %d at 08:30 AM')}). Expected liquidity peak."
        confidence = 0.95
    else:
        # Schedule 45-60 mins out to clear transient network/server glitches
        target_time = now + timedelta(minutes=45)
        reason = f"Transient gateway recovery slot ({target_time.strftime('%H:%M')}). Bank uptime: {bank_info['success_rate']*100}%."
        confidence = bank_info["success_rate"]

    return {
        "event_id": event.get("event_id"),
        "bank_name": bank_name,
        "recommended_retry_time": target_time.isoformat(),
        "display_slot": target_time.strftime("%d %b %Y, %I:%M %p"),
        "salary_cycle_match": is_salary_week,
        "expected_success_probability": confidence,
        "reasoning": reason,
        "bank_maintenance_window": bank_info["maintenance_window"]
    }
