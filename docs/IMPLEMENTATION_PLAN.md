# 3-Day Implementation Plan

## Day 1 – Data + detection
- Generate/import synthetic payment events.
- Build risk/revenue-at-risk detector.
- Create held-out train/test split.
- Establish baseline precision and recall.
- Build database schema.

## Day 2 – Agent + recovery workflow
- Add diagnosis.
- Add LLM explanation/decision layer if useful.
- Keep final action bounded by deterministic guardrails.
- Integrate Razorpay test-mode APIs.
- Implement verification and audit logs.

## Day 3 – Dashboard + evaluation
- Build Streamlit dashboard.
- Show recovered revenue across a batch.
- Add failure and escalation views.
- Calculate precision, recall, recovery rate and false-positive cost.
- Record one graceful failure.
- Prepare demo and pitch.

## Demo scenario
Show a batch containing:
1. Temporary payment failures → bounded retry → success.
2. Insufficient funds → reminder → no automatic repeated charge.
3. Unknown failure → escalation.
4. Retry-limit breach → blocked by guardrail.
5. Full audit trail for every decision.
