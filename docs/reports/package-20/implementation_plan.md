# PACKAGE 20 — FINAL CORRECTED IMPLEMENTATION PLAN

## 1. Plan Status
READY FOR IMPLEMENTATION.

## 2. P19 Frozen Baseline
- **SHA:** 552421c6fa8afe46bad4137927c6dd74b16c58b0
- P19 established the core integration: Event → Case, Intelligence → Policy, Policy → Execution. Single financial execution authority, n8n orchestration, human approval, UNKNOWN safety, provider verification, demo seeding, Analyze Case, P17 security, P18 deployment, and the Warm Premium frontend. P19 is FROZEN.

## 3. Original P20 Intent
To assemble the verified components from P01–P19 into a bulletproof, evidence-driven public submission centered on the bounded revenue-recovery control loop, run a synthetic batch evaluation, and record a 3–5 minute judge pitch.

## 4. Current Repository Reality
- Dashboard analytics currently lack explicit API backing for some metrics.
- Real AI inference: NOT EXECUTED. Requires `GEMINI_API_KEY` configuration.
- Razorpay Test Mode: NOT EXECUTED. Requires credentials and webhook infrastructure.
- `seed_demo_data.py` populates base cases, but UI state relies on actual analysis execution.

## 5. Corrected P20 Gap Analysis
- **API Extension:** Metrics must be derived from existing authoritative domains (e.g., P09 VerificationRecord, RecoveryCase).
- **Seed Data Polish:** Ensure truthful seeding. Do NOT fabricate AI recommendations to make the UI look complete.
- **UI Polish:** Make Dashboard metrics compute legitimately. Implement "Why this recommendation?" and clear Analytics state machine.
- **Documentation & Demo:** Documentation Truth Audit, README overhaul, 3–5 minute pitch video, and P14 evaluation execution.

## 6. Real AI Provider Plan
- **Status:** Not yet executed. P20 will configure and validate the selected provider.
- **Environment:** Add `LLM_PROVIDER=gemini` and `GEMINI_API_KEY` to `.env.example`.
- **Selection:** Use `ConcreteLLMGateway` targeting `gemini-2.5-pro` (or similar).
- **Secret Handling:** Keys read server-side only via `os.environ`.
- **Fallback:** Cascade to Groq -> HuggingFace -> Deterministic Rules. Do NOT label deterministic output as LLM output.

## 7. Analyze Case Plan
- **Flow:** User clicks [Analyze Case]. `intelligence.analyze()` generates recommendations; `PolicyEngine` evaluates them. Zero financial execution.
- **State Machine:** NOT_ANALYZED, ANALYZING, ANALYZED, ANALYSIS_FAILED, ANALYSIS_UNAVAILABLE. Every demo case has a truthful analysis state.
- **Constraint:** Analyze Case MUST NOT directly execute Razorpay.

## 8. Evidence-First Plan
- **Structure:** 
  1. CASE CONTEXT
  2. WHAT HAPPENED?
  3. EVIDENCE
  4. [ ANALYZE CASE ]
  5. WHAT DID AI UNDERSTAND?
  6. WHAT DID AI SUGGEST?
  7. WHAT DID POLICY DECIDE?
  8. WHAT DID THE SYSTEM DO?
  9. WHAT VERIFIED THE RESULT?
  10. AUDIT TIMELINE
- **Source:** Evidence must be sourced from actual legitimate records (RevenueEvent, RecoveryCase, provider metadata, etc.). No AI-generated evidence.

## 9. AI Provenance
- Display compact, truthful indicators (e.g., "Analysis Source: Gemini", "Model: gemini-2.5-pro" or "Analysis Source: Deterministic Fallback").
- Only display information actually known from the application runtime. Never expose secrets.

## 10. AI Validation
- Validate actual outputs across 6 scenarios: (A) Straightforward payment failure, (B) High-value/sensitive case, (C) Systemic degradation, (D) EXECUTION_UNKNOWN, (E) POLICY_DENIAL / SUPPRESS, (F) HUMAN_ESCALATION.
- Assess specificity, evidence grounding, recommendation quality, safety, unsupported claims, hallucination, generic language, and blind retry risk.

## 11. AI-Slop Evaluation
- Flag outputs that invent evidence, confidence, customer behavior, or historical events.
- Define explicit handling for poor outputs (e.g., rejection or deterministic fallback) rather than manually rewriting them.

## 12. Financial Analytics
- Implement truthful analytics on the Dashboard. Retain the Warm Premium editorial hierarchy.
- **Hierarchy:** Recovery Overview -> Key Financial Metrics -> Outcome Distribution -> Recovery Funnel (only if defensible) -> Recent Cases.
- Allow drill-down from metrics to underlying cases (e.g., clicking Verified Recovered links to those specific cases) where supported.

## 13. Metric Provenance
- P20 MUST inspect the actual P19/P09 domain model to determine authoritative truth before implementing metrics.
- **Verified Recovered Authority:** Inspect P09 VerificationRecord / provider evidence / RecoveryAction. Do not let the frontend invent "verified".
- **Contract Definition Requirements:** Name, Source, Formula, Numerator, Denominator, Included, Excluded, Currency rule, Authoritative state, Availability condition, UI behavior, and Classification (SUPPORTED, COMPUTABLE AFTER API EXPOSURE, NOT COMPUTABLE, OPTIONAL).

## 14. Currency Safety
- **Rule:** INR + USD = invalid aggregation.
- No metric may sum monetary values across currencies without a legitimate conversion architecture.
- Group by CurrencyCode or show separate currency values.

## 15. Demo Dataset
- Seed a minimum of 7 curated judge-critical scenarios: SUCCESS, FAILURE, UNKNOWN, DENIAL, ESCALATION, DUPLICATE, LIVE DETECTED.
- **Rule:** Do NOT require the seed script to create fabricated LLM_RECOMMENDATION_CREATED events. Seed only truthful case/evidence.

## 16. 30-Case Decision
- **Decision:** NO. 30 real Razorpay cases are NOT required. A curated set of 7 cases comprehensively proves all safety invariants and pipeline states.

## 17. Razorpay Test Mode
- **Status:** Not yet executed.
- **P20 Task:** Attempt controlled Test Mode execution using `P08 RazorpayAdapter` if legitimate credentials/webhooks are available.
- Explicitly separate seeded deterministic demo from real Razorpay provider proof.

## 18. Webhook Proof
- If Test Mode is available, demonstrate the P09 webhook path (`/webhooks/razorpay/{merchant_id}`) finalizing the VERIFIED_SUCCESS state.

## 19. Dashboard
- **Hierarchy:** Recovery Overview -> Key Financial Metrics -> Outcome Distribution -> Recovery Funnel -> Recent Cases.
- Implement explicit "Data Unavailable" for unsupported metrics. Ensure no fake metrics.
- **Distinguish:** Case Outcome Distribution (Counts) vs Financial Outcome Distribution (Money).

## 20. Cases
- Ensure Cases list filters properly. Connect Dashboard metrics to Case List filtering where technically supported.

## 21. Case Detail
- **Hero Screen:** Case Detail communicates "Why did this happen?", "What evidence exists?", "What did AI suggest?", "What did policy decide?", etc.
- **Why this recommendation?:** Implement progressive disclosure (`[ View supporting evidence ]`).

## 22. State UX
- Ensure visual clarity: VERIFIED_SUCCESS (restrained green), FAILURE (restrained red/error), DENIAL/SUPPRESS (restrained red/policy-negative), UNKNOWN (restrained amber), WAITING_APPROVAL/ESCALATION (restrained amber).

## 23. Audit UX
- Make the timeline human-first (Readable event, actor, timestamp, state transition, explanation).
- Technical data (raw JSON) should be secondary, accessible via `[ View technical evidence ]`.

## 24. Responsive
- Verify on tablet/mobile sizing. Ensure no horizontal overflow in Case Tables, Charts, or Timeline.

## 25. Accessibility
- Add basic ARIA labels on Dashboard Metrics. Ensure keyboard navigability, focus states, and adequate contrast. Final analytics must have textual equivalents.

## 26. Stitch
- Preserve existing React UI structure (Project 1051231661397186252, Design System assets/15122457507156157995).
- Do NOT create another project. Only use Stitch if an actual visual/interaction gap remains.

## 27. Final Judge Journey
- 0:00 Problem / value proposition
- 0:20 Dashboard (financial impact)
- 0:45 Recovery Cases
- 1:00 Select SUCCESS case (complete value loop)
- 1:10 Evidence
- 1:20 Analyze Case
- 1:35 Actual AI output
- 1:55 Policy Decision
- 2:10 Execution
- 2:30 Verification
- 2:45 Audit
- 3:00 DENIAL or UNKNOWN (Safety proof: AI ≠ authorization, no blind retry)
- 3:30 ESCALATION (risk-sensitive human intervention)
- 4:00 Evaluation / metrics
- 4:30 Closing

## 28. Primary Demo
- Target: Real AI provider + Razorpay Test Mode (where executed/available).

## 29. Backup Demo
- Target: Deterministic seeded cases using the same production UI.
- Constraint: MUST NOT claim live LLM inference or live Razorpay execution unless it actually happened.

## 30. Demo Reset
- Inspect the real configured SQLite database path.
- Provide the correct Windows-safe reset/reseed procedure (e.g. via PowerShell).

## 31. Fresh Windows Setup
- Rehearse deployment using native Windows PowerShell:
  `Copy-Item .env.example .env`
  `Copy-Item frontend\.env.example frontend\.env`
  `.\scripts\start-all.ps1`
  `.\scripts\check-health.ps1`
  (Inspect actual scripts before finalizing).

## 32. P14 Evaluation
- P20 MUST utilize existing P14 infrastructure to run synthetic batch evaluations.
- Compare RecoverAI vs No Intervention vs Rule-Based only where supported. Do NOT invent uplift numbers.

## 33. Failure/Safety Rehearsal
- Explicitly demonstrate Scenario D (DENIAL) and Scenario C (UNKNOWN) to prove the policy engine prevents double-execution and incorrect authorization. Define failure modes and fallbacks for external dependencies.

## 34. Security Release Audit
- Verify `.gitignore` excludes `.env`, `data/`, `node_modules/`. Verify no `N8N_API_KEY` leaks to frontend. Verify P17 HMAC validation remains active. No browser-side financial execution.

## 35. Documentation Truth Audit
- Search for and remove any stale claims about "local sovereign inference", "Qwen3", "llama.cpp", "XGBoost", "30 real Razorpay cases", or unsupported ML metrics from the README and source.

## 36. Architecture Diagrams
- Create Mermaid diagrams in README: System Architecture, AI / Policy Trust Boundary, Financial Execution Path, Verification Path, UNKNOWN / Failure Safety Flow.

## 37. README
- Rewrite `README.md` entirely. Include Track 03 mission, Setup instructions, Architecture, AI context, Safety Guarantees, Evaluation metrics, and Demo script.

## 38. Screenshots
- Curate screenshots for: Dashboard, Cases List, Case Detail (SUCCESS), Case Detail (DENIAL), Audit Timeline. Only capture states that actually exist. No secrets.

## 39. Video
- Record a 3-5 minute MP4 walking through the Final Judge Journey. Do not use fabricated screenshots.

## 40. Submission
- Final package: source code, README, diagrams, video, setup instructions, evaluation results. Clean Git, no secrets, no stale artifacts.

## 41. File-Level Plan
| File | Action | Purpose | Requirement | Priority | Dependency | Verification |
|------|--------|---------|-------------|----------|------------|--------------|
| `recoverai/api/main.py` | MODIFY | Expose existing domain truth for metrics | Analytics | CORE | None | API Tests |
| `frontend/src/pages/Dashboard.tsx` | MODIFY | Bind API metrics legitimately | UI Polish | CORE | API | Browser |
| `frontend/src/pages/CaseDetailView.tsx` | MODIFY | Add AI provenance, "Why this recommendation?", Human-first audit | UI Polish | CORE | API | Browser |
| `scripts/seed_demo_data.py` | MODIFY | Seed 7 canonical truthful scenarios (NO fabricated AI) | Demo Data | CORE | None | DB Check |
| `README.md` | MODIFY | Final submission docs | Submission | CORE | Metrics | Manual |
| `.env.example` | MODIFY | Add GEMINI placeholders | Security | CORE | None | Manual |

## 42. Implementation Sequence
- **PHASE 0:** Runtime/repository baseline.
- **PHASE 1:** Environment/provider configuration.
- **PHASE 2:** Real AI provider execution and validation.
- **PHASE 3:** Evidence + Analyze Case product validation.
- **PHASE 4:** AI → Policy → Execution → Verification → Audit proof.
- **PHASE 5:** Financial analytics + metric provenance.
- **PHASE 6:** Demo case curation.
- **PHASE 7:** Razorpay Test Mode + webhook proof.
- **PHASE 8:** P14 batch evaluation.
- **PHASE 9:** UX / responsive / accessibility polish.
- **PHASE 10:** Failure/safety rehearsal.
- **PHASE 11:** Fresh Windows environment rehearsal.
- **PHASE 12:** Security + documentation truth audit.
- **PHASE 13:** Architecture diagrams.
- **PHASE 14:** README.
- **PHASE 15:** Screenshot capture.
- **PHASE 16:** Demo script.
- **PHASE 17:** Video.
- **PHASE 18:** Submission package.
- **PHASE 19:** Final regression + release freeze.

## 43. Testing Strategy
- `uv run pytest tests/`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy recoverai/ tests/`
- `cd frontend && npm run build`
- Actual browser testing, real provider testing, Razorpay Test Mode testing, and demo journey rehearsal.

## 44. Core / High-Value / Optional / Not Required
- **CORE:** Real provider config, actual AI validation, evidence-driven Case Detail, AI → Policy separation, truthful metrics, metric provenance, curated demo scenarios, final UX, security/release audit, README, architecture diagrams, demo journey.
- **HIGH-VALUE:** Razorpay Test Mode proof, real webhook demo, P14 batch evaluation, dashboard metric drilldown, stronger analytics.
- **OPTIONAL:** Extra charts, extra animations, additional noncritical Stitch references, additional background cases.
- **NOT REQUIRED:** New architecture, XGBoost, llama.cpp, Qwen3, Kubernetes, new database, new auth, new orchestration.

## 45. Entry Gates
- P19 is frozen, core integration connected, Analyze Case exists, seed works, P17/P18 works.

## 46. Exit Gates
- **Product:** Dashboard, Cases, Case Detail, System Health work correctly.
- **AI:** Analyze Case, actual provider, actual outputs, quality validation.
- **Evidence:** Evidence visible, recommendation grounded.
- **Policy:** Independently evaluated.
- **Execution:** Authorized only.
- **Verification:** Actual provider truth where executed.
- **Analytics:** Truthful, currency-safe, provenance documented.
- **Demo:** Primary path rehearsed, backup path rehearsed.
- **Submission:** README, diagrams, screenshots, video, evaluation, setup documentation.
- **Security:** Clean.
- **Regression:** Full suite green.

## 47. Acceptance Criteria
1. P19 remains intact.
2. Real AI can be configured and executed where credentials exist.
3. Actual AI output is never fabricated.
4. Analyze Case is a genuine user interaction.
5. Evidence is visible and grounded in actual records.
6. AI recommendation is separate from Policy.
7. Policy remains authoritative.
8. Execution remains single-authority.
9. Verification remains authoritative.
10. UNKNOWN remains reconciliation-only.
11. DENIAL remains non-executing.
12. ESCALATION remains human-in-the-loop.
13. Financial metrics are truthful.
14. Currency is never mixed.
15. Metric definitions are documented.
16. Demo cases are internally consistent.
17. 30 real Razorpay cases are NOT required.
18. Seven curated scenarios are sufficient as the minimum judge set.
19. Real Razorpay proof is separately identified from seeded demo proof.
20. Dashboard communicates financial impact.
21. Case Detail communicates evidence and reasoning.
22. Audit trail is human-readable.
23. Warm Premium remains unchanged.
24. Stitch project is unchanged.
25. Final documentation is truthful.
26. Fresh Windows setup is reproducible.
27. Security release audit passes.
28. Final demo is rehearsed.
29. Full regression passes.
30. Git is clean at final release.

## 48. Required Matrices

### A. P20 Workstream Matrix
| Workstream | Current State | P20 Work | Priority | Verification |
|------------|---------------|----------|----------|--------------|
| AI Auth    | Unconfigured  | Setup Gemini/Groq | CORE | Runtime |
| Analytics  | Mocked/Partial| Implement derived Metrics | CORE | UI Test |
| Seed Data  | Missing states| Curate 7 Scenarios | CORE | SQLite |
| Docs       | Outdated      | Truth Audit & Rewrite | CORE | Manual |

### B. AI Validation Matrix
| Scenario | Provider | Executed | Output | Specific | Grounded | Safe | Verdict |
|----------|----------|----------|--------|----------|----------|------|---------|
| A. SUCCESS | TBD      | No       | Pending| TBD      | TBD      | TBD  | PENDING |
| B. HIGH-VALUE | TBD   | No       | Pending| TBD      | TBD      | TBD  | PENDING |
| C. DEGRADATION | TBD  | No       | Pending| TBD      | TBD      | TBD  | PENDING |
| D. UNKNOWN | TBD      | No       | Pending| TBD      | TBD      | TBD  | PENDING |
| E. DENIAL  | TBD      | No       | Pending| TBD      | TBD      | TBD  | PENDING |
| F. ESCALATION | TBD   | No       | Pending| TBD      | TBD      | TBD  | PENDING |

### C. Financial Metric Matrix
| Metric | Source | Formula | Numerator | Denominator | Currency | Availability | UI |
|--------|--------|---------|-----------|-------------|----------|--------------|----|
| Revenue at Risk | recovery_cases | SUM(amount) | Amount | N/A | Partitioned | SUPPORTED | Hero |
| Verified Recovered | VerificationRecord | SUM(amount) | Amount | N/A | Partitioned | API EXPOSURE | Hero |

### D. Demo Scenario Matrix
| Scenario | Evidence | Analyze | AI | Policy | Execution | Verification | Demo Purpose |
|----------|----------|---------|----|--------|-----------|--------------|--------------|
| SUCCESS  | Seeded   | UX Flow | Truthful| APPROVE | SUCCESS | VERIFIED | Value Prop |
| DENIAL   | Seeded   | UX Flow | Truthful| SUPPRESS| BLOCKED | N/A      | AI ≠ Auth |

### E. Provider Matrix
| Provider | Configured | Reachable | Executed | Role |
|----------|------------|-----------|----------|------|
| Gemini   | No         | Pending   | No       | Primary AI |
| Razorpay | No         | Pending   | No       | Test Execution |

### F. Frontend Route Matrix
| Route | Runtime | Data | Demo Purpose | Final Action |
|-------|---------|------|--------------|--------------|
| /     | React   | API  | Financial Impact | Bind Metrics |
| /cases/:id | React | API | Lifecycle Evidence | Polish Evidence |

### G. Security Matrix
| Boundary | Implemented | Tested | Runtime Verified |
|----------|-------------|--------|------------------|
| Secrets  | .gitignore  | Yes    | Pending          |
| Direct Exec| Blocked   | Yes    | Pending          |

### H. Demo Reliability Matrix
| Dependency | Primary Path | Failure | Backup | Presenter Action |
|------------|--------------|---------|--------|------------------|
| LLM API    | Live Inference | Timeout | Deterministic Seed | State Fallback |

### I. P20 Exit Gate Matrix
| Gate | Requirement | Evidence | Status |
|------|-------------|----------|--------|
| Entry| P19 Frozen  | Git SHA  | PASSED |
| Exit | Metrics True| UI Render| PENDING|

## 49. Final Freeze Conditions
- No uncommitted code. No broken tests. No exposed secrets. Video recorded. Git is clean.

## 50. Final Decision
A. READY FOR GEMINI P20 IMPLEMENTATION

## 51. Stop Conditions
Corrected plan generated. Handoff to Gemini 3.1 Pro (High).
