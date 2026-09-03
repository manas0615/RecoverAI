# System Benchmark Evidence

This directory documents the frozen 1,500-scenario deterministic benchmark. It is the primary proof of RecoverAI's structural capability, throughput, and safety boundaries.

## Evaluation Methodology

The benchmark utilizes a synthetic generator to deterministically create 1,500 `ObservableCaseEvidence` instances. These scenarios simulate a variety of complex real-world payment states:
- High-value transactions triggering policy limits.
- Attempt histories simulating deep closed-loop replanning.
- Mass systemic degradation events simulating gateway outages.

To cleanly isolate the system's architectural strength from the live Gemini API (which is subject to variable latency and Free Tier quota limits), **this benchmark executes entirely with `llm_gateway=None`**. The `RevenueIntelligenceAnalyzer` falls back to its robust, deterministic behavior model.

## The Benchmark Specification
- **Seed**: `42`
- **Scenario Count**: `1,500`

## Baseline Strategies Evaluated

- **L0 (No Intervention)**: Simulates a system where no automated recovery is attempted. Revenue is recovered solely if the customer independently logs in and updates their card.
- **L1 (Naive Automation)**: Blindly issues a `CREATE_PAYMENT_LINK` for every single failure immediately, regardless of context.
- **L2 (Safe Deterministic)**: Evaluates a static, safe baseline. It suppresses retries during systemic degradation and stops after attempt bounds.
- **L3 (RecoverAI Bounded)**: The actual RecoverAI architecture. Evaluates the `PolicyEngine`, `CaseManager`, and deterministic analysis fallback executing in concert.

## Frozen Results

| Level | Strategy | Recovery Rate | Gross Simulated Recovery | Safety |
|---|---|---:|---:|---|
| **L0** | No Intervention | 8.2% | ₹569,697.22 | PASS |
| **L1** | Naive | 54.5% | ₹3,232,371.94 | **FAIL** (519 policy violations) |
| **L2** | Safe Deterministic| 32.0% | ₹1,825,326.26 | PASS |
| **L3** | **RecoverAI (Bounded)**| **47.5%** | **₹2,709,921.81** | **PASS** |

## Result Claims

1. **Safety First:** The L1 strategy highlights why blind automation is dangerous: it generated 519 policy violations and 218 stopping limit violations (runaway retries). RecoverAI (L3) achieved `0 policy violations` while strictly enforcing safety boundaries.
2. **Structural Efficacy:** RecoverAI (L3) achieved a **48.46%** higher simulated gross recovered value than the safe baseline (L2).

*(Important: This 48.46% metric isolates reproducible system orchestration behavior. It is not causal AI-judgment uplift.)*

## Detailed Artifact
The raw output of the benchmark script is archived here: [benchmark_1500_seed42.md](../../docs/reports/benchmark_1500_seed42.md)
