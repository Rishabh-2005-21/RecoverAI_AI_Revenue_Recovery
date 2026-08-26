# System Architecture

1. Razorpay test-mode event/payment data enters the ingestion layer.
2. Detection engine identifies revenue-at-risk events.
3. Diagnosis layer explains the likely failure cause.
4. Decision agent selects a bounded intervention.
5. Guardrail layer enforces retry limits, approval requirements, and stopping rules.
6. Recovery executor performs the test-mode action.
7. Verification checks the result.
8. Audit service records every decision and money-related action.
9. Dashboard reports recovery metrics and exceptions.
