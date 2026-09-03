# Benchmark Evidence

This directory contains the frozen 1,500-scenario deterministic benchmark results that prove the architectural and policy behavior of the RecoverAI system.

## The Benchmark Specification
- **Seed**: 42
- **Scenario count**: 1,500

## Frozen Results

| Level | Intervention Strategy | Recovery Rate | Gross Simulated Recovery | Safety |
|---|---|---:|---:|---|
| **L0** | No Intervention | 8.2% | ₹569,697.22 | PASS |
| **L1** | Naive (Retry Everything) | 54.5% | ₹3,232,371.94 | **FAIL** (519 policy violations, 218 stopping violations) |
| **L2** | Safe Deterministic | 32.0% | ₹1,825,326.26 | PASS |
| **L3** | RecoverAI (Bounded) | 47.5% | **₹2,709,921.81** | **PASS** |

## Result Claim

The bounded RecoverAI architecture achieved a **48.46%** higher simulated gross recovered value than the safe deterministic baseline (L2) in the frozen benchmark.

> **CRITICAL CONTEXT**: This benchmark explicitly used `llm_gateway=None`. It measures the system, recovery architecture, and policy behavior—not causal live-LLM uplift. Therefore, we do **not** claim that "Gemini caused 48.46% uplift".
