# RecoverAI – AI Revenue Recovery Agent

Hackathon Track: Razorpay AI Buildathon 2026 – Track 03: AI Revenue Recovery

## Goal
Detect revenue at risk, diagnose the likely cause, choose a bounded recovery action, execute it through test-mode integrations, verify the outcome, and maintain an auditable trail.

## Suggested stack
- Python
- FastAPI
- Streamlit
- Pandas / NumPy
- Scikit-learn
- LangChain / LLM provider
- SQLite/PostgreSQL
- Razorpay Test Mode APIs
- Docker (optional)

## Core workflow
Detect → Diagnose → Decide → Act → Verify → Stop/Escalate → Audit

## Evaluation
Use a held-out synthetic batch and report:
- Detection precision/recall
- Recovery success rate
- Revenue recovered
- False recovery / unnecessary intervention rate
- Average recovery time
- Escalation rate
- Guardrail violations prevented

See `docs/IMPLEMENTATION_PLAN.md` for the build plan.

