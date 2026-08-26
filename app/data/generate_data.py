import random
import pandas as pd

random.seed(42)

reasons = [
    "network_error",
    "timeout",
    "temporary_bank_issue",
    "insufficient_funds",
    "unknown"
]

rows = []
for i in range(1000):
    amount = random.choice([199, 499, 999, 1499, 2499, 4999])
    failed = random.random() < 0.30
    rows.append({
        "payment_id": f"pay_test_{i:05d}",
        "order_id": f"order_{i:05d}",
        "customer_id": f"cust_{random.randint(1, 300):04d}",
        "amount": amount,
        "currency": "INR",
        "status": "failed" if failed else "captured",
        "failure_reason": random.choice(reasons) if failed else None,
    })

df = pd.DataFrame(rows)
df.to_csv("data/raw/payments.csv", index=False)
print("Generated", len(df), "records")
