# RecoverAI

**AI Revenue Recovery Agent**  
*Razorpay AI Buildathon 2026 — Track 03*

> **"AI proposes. Deterministic policy constrains. Provider evidence proves."**

---

## Executive Overview

Lost revenue from payment failures is a massive leak for online merchants. RecoverAI is an autonomous agent that detects recoverable revenue, intelligently proposes bounded interventions, executes them through Razorpay Test Mode, and independently verifies the outcome. If an intervention fails, the system safely replans, bounding its attempts deterministically until the revenue is either recovered or the case is closed. 

## The Problem

When a payment fails, naively retrying the exact same payment is unsafe and often leads to cardholder friction or fraud flags. Conversely, handing full financial authority to an AI agent is inherently untrustworthy due to hallucination risks. Furthermore, simply creating a "Payment Link" does not equal "revenue recovered"—actual provider evidence is required.

## Why Track 03

RecoverAI maps directly to the AI Revenue Recovery track requirements:
- **Identify**: Detects failed payments via webhooks.
- **Mitigate**: Diagnoses causes via LLM feature extraction.
- **Execute**: Deploys Razorpay payment links via deterministic wrappers.
- **Verify**: Parses cryptographic provider evidence.
- **Measure**: Tracks exact recovered value.
- **Bound**: Implements strict escalation, stopping conditions, and limits.

## How AI Works

RecoverAI uses Gemini to perform the following:
- **Feature Extraction**: Parses complex provider payloads for context.
- **Diagnosis**: Assesses the likely failure cause (e.g., Customer NSF, Network Issue).
- **Intervention Proposal**: Generates multiple candidate interventions.
- **Candidate Ranking**: Ranks interventions by likelihood of success.
- **Deterministic Fallback**: If Gemini fails or times out, the system safely demotes to a predefined heuristic fallback without halting.

## Architecture

```mermaid
flowchart TD
    WH[Razorpay Webhooks] -->|HMAC Verified| CM[Case Manager]
    CM -->|Triggers| LLM[Gemini Intelligence]
    LLM -->|Proposes Plan| PE[Policy Engine]
    PE -->|Constrains| RAS[Recovery Action Service]
    RAS -->|Executes| RZ[Razorpay Test Mode API]
    RZ -->|Payment Outcome| VE[Verification Engine]
    VE -->|Updates| CM
    
    subgraph Trust Boundary
    PE
    RAS
    VE
    end
    
    LLM -.->|Proposes (Untrusted)| Trust Boundary
```

## Agent Lifecycle

| Phase | Description |
|---|---|
| **Ingestion** | Cryptographically verified Razorpay webhooks create `RecoveryCase` entities. |
| **Analysis** | LLM evaluates the failure context and proposes an `InterventionPlan`. |
| **Authorization** | `PolicyEngine` evaluates the plan against attempt limits, thresholds, and idempotency locks. |
| **Execution** | `RecoveryActionService` invokes the Razorpay Adapter (Test Mode). |
| **Verification** | `VerificationEngine` awaits and independently cryptographically confirms the payment outcome. |

## Closed-Loop Recovery

RecoverAI operates a fully closed-loop architecture. When a recovery action (e.g., a Payment Link) fails:
1. **Correlation**: The failure is mapped deterministically back to the original action.
2. **Prior-Action Context**: The failure becomes context for the next AI analysis.
3. **Bounded Next Attempt**: The AI proposes a new intervention.
4. **Deterministic Stop**: The `PolicyEngine` strictly halts execution if `max_attempts_per_case` (e.g., 3) is exceeded.

## AI Trust Boundary

| AI CAN | AI CANNOT |
|---|---|
| Interpret failure context | Authorize money movement |
| Generate likely cause | Bypass PolicyEngine |
| Propose interventions | Mark recovery successful |
| Rank candidate interventions | Override attempt limits |
| Contribute planning context | Override high-value controls |
| | Fabricate provider evidence |
| | Directly invoke Razorpay financial execution |

*(Note: AI "confidence" scores are relative ranking signals, not calibrated financial probabilities.)*

## Recovery Verification

> **Payment Link creation ≠ recovery.**

A recovery is ONLY counted when the `VerificationEngine` independently validates the expected provider evidence. It checks:
- Webhook authenticity via HMAC
- Exact external reference correlation
- Exact amount match
- Exact currency match

If evidence is missing or ambiguous, RecoverAI fails closed to `UNKNOWN`.

## Real Razorpay Evidence

We executed real recoveries using the Razorpay Test Mode API. See the [Evidence Pack](evidence/razorpay/README.md) for full incident reports:
- **A001 & A002**: Successful end-to-end recovery loops.
- **A003**: Intentionally failed recovery exposing a correlation defect, which was successfully caught and patched.
- **A004**: Successful recovery proving the A003 loop fix.
- **A005**: High-value policy threshold trip (historical baseline).

## Safety Engineering

- **Deterministic Policy**: All proposed actions are evaluated before execution.
- **Stopping Conditions**: Maximum attempt limits per case.
- **Idempotency**: Execution claims and duplicate-webhook protections.
- **Verification**: Strict currency and amount checking.
- **Rate Limiting**: Bounded API request limits.
- **High-Value Controls**: Escalate-to-human workflows for large amounts.
- **Systemic Degradation**: Halts automated actions during mass failure events.

## Evaluation

We evaluated RecoverAI across four distinct layers to ensure both safety and efficacy:

1. **Frozen 1,500 Deterministic Benchmark**: Measured the architecture's structural capabilities.
2. **Live Gemini Integration Smoke Test**: Validated live API integration and quota-exhaustion fallback.
3. **Adversarial Red-Team Suite**: Tested against malicious inputs and logic bypasses.
4. **Real Razorpay Test Mode Evidence**: Validated end-to-end financial integrations.

### Frozen Synthetic Benchmark

*Seed: 42 | Scenarios: 1,500*

| Strategy | Recovery Rate | Gross Simulated Recovery | Safety |
|---|---:|---:|---|
| L0 (No intervention) | 8.2% | ₹569,697.22 | PASS |
| L1 (Naive - retry everything) | 54.5% | ₹3,232,371.94 | **FAIL** (519 policy violations) |
| L2 (Deterministic rules) | 32.0% | ₹1,825,326.26 | PASS |
| **L3 (RecoverAI)** | 47.5% | **₹2,709,921.81** | **PASS** |

The bounded RecoverAI architecture achieved a **48.46% higher simulated gross recovered value** than the safe deterministic baseline in the frozen benchmark. 

*(Note: The L3 benchmark evaluates the system/recovery architecture and policy behavior using deterministic fallback `llm_gateway=None`. It does not measure causal live-LLM uplift.)*

## What We Found and Fixed

An offline hostile red-team review by an Antigravity QA agent identified two critical flaws that mocked tests missed. Both were subsequently patched:

1. **Broken Recovery-Loop Correlation**: The Razorpay adapter was not emitting the specific deterministic Recovery Action ID expected by the case manager, meaning recovery failures were not properly correlating. **Fix**: The adapter now securely embeds the `Action ID`, allowing flawless loop closure.
2. **Amount Verification Bypass**: The verification engine accepted malformed webhooks lacking an `amount` block. **Fix**: The engine now fails closed (`UNKNOWN`) if the amount is missing, preventing false success states.

## Quick Start

### 1. Configure environment

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```

Add your **Gemini API key** and **Razorpay Test Mode credentials**. Never commit `.env`.

### 2. Start services

```powershell
uv run uvicorn recoverai.api.main:app --reload
```

### 3. Seed demo data

```powershell
uv run python scripts/reset_demo_db.py
uv run python scripts/seed_demo_data.py
```

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Pydantic
- **Intelligence**: Gemini (Primary), Deterministic Fallback
- **Database**: SQLite
- **Provider**: Razorpay Test Mode API
- **Frontend**: React, TypeScript, Vite

## Repository Structure

```text
RecoverAI/
├── recoverai/      # Core backend, intelligence, policy, verification
├── frontend/       # React operator console
├── tests/          # Unit, integration, E2E, adversarial tests
├── docs/           # Architecture and technical documentation
├── evidence/       # Evaluation, benchmark, and provider evidence
└── scripts/        # Startup and seeding utilities
```

## Evidence & Documentation

- [Benchmark Evidence](evidence/benchmark/README.md)
- [Live AI Evaluation](evidence/ai-evaluation/README.md)
- [Adversarial Findings](evidence/adversarial/README.md)
- [Razorpay Provider Evidence](evidence/razorpay/README.md)
- [Engineering Design](DESIGN.md)
- [Closed-Loop Architecture](docs/CLOSED_LOOP.md)
- [Security & Trust Architecture](docs/SECURITY.md)

## Limitations

- **Rate Limiting**: The current prototype uses a lightweight in-memory rate limiter based on `request.client.host` and does not account for proxy identity spoofing (e.g., `X-Forwarded-For`).
- **Quota Exhaustion**: The Live Gemini smoke test utilized the Free Tier and successfully encountered a `429 QuotaFailure`, demonstrating the necessity of the implemented deterministic fallback.
- **Benchmark Attribution**: The 48.46% benchmark gain represents the structural capabilities of the architecture and policies, not causal live-LLM uplift.
- **Provider Restriction**: The Razorpay integration is strictly fenced to Test Mode.

---

*RecoverAI turns a failed payment into a safe, evidence-driven recovery decision where AI intelligence is bound by immutable deterministic policy.*
