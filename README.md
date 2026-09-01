# RecoverAI

## AI Revenue Recovery Agent

> Detect revenue at risk. Let AI determine the intervention. Recover it through bounded execution. Verify every outcome.

AI • Policy Guardrails • Razorpay Test Mode • Verification • Audit • Analytics

## Why RecoverAI?

Revenue loss does not end at payment failure.

A payment can fail, a checkout can degrade, or a recovery attempt can become unsafe or ambiguous.

RecoverAI closes the loop:

detect → diagnose → decide → recover → verify.

## Razorpay Buildathon — Track 03: AI Revenue Recovery

RecoverAI maps directly to the challenge requirements:
- Detect revenue at risk
- Diagnose the failure
- Determine the right intervention
- Execute a bounded recovery workflow
- Verify the provider outcome
- Measure recovered revenue
- Maintain compliant escalation and stopping rules
- Preserve an audit trail

## System Architecture

`mermaid
flowchart LR
    A[Revenue Event] --> B[Recovery Case]
    B --> C[Evidence Context]
    C --> D[AI Intelligence]
    D --> E[Policy Engine]

    E -->|APPROVE| F[RecoveryActionService]
    E -->|ESCALATE| G[Human Approval]
    E -->|DENY / SUPPRESS| H[Stop]

    G --> F
    F --> I[Razorpay Test Mode]
    I --> J[Provider Webhook]
    J --> K[VerificationEngine]
    K --> L[Verified Recovery]
    L --> M[Audit + Analytics]
`

## How the Agent Thinks

The AI layer in RecoverAI acts as an intelligent diagnostic and proposal engine.

### AI receives
* RecoveryCase facts
* observable RevenueEvent evidence
* relevant recovery context

### AI produces
* cause assessment
* ranked intervention candidates
* recommendation
* confidence
* reasoning

### AI cannot
* call Razorpay
* write directly to the database
* bypass PolicyEngine
* directly execute financial recovery

## AI and Policy Boundary

`mermaid
flowchart TD
    A[Case Evidence] --> B[Gemini]
    B --> C[Structured Intervention Plan]
    C --> D[PolicyEngine]
    D --> E[Bounded Execution]

    B -. No financial credentials .-> F[No direct Razorpay access]
    B -. No DB write access .-> G[No direct state mutation]
`

AI proposes. Deterministic policy decides what is allowed.

## Provider & Fallback Model

The system utilizes a defined fallback chain for continuous resilience:

**Gemini → Groq → Hugging Face → Deterministic Fallback**

* Gemini has been successfully used for real, live recommendations within the system.
* Provider provenance is strictly tied to the provider that actually generated the intervention, visible in the UI and audit trail.
* Deterministic fallback is a resilience path ensuring operational continuity, and is explicitly labelled, not disguised as an AI result.
* Current Groq access may be restricted depending on credentials and project configuration.

## Execution Safety

The canonical financial execution path is tightly constrained:
**Policy → RecoveryActionService → RazorpayAdapter → Razorpay Test Mode**

Execution is heavily guarded through:
* strict authorization checks
* action-state validation
* idempotency keys
* atomic execution claim
* Test Mode fail-closed bounds
* completely decoupled frontend containing no private Razorpay credentials

> A recovery action is atomically claimed before crossing the financial provider boundary, preventing simultaneous execution attempts from creating duplicate provider actions.

## State Machine

`mermaid
stateDiagram-v2
    [*] --> PROPOSED
    PROPOSED --> AUTHORIZED
    PROPOSED --> ESCALATED
    PROPOSED --> CANCELLED
    ESCALATED --> AUTHORIZED
    AUTHORIZED --> EXECUTING
    EXECUTING --> VERIFICATION_PENDING
    VERIFICATION_PENDING --> VERIFIED_SUCCESS
    VERIFICATION_PENDING --> VERIFIED_FAILURE
    VERIFICATION_PENDING --> EXECUTION_UNKNOWN
`

* **APPROVE** → transitions directly to bounded execution.
* **ESCALATE** → blocks execution pending the human approval boundary.
* **DENY/SUPPRESS** → halts the recovery attempt entirely.
* **UNKNOWN** → fail-safe verification state protecting against ambiguous provider signals.

## Verification

A provider response alone does not equal recovery.
The VerificationEngine independently checks provider evidence to validate the outcome.

`mermaid
flowchart LR
    A[Provider Event] --> B{Reference Match?}
    B -->|No| U[UNKNOWN]
    B -->|Yes| C{Amount Match?}
    C -->|No| U
    C -->|Yes| D{Currency Match?}
    D -->|No| U
    D -->|Yes| E{Event Type Match?}
    E -->|No| U
    E -->|Yes| S[VERIFIED_SUCCESS]
`

Mismatches remain UNKNOWN rather than prematurely registering as false successful recoveries.

## Real Test Mode Proof

RecoverAI proves end-to-end integration:

payment failure / revenue-risk event
→ case creation
→ AI recommendation
→ policy
→ Razorpay Test Mode
→ real payment-link reference
→ webhook ingestion
→ independent verification
→ recovered outcome

> Razorpay integration is demonstrated in Test Mode, not against a production merchant account.

## Operator Workflow

RecoverAI provides a complete operator UI journey:

* **01 Dashboard:** High-level overview of revenue risk and active operational metrics.
* **02 Recovery Cases:** Tabular queue of all active and historically resolved recovery scenarios.
* **03 Case Detail:** Deep-dive view of case facts, evidence, AI assessment, and timeline history.
* **04 Approval Queue:** Dedicated interface for reviewing and resolving ESCALATED human-in-the-loop decisions.
* **05 Execution Queue:** Real-time visibility into the bounded financial execution pipeline.
* **06 Verification:** Visibility into the VerificationEngine matching logic and UNKNOWN event fallouts.
* **07 Audit:** Immutable chronological record of system events, policy decisions, and state transitions.
* **08 Operational Analytics:** Live charts tracking real runtime outcomes and system performance.

## What Is Real vs Synthetic?

| Component              | Nature                                    |
| ---------------------- | ----------------------------------------- |
| Gemini recommendation  | Real provider output when Gemini succeeds |
| Razorpay payment links | Real Razorpay Test Mode resources         |
| Webhook ingestion      | Real application webhook endpoint         |
| HMAC validation        | Real                                      |
| VerificationEngine     | Real backend verification                 |
| Operational analytics  | Runtime DB-derived outcomes               |
| Seed/demo records      | Development/test fixtures                 |
| P25 benchmark          | Synthetic, frozen, explicitly labelled    |

## Synthetic Evaluation Benchmark

The system's deterministic policy bounds were evaluated via the frozen P25 synthetic benchmark:

**P25 — SYNTHETIC QUANTITATIVE BENCHMARK**

**Recovery Rate (Case)**
* Simple Rule: 52.3%
* RecoverAI: 48.5%

> These are synthetic benchmark results and are not operational Razorpay recovery metrics.

## Safety & Security Boundaries

RecoverAI enforces strict security controls:
* No provider secrets exist in the frontend browser environment.
* Financial actions are strictly bounded to Razorpay Test Mode.
* Inbound events require rigorous HMAC webhook validation.
* Duplicate webhook protection ensures idempotent verification.
* Action execution idempotency guarantees one logical action per attempt.
* Atomic execution claim mathematically prevents simultaneous execution race conditions.
* PolicyEngine enforcement evaluates all execution requests dynamically.
* VerificationEngine exhibits fail-closed behavior under ambiguity.
* Audit trails are strictly append-only.
* The AI engine has absolutely no direct financial execution access.

## Questions a Judge Should Be Able to Answer Immediately

**Can Gemini call Razorpay?**
No. It has no provider credentials or direct execution tools.

**Can the browser call Razorpay?**
No. Financial provider credentials remain backend-only.

**Can AI bypass policy?**
No. Financial execution passes exclusively through PolicyEngine and RecoveryActionService.

**What happens when AI providers fail?**
The configured fallback chain activates; deterministic fallback is explicitly identified as fallback provenance.

**Can duplicate execution create two recoveries?**
No. The action is atomically claimed before provider execution and concurrent attempts are mathematically guarded by the database.

**Can a mismatched webhook produce VERIFIED_SUCCESS?**
No. Verification requires strict reference, amount, currency, and event-type consistency.

**What is synthetic?**
Only the P25 benchmark data and the local seed/demo fixtures.

**Where is the audit trail?**
The audit trail is available in the UI on Screen 07 and directly accessible via the backend audit endpoint.

## Repository Structure

`	ext
RecoverAI/
├── recoverai/
│   ├── api/
│   ├── domain/
│   ├── intelligence/
│   ├── llm_gateway/
│   ├── policy/
│   ├── services/
│   ├── ingestion/
│   ├── integrations/
│   ├── verification/
│   ├── persistence/
│   └── mcp/
├── frontend/
├── tests/
├── docs/
├── scripts/
└── pyproject.toml
`

## Engineering Principles

* Backend authority over frontend assumptions
* AI proposes; policy constrains
* AI has no direct financial credentials
* Verify before recording recovery
* Append-only auditability
* Idempotent execution
* Atomic financial-action claim
* Fail closed under ambiguity
* Synthetic benchmarks isolated from operational analytics
* Test Mode for external financial integration

## Quick Start

A complete demo walkthrough is available in [docs/DEMO.md](docs/DEMO.md).

`powershell
# 1. Environment Setup
Copy-Item .env.example .env
Copy-Item frontend/.env.example frontend/.env

# 2. Startup (runs FastAPI backend + React frontend)
.\scripts\start-all.ps1

# 3. Health Check & Demo Reset
# Generates 7 idempotent fixture cases to safely prove all UI states
uv run python scripts/seed_demo_data.py
`

## Demo

Please see [docs/DEMO.md](docs/DEMO.md) for the detailed step-by-step evaluation guide.

The judge-facing demo highlights the complete end-to-end flow:
Recovery Case → Analyze → AI recommendation → Policy → Execution → Razorpay Test Mode → Verification → Audit → Analytics

## Verification & Testing

RecoverAI's engineering is verified by an extensive test suite:

`ash
# Run the core backend test suite
uv run python -m pytest tests/ -q

# Execute the Real Test Mode E2E verification
uv run python -m pytest tests/e2e/test_real_testmode.py -v

# Verify the frontend production build
cd frontend
npm run build
`

The core backend suite verifies internal invariants and concurrency constraints. The Test Mode E2E explicitly validates Razorpay external behavior, and the frontend build proves TSX correctness.

## Status

* P27 — Data Stability ✅
* P28 — Authorization + AI Integrity ✅
* P29 — Razorpay Test Mode E2E ✅
* P30 — Hostile Hardening ✅

**Submission status: Frozen / Ready for submission**
