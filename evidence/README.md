# Evidence Root

This directory contains the immutable artifacts, benchmark results, and engineering validation reports that prove RecoverAI functions as designed. 

RecoverAI separates different classes of evidence to avoid blending architectural capabilities with live API constraints.

## Directory Structure

### 1. `benchmark/`
**What it proves:** The structural efficacy and safety of the `PolicyEngine` and closed-loop orchestration at scale.
**What it does NOT prove:** Live AI response quality (this benchmark uses deterministic simulated fallback to isolate system throughput).
**Primary Artifact:** [benchmark_1500_seed42.md](../docs/reports/benchmark_1500_seed42.md)

### 2. `ai-evaluation/`
**What it proves:** The system's integration with Gemini 3.1 Pro is structurally sound. The parsing, prompt generation, and fallback logic execute gracefully.
**What it does NOT prove:** A statistically significant quantitative AI metric. Live Gemini API Free Tier rate limits (`429 Quota Exceeded`) preclude mass real-time evaluation. Fabricated numerical claims have been intentionally removed.
**Primary Artifact:** [README.md](ai-evaluation/README.md)

### 3. `adversarial/`
**What it proves:** The engineering maturity of the system boundary. Contains reports from an offline hostile QA review.
**Primary Findings:** Real documentation of a closed-loop correlation defect and an amount verification bypass, both of which were successfully patched.
**Primary Artifact:** [README.md](adversarial/README.md)

### 4. `razorpay/`
**What it proves:** That the system can successfully issue, track, and verify mutating financial commands against the live Razorpay Test Mode API.
**Primary Artifacts:** Detailed individual case execution logs (e.g. `A001.md`, `A003.md`).
**Primary Artifact:** [README.md](razorpay/README.md)
