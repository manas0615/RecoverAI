# Evaluation Methodology

RecoverAI separates the evaluation of its deterministic system architecture from the evaluation of live AI reasoning.

## 1. Frozen 1,500-Case Benchmark (System Throughput)

### Purpose
To measure the structural efficacy and safety of the `PolicyEngine` and closed-loop orchestration at scale, independently of live LLM quota limits.

### Methodology
- **Scenario Generator:** A synthetic scenario generator creates 1,500 deterministic `ObservableCaseEvidence` samples with varying failure contexts, attempt histories, and high-value triggers.
- **Seed:** Frozen at `42` for strict reproducibility.
- **Simulation:** The evaluator processes every scenario through the full `CaseManager` and `PolicyEngine` flow, executing mock verification steps.
- **AI Configuration:** This benchmark runs with `llm_gateway=None`, relying on the safe deterministic fallback. **It does not measure live causal AI uplift.**

### Measured Strategies
- **L0 No Intervention:** Simulates zero automated recovery.
- **L1 Naive Rule:** Blindly retries every failure immediately.
- **L2 Safe Deterministic:** Baseline heuristics with safety thresholds.
- **L3 RecoverAI Bounded:** The actual RecoverAI deterministic bounded architecture.

### Primary Results
- **L3 Simulated Gross Recovery:** ₹2,709,921.81
- **L2 Simulated Gross Recovery:** ₹1,825,326.26
- **Relative Increase:** 48.46% (L3 vs L2)

### Safety Results
- **L1 (Naive):** Triggered 519 policy violations and 218 stopping limit violations, demonstrating why blind automation is dangerous.
- **L3 (RecoverAI):** 0 policy violations. 100% adherence to attempt bounds and high-value thresholds.

## 2. Live Gemini Evaluation (AI Reasoning)

### Purpose
To validate that the integration with Gemini 3.1 Pro functions semantically (prompt formatting, JSON parsing, action mapping).

### Methodology
- **Hybrid Smoke Test:** Due to strict `429 Quota Exceeded` limits on the Free Tier, it is impossible to run 1,500 live queries. The evaluator implements a `HybridLiveGeminiStrategy` which attempts live LLM calls and gracefully falls back to deterministic rules when quota is exhausted. 
- **Results:** This proves the integration code is structurally sound and safe. It does not yield a statistically significant quantitative measure of AI quality. *(Prior fabricated quantitative AI metric claims have been explicitly removed to maintain engineering integrity.)*

## 3. Adversarial / Red-Team Validation

### Purpose
To discover and patch structural security vulnerabilities by attacking the system boundaries.

### Methodology
An offline QA subagent audited the codebase, simulating malformed provider webhooks, API abuse, and closed-loop replays. 

### Key Findings
1. **Broken Loop Correlation:** The QA agent found that the Razorpay adapter was not injecting the deterministic `Action ID`, silently breaking closed-loop tracking. **Status: Fixed.**
2. **Missing Amount Verification:** The QA agent bypassed the `VerificationEngine` by sending payloads completely missing the `amount` block. **Status: Fixed** (Fails closed to `UNKNOWN`).

## 4. Real Razorpay Evidence

### Purpose
To prove the system functions against the real Razorpay Test Mode API, validating network transport, payload semantics, and webhook signature verification.

### Methodology
Real manual test cases (A001–A005) were executed against the live Test Mode environment.
- **A001-A002:** Baseline success.
- **A003-A004:** Real discovery and fix of the correlation defect.
- **A005:** Historical policy gap discovery.

Detailed provider evidence is archived in the `evidence/razorpay/` directory.
