# RecoverAI Engineering Design

RecoverAI is architected around a strict separation of concerns between AI-driven intelligence and deterministic financial execution.

## Trust Boundary

**"AI proposes. Deterministic policy constrains. Provider evidence proves."**

The system deliberately does **NOT** let Gemini:
- Directly execute financial operations.
- Declare a payment recovered.
- Override safety policies.
- Decide stopping conditions or retry limits.

## Architecture Pipeline

1. **Frontend**: React SPA for case management and operator visibility.
2. **FastAPI Layer**: Exposes protected REST/MCP endpoints.
3. **Case Manager**: Ingests Razorpay webhooks, correlates them to cases, and triggers background analysis.
4. **Intelligence / LLM Gateway**: Gemini extracts features, generates a likely cause, and proposes candidate interventions.
5. **PolicyEngine**: The central deterministic authority. Re-evaluates proposals against limits, thresholds, and systemic conditions.
6. **RecoveryActionService**: The execution wrapper. Verifies the policy decision before interacting with the provider.
7. **RazorpayAdapter**: Mutates state at the financial boundary via Test Mode APIs.
8. **VerificationEngine**: Cryptographically verifies incoming provider webhooks and confirms exact amount/currency matching before declaring success.
9. **Persistence / Audit**: SQLite database maintaining an immutable ledger of all decisions and state transitions.
