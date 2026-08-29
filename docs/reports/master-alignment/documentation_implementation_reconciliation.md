# RECOVERAI — DOCUMENTATION → IMPLEMENTATION MASTER RECONCILIATION
## COMPLETE MARKDOWN SPECIFICATION AUDIT
**Date:** 2026-08-29

---

## 1. PROJECT IDENTITY — ABSOLUTE

This project is strictly:
**RecoverAI — Razorpay AI Buildathon — Track 03: AI Revenue Recovery.**
It is NOT the Sovereign AI / SIH project.

*   **Local AI / Llama.cpp / Qwen3:** Explicitly **EXCLUDED** by original specs (Decision 12: "No local model is part of the architecture").
*   **XGBoost:** Specified as a candidate production MVP, but explicitly requires empirical evaluation against a Logistic Regression baseline.
*   **DataHub / Kubernetes / Distributed Queues:** Explicitly **EXCLUDED** by "Smallest Correct Change" and YAGNI rules.

---

## 2. THE MARKDOWN DOCUMENTS ARE THE ORIGINAL SPECIFICATION

The repository's Markdown documents form the authoritative specification for RecoverAI. They map exact operational, structural, and behavioral requirements for the AI integration, policy execution, and n8n boundaries.

---

## 3. COMPLETE MARKDOWN INVENTORY

| Path | Title | Apparent Purpose | Topic |
|---|---|---|---|
| `docs/system_architecture.md` | System Architecture | A. MASTER ARCHITECTURE | Entire System |
| `docs/problem_and_scope.md` | Problem & Scope | A. MASTER ARCHITECTURE | Boundaries, Goals |
| `docs/project_charter.md` | Project Charter | A. MASTER ARCHITECTURE | Rules, Golden Path |
| `docs/domain_model.md` | Domain Model | A. MASTER ARCHITECTURE | Entities, Aggregates |
| `docs/revenue_intelligence.md` | Revenue Intelligence | B. PACKAGE PLAN (P06) | ML, LLM, Cause, Value |
| `docs/ai_judgement.md` | AI Judgment | B. PACKAGE PLAN (P10) | Trust Boundary, Gateways |
| `docs/event_model.md` | Canonical Event Model | B. PACKAGE PLAN (P04) | Webhooks, Ingestion |
| `docs/recovery_state_machine.md`| State Machine | B. PACKAGE PLAN (P05) | Transitions, Retries |
| `docs/mcp_tool_contracts.md` | MCP Tool Contracts | B. PACKAGE PLAN (P11) | AI Capabilities |
| `docs/n8n_workflows.md` | n8n Workflows | B. PACKAGE PLAN (P12) | Durable Orchestration |
| `docs/policy_and_safety.md` | Policy & Safety | B. PACKAGE PLAN (P07) | Deterministic Rules |
| `docs/razorpay_integration.md` | Razorpay Integration | B. PACKAGE PLAN (P08) | API, Webhooks, Links |
| `docs/failure_recovery.md` | Failure Recovery | A. MASTER ARCHITECTURE | Safety, Errors, Retries |
| `docs/audit_and_observability.md`| Audit & Observability | B. PACKAGE PLAN (P13) | Ledger, Metrics |
| `docs/evaluation.md` | Evaluation | B. PACKAGE PLAN (P14) | Benchmarks, Baselines |
| `docs/implementation_handoff.md`| Implementation Handoff| A. MASTER ARCHITECTURE | Governance, Rules |

---

## 4. DOCUMENT AUTHORITY

*   **A. MASTER ARCHITECTURE:** Overrides all Package Plans.
*   **B. PACKAGE PLAN:** Overrides Implementation Reports (D) and Checkpoints (G).
*   **F. CHECKPOINT / IMPLEMENTATION REPORTS:** Have **no authority** over the specification. Where a checkpoint claims "Implemented" but the code is empty, the code and the specification prove the checkpoint false.

---

## 5. EXTRACTED ORIGINAL REQUIREMENTS

Over 180 concrete requirements were extracted during this forensic audit (e.g., REQ-SA-001 through IREQ-112). A sample of critical requirements:

*   **REQ-SA-001:** Probabilistic AI behavior must NEVER directly create, mutate, or control financial state/execution.
*   **REQ-SA-016:** `RecoveryCaseManager` manages lifecycle.
*   **DREQ-137:** Case cannot transition to `RECOVERED` without an authoritative `VerificationRecord`.
*   **IREQ-018:** n8n must interact with Razorpay exclusively through RecoverAI internal authenticated endpoints.
*   **IREQ-021:** Verification polling fallback must use exponential backoff.
*   **IREQ-075:** Application startup must run reconciliation on all non-terminal actions (`EXECUTING`, `VERIFYING`, etc).

---

## 6. MERMAID DIAGRAM AUDIT

Analysis of the 30+ extracted Mermaid diagrams vs. the executable architecture:

1.  **System Context Diagram:**
    *   `RP --> EI` (Webhook to Ingestion): **IMPLEMENTED**
    *   `EI --> RC` (Ingestion to Case): **DISCONNECTED**
    *   `RC --> AO` (Case to Agent): **DISCONNECTED** (n8n triggers missing)
2.  **Execution Unknown State Machine:**
    *   `EXECUTION_UNKNOWN --> VERIFYING`: **DISCONNECTED** (Engine uncalled)
3.  **Trust Boundary Diagram:**
    *   `Untrusted AI --> Policy Engine`: **IMPLEMENTED** (PolicyEngine correctly gates `create_payment_link`).
4.  **AI Gateway Router:**
    *   `Gateway --> Gemini/Groq`: **IMPLEMENTED** (Real external API routing exists in `providers.py`).

---

## 7. RECONSTRUCTED INTENDED SYSTEM

*   **INPUT/DETECTION:** Razorpay webhook $\rightarrow$ HMAC verification $\rightarrow$ Deduplication $\rightarrow$ Canonical Event $\rightarrow$ Updates/Creates `RecoveryCase`.
*   **INTELLIGENCE:** Aggregates facts, queries LLM Gateway for root cause, generates candidate interventions, computes Expected Value deterministically.
*   **CASE MANAGEMENT:** State machine transitions from `DETECTED` $\rightarrow$ `EXECUTING` $\rightarrow$ `VERIFYING` $\rightarrow$ `RECOVERED`.
*   **AGENT LAYER:** Reads case, analyzes via MCP, proposes action to Policy Engine.
*   **POLICY:** Deterministically blocks unsafe, duplicate, high-value, or suppressed actions.
*   **EXECUTION:** n8n orchestrates durable waits; calls RecoverAI Action API $\rightarrow$ Razorpay adapter creates Payment Link.
*   **VERIFICATION:** Webhooks or polling triggers `VerificationEngine` to fetch authoritative state and close case.

---

## 8. PACKAGE-BY-PACKAGE RECONCILIATION

| Package | Original Objective | Actually Built | Missing | Disconnected | Required Before P19 | P19 | P20 | Safe to Defer |
|---|---|---|---|---|---|---|---|---|
| P01-P03 | Domain & DB | Domain entities & SQLite. | None | None | No | - | - | - |
| P04 | Ingestion | Parse webhooks to Canonical. | Saves to DB. | Case creation. | **Case Creation** | Yes | Yes | - | - |
| P05 | State Machine | 14-state strict transitions. | Exists in code. | Never traversed. | - | - | - | - |
| P06 | Intelligence | Predict, Root Cause, EV. | Interfaces exist. | **Models Mocked**. | **Wire MCP to it.** | Yes | Yes | XGBoost |
| P07 | Policy Engine | Deterministic auth rules. | Fully built. | None. | - | - | - | - |
| P08 | Razorpay | API adapter, idempotency. | Fully built. | None. | - | - | - | - |
| P09 | Verification | Reconcile external state. | Engine exists. | **Never Invoked**. | **Add Verification Trigger**. | Yes | Yes | - |
| P10 | LLM Gateway | Provider router, structured out. | Fully built. | None. | - | - | - | Local AI |
| P11 | MCP Gateway | 14 Tools for AI execution. | Handlers exist. | **12/14 Mocked**. | **Wire to backend.** | Yes | Yes | - |
| P12 | n8n Workflows | Durable workflow orchestration. | JSON uploaded. | **No Triggers.** | **Add Webhook Triggers.** | Yes | Yes | Complex Branches |
| P13 | Audit | Append-only ledger. | Exists in code. | Empty (no flow). | - | - | - | - |
| P14 | Evaluation | Synthetic scenarios. | Pytest only. | No DB seeding. | **Add Seed Script.** | Yes | Yes | Full CI pipeline |
| P15 | Backend API | Expose internal endpoints. | Exists. | - | - | - | - | - |
| P16 | Frontend | UI Dashboard. | Beautiful UI. | No Data. | - | - | - | - |
| P17 | Security | HMAC, API Keys. | Exists. | - | - | - | - | - |
| P18 | Deployment | Native Windows Scripts. | Exists. | - | - | - | - | Docker |

---

## 9. PACKAGE P06 — REVENUE INTELLIGENCE
*   **Specified:** ML Risk Model (Baseline Logistic, XGBoost candidate), Root Cause LLM synthesis, Degradation Anomaly Detection.
*   **Implemented:** The interfaces exist (`analyzer.py`), but the MCP tools completely bypass them and return hardcoded dictionaries (e.g., `recovery_probability: 0.8`, `root_cause: CUSTOMER_ACTION`). XGBoost is not implemented (which is acceptable for MVP as long as the base logic is connected, but the base logic is *bypassed*).

---

## 10. PACKAGE P10 — LLM GATEWAY
*   **Specified:** External provider routing (Gemini, Groq, Hugging Face). No local AI.
*   **Implemented:** `recoverai/llm_gateway/providers.py` correctly implements external HTTP clients to Gemini and Groq, with strict Pydantic structured output validation.
*   **Verdict:** Matches specification perfectly.

---

## 11. PACKAGE P11 — MCP
*   **Specified:** 14 strictly typed capabilities.
*   **Implemented:** 14 tools are registered.
*   **Conflict Resolved:** Previous reports claimed "14 tools implemented". The Master Audit claimed "many tools are mocked". **The Master Audit is correct.** The read/analyze tools in `handlers.py` return hardcoded mock dicts. Only `create_payment_link` actually delegates to the real PolicyEngine and Razorpay Service.

---

## 12. PACKAGE P12 — N8N
*   **Specified:** Workflows triggered by API or webhooks to manage execution state.
*   **Implemented:** Workflows exist in JSON files.
*   **Missing:** There are NO trigger nodes (`n8n-nodes-base.webhook`) at the root of `payment-recovery.json`. The workflows are physically incapable of starting.

---

## 13. PACKAGE P09 — VERIFICATION
*   **Specified:** Engine that checks ambiguous external states and transitions cases to `RECOVERED`.
*   **Implemented:** `VerificationEngine` exists and is thoroughly unit tested.
*   **Missing:** A global codebase search reveals `verify_case()` is NEVER invoked by the API, webhook ingestion, or any background cron job.

---

## 14. P13, P14, P15, P16, P17, P18
*   The persistence, API, and UI layers are robust, but they sit atop an empty database because the integration pipeline is severed. `SyntheticScenarioGenerator` (P14) only runs in memory for `pytest`.

---

## 20. CROSS-PACKAGE CONNECTIVITY (ACTUAL GRAPH)

| From | To | Documented Contract | Actual Call Path | Status | Evidence |
|---|---|---|---|---|---|
| P04 (Ingest)| P05 (Case) | Create `RecoveryCase` | Disconnected | **BROKEN** | `WebhookIngestionService` saves event, exits. |
| P05 (Case) | P12 (n8n) | Trigger recovery | Disconnected | **BROKEN** | No n8n triggers in JSON. |
| P12 (n8n) | P11 (MCP) | Call AI tools | Partial | **PARTIAL** | n8n can call MCP, but n8n never starts. |
| P11 (MCP) | P06 (Intel)| Analyze risk | Disconnected | **MOCKED** | `assess_recovery_case` returns hardcoded `{prob: 0.8}`. |
| P11 (MCP) | P07 (Policy)| Authorize link | Connected | **WORKING** | `handle_create_payment_link` calls `PolicyContext`. |
| P07 (Policy)| P08 (Razor)| Execute link | Connected | **WORKING** | Reaches `execute_and_record`. |
| P08 (Razor)| P09 (Verify)| Reconcile state | Disconnected | **BROKEN** | `VerificationEngine` is never called. |

---

## 21. ORPHANED / DISCONNECTED COMPONENTS

1.  **`VerificationEngine`**: Exists, has tests, documented. Never invoked by the application. *Consequence:* Cases can never reach `RECOVERED`.
2.  **`RecoveryCaseRepository.save()` (Insert Path)**: Exists. *Consequence:* No production code instantiates a new `RecoveryCase` from a webhook.
3.  **`RevenueIntelligenceAnalyzer`**: Exists. *Consequence:* Ignored by MCP handlers in favor of mock dictionaries.
4.  **`SyntheticScenarioGenerator`**: Exists. *Consequence:* Used in tests, but unavailable to seed the UI dashboard for a demo.

---

## 22. DOCUMENTATION CLAIM VS IMPLEMENTATION REALITY

*   **Claim:** "Case Creation Implemented" (Package 05). **Reality:** Scaffolded in persistence; no application service actually invokes it on a webhook.
*   **Claim:** "14 MCP Tools Implemented" (Package 11). **Reality:** Scaffolded. 12 return mocked JSON.
*   **Claim:** "Workflows Deployed" (Package 12). **Reality:** Scaffolded. JSON lacks trigger nodes.
*   **Claim:** "Verification Integrated" (Package 09). **Reality:** Orphaned. Exists only in `tests/`.

---

## 23. REQUIREMENTS PRESENT IN ORIGINAL DOCS BUT ABSENT FROM CODE

| ID | Original Specification | Current State | Why It Matters | Proposed Package |
|---|---|---|---|---|
| REQ-1 | Event creates `RecoveryCase` | Missing | Loop stops at DB | P19 |
| REQ-2 | Verification loop invoked | Missing | Cannot prove recovery | P19 |
| REQ-3 | MCP invokes `Intelligence` | Mocked | AI is bypassed | P19 |
| REQ-4 | n8n starts via Webhook | Missing | Workflows never run | P19 |
| REQ-5 | Synthetic evaluation DB seed | Missing | Dashboard is empty | P19 |

---

## 24. ORIGINAL IDEAS SUPERSEDED / NOT REQUIRED

*   **XGBoost:** Specified as a candidate, but the hardcoded/logistic baseline is perfectly acceptable for the MVP demo, provided the *plumbing* connects to it. We do NOT need to implement XGBoost right now.
*   **Local AI (llama.cpp):** Explicitly excluded in the docs. External API usage is correct.
*   **Docker:** Excluded for the core application (native Windows).

---

## 25. DEMO-CRITICAL GAPS

To satisfy Track 03 (measured revenue recovery):
1.  A webhook must create a Case.
2.  n8n must start.
3.  MCP must consult the intelligence analyzer (not a mock).
4.  Verification must run to transition the case to `RECOVERED`.
5.  A seed script must populate the UI for the judges.

---

## 26. ACTUAL END-TO-END RECOVERY TRACE

**INTENDED TRACE:**
Detection $\rightarrow$ Case $\rightarrow$ Intelligence $\rightarrow$ MCP $\rightarrow$ Policy $\rightarrow$ Razorpay $\rightarrow$ Webhook $\rightarrow$ Verification $\rightarrow$ UI

**ACTUAL TRACE:**
Detection $\rightarrow$ `RevenueEvent` in DB. *(End of trace)*.

---

## 27. EVALUATE P19

**P19 (Integration & Failure Testing) CANNOT BEGIN DIRECTLY.**
Because the core components are disconnected, you cannot inject failures into a pipeline that does not flow.
**Recommendation:** P19 must be split into:
*   **P19-A (Integration Glue):** Connect the orphaned components (Case creation, n8n triggers, MCP wiring, Verification invocation, DB Seed).
*   **P19-B (Failure Testing):** Test the connected loop.

---

## 28. EVALUATE P20

P20 (Demo & Submission) is highly dependent on P19-A. Once the UI has data (via the seed script) and the loop works, P20 can focus strictly on the README, architecture diagrams, and recording the demo video.

---

## 29. SCORE THE CURRENT PROJECT

*   **Track 03 alignment:** 5/5 (The design is perfectly aligned).
*   **Detection:** 2/5 (Webhook validates and saves, but drops the ball).
*   **Intelligence:** 1/5 (Orphaned / bypassed by mocks).
*   **Policy Safety:** 5/5 (World-class deterministic boundary implemented).
*   **Execution:** 4/5 (Razorpay adapter works beautifully).
*   **Verification:** 1/5 (Orphaned).
*   **Frontend:** 4/5 (Beautiful but starved of data).
*   **End-to-end integration:** 0/5 (The pipeline is severed in 4 places).

---

## 32. FINAL DECISION

### A. What did we originally design?
A hybrid AI system with strict deterministic safety boundaries, orchestrated by n8n, utilizing external LLMs for root-cause synthesis.
### B. What did we actually build?
World-class domain modules, a bulletproof policy engine, a beautiful UI, and rigorous tests—all sitting completely disconnected from one another.
### C. What went wrong?
The "Implementation Reports" hallucinated connectivity. Checkpoints were approved because unit tests passed, masking the fact that the application layer never wired the modules together.
### D. What is genuinely missing?
The "glue": Case Creation from webhooks, n8n trigger nodes, Verification invocation, and a DB seed script.
### E. What is merely disconnected?
The Verification Engine and the Revenue Intelligence Analyzer.
### F. What is intentionally simplified?
The ML model (hardcoded baseline vs XGBoost).
### G. What is unnecessary for Track 03?
Local AI, Kubernetes, complex XGBoost training pipelines.
### H. What MUST be completed before P19?
Nothing. The integration glue *is* the first phase of P19.
### I. What should P19 actually do?
P19-A: Connect the 5 missing integration wires. P19-B: Failure test the loop.
### J. What should P20 actually do?
Record the demo and finalize the submission.

**DECISION:**
**OPTION B**
Complete a small integration-completion phase inside P19.

---

## 33. MOST IMPORTANT FINAL QUESTION

> If we stopped development at the current repository HEAD, would we honestly be demonstrating the RecoverAI system defined by our original Markdown architecture, or would we mainly be demonstrating isolated architectural components and a polished UI?

**We would be demonstrating isolated architectural components and a polished UI.** The core recovery loop is entirely broken. The system cannot process a webhook into a case, cannot autonomously trigger a workflow, uses hardcoded mocks for AI intelligence, and can never verify a successful payment.

> What is the MINIMUM remaining engineering work required to make the project an honest, compelling Razorpay AI Buildathon Track 03 submission?

1. Add a 10-line `RecoveryCase` creation call in the webhook ingestion service.
2. Add Webhook Trigger nodes to the n8n JSON files.
3. Wire the 3 MCP analyze handlers to the existing `RevenueIntelligenceAnalyzer`.
4. Add a FastAPI background task to invoke `VerificationEngine.reconcile_case()`.
5. Write a `scripts/seed_demo_data.py` script to populate the SQLite database.
