# RecoverAI
### AI Revenue Recovery Agent
**Razorpay Buildathon — Track 03: AI Revenue Recovery**

RecoverAI is an evidence-first revenue recovery system that investigates failed payments and recommends intelligent interventions.

> **AI proposes. Deterministic policy constrains. Provider evidence proves.**

![Razorpay Test Mode](https://img.shields.io/badge/Razorpay-Test_Mode-blue)
![Track 03](https://img.shields.io/badge/Razorpay_Buildathon-Track_03-orange)
![Gemini Powered](https://img.shields.io/badge/AI_Powered-Gemini-green)

---

## The Problem

Revenue is frequently lost when payments fail or require manual intervention to complete. RecoverAI is designed to safely automate this by closing the loop. It:
1. Detects revenue-at-risk signals.
2. Analyzes qualitative evidence (e.g., failure codes, customer context).
3. Proposes an intelligent recovery action.
4. Applies deterministic financial policy to approve or block the action.
5. Executes bounded recovery actions securely.
6. Verifies the provider outcome independently.
7. Records an append-only timeline for audit and analytics.

---

## What We Built

RecoverAI strictly follows an auditable lifecycle: **Detect → Understand → Recommend → Decide → Recover → Verify → Measure**

| Capability | RecoverAI Behavior |
| --- | --- |
| **Case detection** | Ingests payment failure events into structured recovery cases. |
| **AI recommendation** | Interprets context (via Gemini/Groq) to suggest an optimal intervention. |
| **Policy decision** | Deterministically evaluates the action against strict financial limits. |
| **Human approval** | Escalates ambiguous or high-value cases to manual review via n8n. |
| **Financial execution** | Executes authorized actions strictly through a centralized backend service. |
| **Webhook verification** | Authenticates webhook HMAC signatures from the provider. |
| **Recovery outcome** | Asserts success only after verified matching provider evidence (amount/currency). |
| **Audit** | Persists an immutable timeline of all decisions and state changes. |

---

## Real Product Proof

RecoverAI demonstrates real functionality backed by real providers. Where stated, the system interacts with the **Razorpay Test Mode API** and live LLM providers. 

- **Generates real recommendations** using live Gemini outputs.
- **Creates real Razorpay Test Mode** payment links dynamically.
- **Processes real Razorpay webhooks** matching live signatures.
- **Executes real backend verification** to assert recovery success.

*This repository demonstrates test-environment capabilities, not production payment processing or live money movement.*

---

## Architecture

`mermaid
graph TD
    Event[Razorpay Event] --> Ingest[Ingestion]
    Ingest --> Case[Recovery Case]
    Case --> AI[AI Analysis]
    AI --> Policy[Deterministic Policy]
    Policy -->|APPROVE| Exec[Recovery Action Service]
    Exec --> RZ[Razorpay Test Mode]
    RZ -.->|payment_link.paid| WH[Webhook]
    WH --> Verify[Independent Verification]
    Verify --> Audit[Audit & Analytics]
    Policy -->|ESCALATE| n8n[n8n Orchestration]
`

---

## AI Trust Boundary

The core engineering principle of RecoverAI is that **the LLM is not the final financial authority**.

| Agentic Intelligence (Gemini/Groq/Fallback) | Deterministic System (PolicyEngine & App) |
| --- | --- |
| Interprets unstructured qualitative evidence. | Enforces strict financial limits. |
| Recommends an action based on context. | Controls the final execution boundary. |
| Determines confidence of the cause. | Asserts recovery outcomes via verification. |
| Proposes intervention parameters. | Records immutable audit state. |

---

## Key Engineering Decisions

1. **AI recommendation is separated from policy decision.** The LLM cannot mutate financial state; it proposes a plan that a strict Python policy engine evaluates.
2. **Financial execution is centralized.** All provider interactions route through a canonical RecoveryActionService, establishing a single enforcement chokepoint.
3. **Atomic execution prevents concurrency races.** Before calling Razorpay, the database atomically claims the recovery action, preventing simultaneous duplicate executions.
4. **Razorpay webhook authenticity is checked.** HMAC validation prevents spoofed payment confirmations from altering case states.
5. **Duplicate webhook handling is idempotent.** Redundant events are ignored safely to prevent double-counting recovered revenue.
6. **Verification is independent of AI output.** Success is only recorded when provider amounts and currencies strictly match expectations.
7. **Ambiguous evidence remains UNKNOWN.** The system fails closed; uncertain provider responses result in an UNKNOWN state rather than assuming success.

---

## Failure & Safety Paths

RecoverAI is built for resilience. Failures are handled safely without compromising the recovery lifecycle.

| Failure | System Response |
| --- | --- |
| **AI provider unavailable** | Falls back to a deterministic rule-based evaluation. |
| **Policy denial** | Execution is blocked entirely. |
| **Human approval required** | Action transitions to ESCALATE state for operator review. |
| **Execution uncertainty** | Action transitions to UNKNOWN pending manual reconciliation. |
| **Invalid webhook** | Payload is rejected. |
| **Duplicate webhook** | Event is ignored idempotently. |
| **Evidence mismatch** | Case status defaults to UNKNOWN. |
| **Concurrent execution** | Only one atomic execution claim succeeds; others fail safely. |

---

## Real vs Synthetic Evidence

RecoverAI keeps proof categories explicit to ensure absolute transparency:

- **REAL / PROVIDER-BACKED:** All Razorpay Test Mode interactions, HMAC webhook validations, live AI provider outputs, and frontend interactions are powered by the actual backend.
- **SYNTHETIC:** We generated a 1,500-scenario dataset offline specifically to tune our policy thresholds and benchmark the deterministic fallback logic.

*Synthetic benchmark numbers are not live merchant performance and do not feed operational analytics.*

---

## Evaluation

We evaluated RecoverAI's fallback behavior using a 1,500-scenario synthetic benchmark against a naive "Simple Rule" baseline (which always attempts aggressive recovery).

| Metric | Simple Rule | RecoverAI |
| --- | ---: | ---: |
| **Recoveries** | 785 | 727 |
| **Gross recovery** | ₹3,362,181 | ₹3,159,057 |
| **Failed interventions** | 558 | 506 |
| **Escalations** | 0 | 121 |

**Tradeoff:** RecoverAI sacrifices some gross recovery in this synthetic benchmark in exchange for preventing 52 failed interventions and explicitly escalating 121 risky cases. *(Synthetic evaluation — not live merchant performance).*

---

## Security & Execution Safety

- **Backend-only provider credentials:** Secrets are never exposed to the browser.
- **Test Mode guard:** Hardcoded enforcement prevents processing outside Razorpay's sandbox endpoints.
- **Webhook HMAC verification:** Validates the authenticity of all incoming provider events.
- **Idempotency & Atomic Claims:** Database-level transaction locks prevent duplicate executions.
- **Independent verification:** Recovery success requires explicit event alignment, not just a 200 OK.
- **Append-oriented audit trail:** Case history cannot be silently overwritten.

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| **Backend API** | Python 3.11, FastAPI, Pydantic |
| **Intelligence** | Gemini, Groq (via abstraction gateway) |
| **Database** | SQLite (for zero-dependency local evaluation) |
| **Provider** | Razorpay Test Mode API |
| **Frontend** | React, TypeScript, Vite |
| **Orchestration** | n8n (via Docker compose) |

---

## Quick Start

### 1. Configure Environment
`ash
cp .env.example .env
cp frontend/.env.example frontend/.env
`
*(Add your Gemini API key and Razorpay Test Mode credentials. Never commit .env)*

### 2. Startup
`powershell
.\scripts\start-all.ps1
`

### 3. Reset Demo Data
`powershell
uv run python scripts/seed_demo_data.py
`

---

## Repository Structure

`	ext
RecoverAI/
├── recoverai/       # Core backend domain, services, and intelligence
├── frontend/        # React operator console
├── tests/           # Unit and E2E verification
├── n8n/             # Docker compose for orchestration
├── docs/            # Deeper technical documentation
└── scripts/         # Startup and seeding utilities
`

---

## Documentation

For deep technical insights, review the documentation:
- [System Architecture](docs/system_architecture.md)
- [Policy & Safety](docs/policy_and_safety.md)
- [Security](docs/security.md)
- [Razorpay Integration](docs/razorpay_integration.md)
- [Evaluation Strategy](docs/evaluation.md)

---

## Limitations

- **Competition Prototype:** This is a single-merchant prototype designed for the Buildathon, not a production multi-merchant platform.
- **Test Mode Only:** Razorpay integration is strictly constrained to Test Mode.
- **Synthetic Evaluation:** Quantitative benchmarks use synthetic scenarios, not real-world INR metrics.
- **Exchange Rates:** Multi-currency support exists via strict partitioning, but live exchange-rate calculations are out of scope.

---

RecoverAI turns revenue recovery from a blind retry into an evidence-driven decision: AI proposes the intervention, policy constrains it, Razorpay executes it, verification proves it, and the audit trail records what actually happened.
