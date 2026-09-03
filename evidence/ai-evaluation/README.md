# Live Gemini Evaluation Evidence

This directory documents the hybrid live-Gemini smoke test. 

## Hybrid Smoke Test Results

We ran the evaluation framework in hybrid mode to validate the live integration with the Gemini API and the system's fault tolerance under stress.

**Observed behavior**:
- 50 scenarios evaluated
- 10 live Gemini invocations attempted
- Gemini endpoint was successfully reached.
- The Free Tier quota was exhausted, returning a `429 QuotaFailure`.
- The system safely caught the `429` error and gracefully fell back to the deterministic analysis pathway (`GEMINI_FAILED_FALLBACK`).
- No crashes occurred.
- 0 policy violations occurred.

## Claim
Real Gemini integration and failure-safe fallback were validated under live quota exhaustion.

*(Note: Gemini response-quality evaluation was not successfully measured in this run because the provider returned 429s, demonstrating the necessity of the deterministic fallback.)*
