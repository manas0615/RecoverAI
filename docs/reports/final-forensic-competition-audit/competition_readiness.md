# 9. Competition Readiness & Scorecard

**Status:** Ready after Targeted Fixes.

## Track 03 Readiness Scorecard

| Capability | Score | Justification |
| :--- | :--- | :--- |
| **Revenue Risk Detection** | 9/10 | Accurately extracts and standardizes amounts from Razorpay webhooks. |
| **Intervention Intelligence** | 3/10 | Relies on hardcoded heuristic fallbacks; LLM is merely a structural narrator. |
| **AI Grounding** | 9/10 | Strict Pydantic schemas and EV isolation completely prevent financial hallucinations. |
| **Bounded Execution** | 10/10 | Immaculate backend execution pipeline. |
| **Policy Safety** | 10/10 | Robust state machine blocks duplicates and contradictory executions. |
| **Verification** | 10/10 | P09 cryptographic webhook verification is mathematically sound. |
| **Auditability** | 9/10 | Comprehensive `audit_events` ledger for every state transition. |
| **Batch Measurement** | 2/10 | Evaluation framework is structurally rigged and 100% synthetic. |
| **Business Value** | 7/10 | Clear dashboard, but "Unknown Exposure" calculations are somewhat opaque. |
| **Reliability** | 9/10 | High. SQLite WAL mode, optimistic locking, idempotent handling. |
| **Security** | 1/10 | P0 failure due to plaintext Gemini/Razorpay secrets in `.env` and scripts. |
| **Demo Credibility** | 8/10 | Visually stunning, but vulnerable to technical teardown of metrics. |
| **UX** | 8/10 | Premium feel, though a11y issues and error swallowing remain. |
| **Differentiation** | 7/10 | Deep integration with Razorpay is excellent, but AI intelligence claims are weak. |

**TOTAL: 102/140**

## The "What will a judge attack?" Matrix

1. **"Is this just a rule engine?"**
   *Evidence:* `_deterministic_cause_assessment` uses hardcoded 0.95 confidence.
   *Response:* We must implement a genuine LLM risk/cause evaluator before submission, or explicitly brand the system as a "hybrid deterministic-AI engine."
2. **"Are your evaluation numbers fake?"**
   *Evidence:* `expected_natural_recovery = False` in `simulator.py`.
   *Response:* We must rewrite the simulator to use empirical/historical distributions, or remove the evaluation framework from the repository.
3. **"Where is the multi-tenant isolation?"**
   *Evidence:* `GET /recovery-cases` fetches all DB cases using a static frontend API key.
   *Response:* Acknowledge it as a single-merchant prototype for the buildathon scope.

## Fix Before P25
1. **MUST FIX:** Rotate Gemini, Groq, and Razorpay API keys.
2. **MUST FIX:** Delete dangerous/live automation scripts in `scratch/`.
3. **SHOULD FIX:** Un-rig the evaluation simulator baseline logic.
4. **SHOULD FIX:** Ensure frontend API client parses JSON error responses.

## Do Not Build
- Do not build multi-tenant auth (waste of time, just document the scope).
- Do not add more AI models or tools.
- Do not migrate to Postgres or add Kubernetes. SQLite is a strength for demo portability.
