# RecoverAI

### AI Revenue Recovery Agent
**Razorpay Buildathon — Track 03: AI Revenue Recovery**

> AI proposes. Deterministic policy constrains. Provider evidence proves.

![Razorpay Test Mode](https://img.shields.io/badge/Razorpay-Test_Mode-blue)
![Track 03](https://img.shields.io/badge/Razorpay_Buildathon-Track_03-orange)

---

## The Problem

Payment failures represent revenue at risk. 

RecoverAI turns a failed payment into a bounded recovery workflow rather than blindly retrying everything. Treating every failure as an aggressive retry degrades the customer experience and risks violating merchant policies. Instead, we need a system that intelligently understands the context of a failure before acting, while remaining strictly constrained by deterministic safety rules.

---

## Core Lifecycle

RecoverAI strictly follows an auditable lifecycle:

**Detect** → **Understand** → **Recommend** → **Decide** → **Recover** → **Verify** → **Measure**

- **Detect:** The system ingests failure signals (like webhooks) into a recovery case.
- **Understand:** The intelligence layer evaluates contextual evidence (e.g., error codes).
- **Recommend:** The intelligence layer contributes contextual signals and an intervention proposal; the analyzer derives the expected recovery probability and expected recovery value used for planning.
- **Decide:** A deterministic policy engine evaluates the proposal and issues an `APPROVE`, `ESCALATE`, `DENY`, `SUPPRESS`, or `WAIT`.
- **Recover:** Bounded execution triggers safe interventions (like generating a Payment Link) where allowed.
- **Verify:** Independent provider evidence confirms success.
- **Measure:** Outcomes feed into audit and analytics.

---

## AI Trust Boundary

**The LLM is NOT the final financial authority.**

The core engineering principle of RecoverAI is the separation of intelligence from execution:

| Agentic Intelligence (Gemini/Fallback) | Deterministic System (PolicyEngine & App) |
| --- | --- |
| Interprets unstructured qualitative evidence. | Enforces strict financial limits. |
| Recommends an action based on context. | Controls the final execution boundary. |
| Provides contextual signals for the recovery assessment. | Asserts recovery outcomes via verification. |
| Proposes intervention parameters. | Records immutable audit state. |

---

## Key Engineering Decisions

1. **AI recommendation is separated from policy decision.** The LLM cannot mutate financial state; it proposes a plan that a strict Python policy engine evaluates.
2. **Financial execution is centralized.** All provider interactions route through a canonical `RecoveryActionService`, establishing a single enforcement chokepoint.
3. **Atomic execution prevents concurrency races.** Before calling Razorpay, the database atomically claims the recovery action, preventing simultaneous duplicate executions.
4. **Razorpay webhook authenticity is checked.** HMAC validation prevents spoofed payment confirmations from altering case states.
5. **Duplicate webhook handling is idempotent.** Redundant events are ignored safely to prevent double-counting recovered revenue.
6. **Verification is independent of AI output.** Success is only recorded when provider amounts and currencies strictly match expectations.
7. **Ambiguous evidence remains UNKNOWN.** The system fails closed; uncertain provider responses result in an UNKNOWN state rather than assuming success.

---

## Recovery Verification

**Payment Link creation ≠ recovery.**

A recovery only becomes a verified recovery after appropriate Razorpay provider evidence is independently validated. Verification checks the relevant provider evidence, including event authenticity, reference correlation, amount, currency, and event/status semantics. The system does not assume success simply because an action was dispatched.

---

## Real Razorpay Evidence

RecoverAI has been exercised against the Razorpay Test Mode API, with provider events independently verified by the backend.

- **A001 — ₹100** — verified Razorpay Test Mode recovery
- **A002 — ₹450** — verified Razorpay Test Mode recovery
- **A003 — ₹750** — recovery-payment failure exposed a recovery-loop bug
- **A004 — ₹1,000** — verified Razorpay Test Mode recovery after loop fix
- **A005 — ₹50,000** — the pre-fix live policy wiring gap caused the high-value case to be approved under the old configuration; a Payment Link was created, but no recovery was claimed. The live high-value threshold wiring was subsequently fixed and regression-tested.

*This repository demonstrates test-environment capabilities, not production payment processing or live money movement.*

---

## Evaluation

We evaluated RecoverAI using a frozen 1,500-scenario synthetic benchmark (Seed 42) to compare baseline strategies against the system.

| Strategy | Recovery Rate | Gross Simulated Recovery | Safety |
|---|---|---|---|
| L0 | 8.2% | ₹569,697.22 | PASS |
| L1 | 54.5% | ₹3,232,371.94 | FAIL — 519 policy / 218 stopping violations |
| L2 | 32.0% | ₹1,825,326.26 | PASS |
| L3 RecoverAI | 47.5% | ₹2,709,921.81 | PASS |

In the frozen synthetic benchmark, RecoverAI's L3 pipeline produced a **48.5% relative increase in simulated gross recovered value** over L2. 

*(This is synthetic simulated recovery, not real Razorpay recovered revenue).*

---

## Safety

RecoverAI was rigorously tested against adversarial pressures in a controlled environment. 

Across the 21 tested adversarial scenarios, RecoverAI recorded zero violations of the defined safety invariants:
- **False Recovery Claims:** 0
- **Policy Violations:** 0
- **Invalid Evidence Accepted:** 0
- **Duplicate Financial Execution:** 0
- **Stopping-Rule Violations:** 0
- **Unsafe Actions:** 0

---

## What We Found and Fixed

During development and provider testing, the system exposed several critical edge cases which were subsequently diagnosed, fixed, and locked with regression tests:

1. **Recovery-payment failure loop:** A failed recovery Payment Link generated a new `payment.failed` event, which erroneously spawned a recursive recovery case (discovered in A003). Fixed via exact provider correlation.
2. **Missing live high-value threshold wiring:** The benchmark successfully evaluated a ₹40K threshold, but live dependency injection missed the configuration, causing a ₹50K case (A005) to be automatically approved rather than escalated. Fixed by wiring merchant-configurable thresholds.
3. **Automated tests reaching real Razorpay provider boundary:** The test suite inherited real credentials and allowed auto-execution paths to hit the provider. Fixed by introducing an explicit `ALLOW_REAL_RAZORPAY` safety fence and narrow mocks.

---

## Future Direction: Systemic Intelligence

*(Strategic Extension - Not currently in MVP)*

While the current system performs case-level recovery intelligence, a future extension is portfolio-level intelligence. By detecting gateway-wide degradation across the entire merchant portfolio, the system could suppress individual recoveries during global outages to prevent systemic operational noise.

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| **Backend API** | Python 3.11, FastAPI, Pydantic |
| **Intelligence** | Gemini (Primary intended provider), Deterministic Fallback (Reliability path) |
| **Database** | SQLite |
| **Provider** | Razorpay Test Mode API |
| **Frontend** | React, TypeScript, Vite |
| **Optional Orchestration**| n8n (Only where applicable for external human-approval routing) |

---

## Quick Start

### 1. Configure Environment
```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```
*(Add your Gemini API key and Razorpay Test Mode credentials. Never commit .env)*

### 2. Startup
```powershell
.\scripts\start-all.ps1
```

### 3. Reset Demo Data
```powershell
uv run python scripts/reset_demo_db.py
uv run python scripts/seed_demo_data.py
```

---

## Repository Structure

```text
RecoverAI/
├── recoverai/       # Core backend domain, services, and intelligence
├── frontend/        # React operator console
├── tests/           # Unit and E2E verification
├── docs/            # Deeper technical documentation
└── scripts/         # Startup and seeding utilities
```

---

## Documentation

For deep technical insights and evidence reports, review:
- [System Architecture](docs/architecture.md)
- [Class C Synthetic Benchmark](docs/reports/benchmark_1500_seed42.md)
- [Final Evidence Pack](docs/reports/FINAL_EVIDENCE_PACK.md)
- [Real Razorpay Evidence](docs/reports/REAL_RAZORPAY_EVIDENCE.md)
- [Competitive Positioning](docs/reports/COMPETITIVE_POSITIONING.md)

---

## Limitations

- **Competition Prototype:** This is a single-merchant prototype designed for the Buildathon, not a production multi-merchant platform.
- **Test Mode Only:** Razorpay integration is strictly constrained to Test Mode.
- **Synthetic Evaluation:** Quantitative benchmarks use synthetic scenarios, not real-world INR metrics.
- **Exchange Rates:** Multi-currency support exists via strict partitioning, but live exchange-rate calculations are out of scope.

---

RecoverAI turns revenue recovery from a blind retry into an evidence-driven decision: AI proposes the intervention, policy constrains it, Razorpay executes it, verification proves it, and the audit trail records what actually happened.
