# 3. AI Quality & Guardrails Audit

**Status:** Architecturally Safe, but Dangerously Heuristic.

## AI vs Application Authority
The separation of concerns is strictly enforced.
- **Evidence Formatting:** The LLM receives purely factual JSON (`RecoveryEvidenceBundle`). No raw DB blobs.
- **Financial Immunity:** The LLM return schemas (`CauseAssessmentModel`, `InterventionPlanResponseModel`) completely lack financial fields.
- **Deterministic Economics:** Expected Value (EV) is calculated deterministically (`ev_minor = int(round(amount * prob))`). The AI has absolutely zero authority to modify or hallucinate a financial amount.
- **Adversarial Safety:** Prompt instructions forbid boilerplate phrases and financial calculations.

## Fallback Intelligence Audit (The Weakness)
When the LLM gateway fails (or is bypassed), the system relies on `_deterministic_cause_assessment` and `_deterministic_intervention_plan`.
- **Heuristic Faking:** The fallback hardcodes arbitrary confidences (e.g., `0.95`, `0.80`, `0.70`) to mimic AI granularity.
- **Two-Path Collapse:** All cases deterministically collapse to either `WAIT` (if systemic) or `CREATE_PAYMENT_LINK`.
- **Blind Evidence:** The fallback blindly attaches all events as `evidence_references` without actual causal linkage.
- **Risk Assessment:** Risk is **always** calculated via a hardcoded formula (`0.85 - (0.60 if systemic else failures * 0.15)`), never by an LLM.

**Verdict:** While the prompt boundaries successfully neuter LLM hallucination risk, the system's reliance on heavily simplified, hardcoded heuristics for baseline processing makes the "AI Intelligence" claim highly vulnerable to judge scrutiny. A judge could easily assert this is a simple rule-engine masquerading as AI.
