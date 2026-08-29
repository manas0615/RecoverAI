# PACKAGE 19 — INTEGRATION & FAILURE TESTING
## IMPLEMENTATION PLAN
**Date:** 2026-08-29
**Project:** RecoverAI — Razorpay AI Buildathon — Track 03: AI Revenue Recovery

---

## 1. Executive Summary
Package 19 (P19) bridges the fully verified, isolated architectural subsystems of RecoverAI into a single, cohesive, executable Track 03 MVP loop. This is a pure integration phase; P01–P18 remain strictly frozen. The package contains two internal phases:
*   **P19-A (Integration Completion):** Wires the explicit architectural boundaries safely.
*   **P19-B (End-to-End & Failure Testing):** Proves system resilience, safety boundaries, and restartability.

---

## 2. P19-A — INTEGRATION COMPLETION

### 2.1 Single Authoritative Financial Execution Path
To prevent competing orchestration paths, financial execution occurs at a **single point** strictly governed by Policy. The application-level conductor for this is the `RecoveryActionService`.

There is exactly ONE financial execution authority in P19: `RecoveryActionService` invoking the frozen P08 `RazorpayAdapter` after a valid `PolicyDecision == APPROVE`.

n8n MUST NOT invoke P08 or Razorpay directly.
MCP MUST NOT create a competing direct Razorpay execution path.
Frontend MUST NOT execute financial actions.

n8n remains an orchestration/time/wait/follow-up layer.

P19 must preserve the frozen P08/P11/P12 contracts rather than inventing a second execution path. Do not redesign the architecture.

1. **Creation/Selection:** Agent selects an action via MCP.
2. **Policy Invocation:** The MCP handler delegates the request to `RecoveryActionService.execute_action()`, which invokes `PolicyEngine.evaluate()`.
3. **Policy Decision Receiver:** `RecoveryActionService` receives the decision.
4. **Authorization to Execute:** ONLY `RecoveryActionService` is authorized to initiate financial execution, and ONLY if the decision is exactly `APPROVE`.
5. **Provider Execution:** `RecoveryActionService` invokes the frozen P08 `RazorpayAdapter`.
6. **n8n Responsibility Before:** n8n may orchestrate waiting for Human Approval, but cannot authorize execution.
7. **n8n Responsibility After:** Upon P08 success, `RecoveryActionService` makes an authenticated HTTP call (using `N8N_API_KEY`) to trigger the n8n `payment-recovery.json` workflow.
8. **Duplicate Protection:** Persistent `RecoveryAction` state (e.g., `EXECUTING`, `EXECUTION_UNKNOWN`) completely prevents n8n or MCP from initiating a second P08 call for the same action.

### 2.2 Golden Path Sequence
1. Recoverable revenue-loss event arrives at the webhook endpoint.
2. Event is verified, normalized, and persisted.
3. `RecoveryCase` is created/updated by the designated case-management boundary (`RecoveryCaseManager`).
4. Revenue Intelligence analyzes the case.
5. An InterventionPlan / candidate action is produced.
6. `PolicyEngine` evaluates the candidate action.
7. **If and only if** `PolicyDecision == APPROVE`, the authorized execution path (`RecoveryActionService`) proceeds.
8. The single financial execution boundary invokes P08 (`RazorpayAdapter`).
9. n8n performs only the orchestration responsibilities defined by the architecture.
10. Razorpay Test Mode processes the bounded action.
11. Provider outcome/event arrives.
12. P09 `VerificationEngine` verifies financial truth.
13. Audit evidence is recorded in a single transaction trace.
14. P15 API exposes the resulting state.
15. P16 Warm Premium frontend displays the state/timeline.

### 2.3 Provider Correlation (Frozen P08 Boundary)
P19 consumes the EXACT provider correlation/reference identifier already emitted by the frozen P08 implementation. P19 will not invent, redefine, truncate, or reconstruct a provider reference format. 
**Trace:** Provider event $\rightarrow$ actual provider reference/correlation emitted by P08 $\rightarrow$ `RecoveryAction` $\rightarrow$ `RecoveryCase` $\rightarrow$ `VerificationEngine`.

### 2.4 Case Creation & Failure Recovery
*   **Success Path:** `WebhookIngestionService` normalizes event, persists it, and delegates to `RecoveryCaseManager.create_from_event()`. Idempotency is guaranteed via correlation ID lookups. Case initializes to `DETECTED`.
*   **Failure Recovery:** If case creation throws an exception, the persisted event remains `UNPROCESSED`. `WebhookIngestionService` logs the error and safely returns HTTP 200 (webhook accepted).
*   **Rediscovery:** Startup reconciliation fetches all `UNPROCESSED` events and retries `RecoveryCaseManager.create_from_event()`. Since the operation relies on immutable provider events and database `payment_id` constraints, reprocessing is perfectly idempotent. No new retry engine is invented.

### 2.5 Verification Invocation & Concurrency
**Correlation:** P19 must use the exact provider correlation/reference identifier emitted by the frozen P08 implementation. It must trace: `Provider Event -> Provider Reference -> RecoveryAction -> RecoveryCase -> VerificationEngine`.
**Concurrency:** Verification is invoked via three paths:
1. **Event-driven:** Webhook `payment_link.paid` arrives.
2. **Startup:** Process restart fetches `VERIFYING` / `EXECUTION_UNKNOWN` actions.
3. **n8n-driven:** Bounded polling waits expire.
**Safety:** Concurrent verification attempts must use the existing SQLite transaction and persistence semantics to converge idempotently on one authoritative result. The implementation must prevent duplicate VerificationRecords, duplicate case closure, and inconsistent terminal outcomes. Do not introduce a locking mechanism incompatible with the existing SQLite architecture. If the action is already `RECOVERED` or `NOT_RECOVERED`, it short-circuits safely. Duplicate evidence is ignored; conflicting evidence follows architecture precedence (Provider truth wins).

### 2.6 Human Approval Safety
Human approval workflows are explicitly NOT a second authorization system.
**Lifecycle:**
1. `PolicyEngine` returns `WAITING_APPROVAL`.
2. `RecoveryActionService` hands off to n8n `human-approval.json`.
3. n8n waits for human input.
4. Human approval event hits backend API.
5. Backend **RE-CHECKS** authoritative state and re-invokes `PolicyEngine`.
6. ONLY if still `APPROVE` does financial execution proceed. Human callbacks cannot authorize Razorpay mutations directly.

### 2.7 UNKNOWN State Invariant
**Rule:** `EXECUTION_UNKNOWN` means **reconciliation only**.
There is absolutely NO BLIND FINANCIAL RETRY. A network timeout does not authorize a new Razorpay POST. The action remains stuck in `EXECUTION_UNKNOWN` until authoritative evidence arrives (via webhook or reconciliation polling) to establish success or failure.

### 2.8 Audit Integration
P19 preserves all internal audit behavior of frozen P07/P09 engines. P19 only adds application-level audits (e.g., `CASE_CREATED`, `ORCHESTRATION_HANDOFF`) within the existing transactional boundaries of the application services (`RecoveryCaseManager`, `RecoveryActionService`). Every audit write guarantees correlation ID and atomic commitment alongside the business mutation.

### 2.9 Intelligence & MCP Wiring
**Role:** MCP is strictly an adapter boundary. It is NOT a second business logic engine.
*   **READ Tools:** Delegate directly to authoritative Repositories.
*   **ANALYZE Tools:** Delegate directly to P06 `RevenueIntelligenceAnalyzer`.
*   **ACT Tools:** Delegate directly to the application-level conductor (`RecoveryActionService`), which encapsulates Policy and Execution. MCP handlers do NOT implement policy, retry, or direct Razorpay calls.

### 2.10 Demo Seed Coherence
**Tool:** `scripts/seed_demo_data.py`.
Each seeded scenario must contain the minimum internally consistent domain graph required to truthfully represent that scenario. Entities must exist only when semantically appropriate.

Examples:
*   **SUCCESS:** Event $\rightarrow$ Case $\rightarrow$ Action $\rightarrow$ PolicyDecision $\rightarrow$ successful VerificationRecord $\rightarrow$ Audit
*   **PROVIDER FAILURE:** Event $\rightarrow$ Case $\rightarrow$ Action $\rightarrow$ PolicyDecision $\rightarrow$ failed execution/verification state $\rightarrow$ Audit
*   **EXECUTION_UNKNOWN:** Event $\rightarrow$ Case $\rightarrow$ Action in EXECUTION_UNKNOWN $\rightarrow$ Audit (with no fabricated successful VerificationRecord)
*   **POLICY DENIAL:** Event $\rightarrow$ Case $\rightarrow$ proposed Action / PolicyDecision DENY or SUPPRESS $\rightarrow$ Audit (with no execution/verification record pretending that execution occurred)
*   **WAITING_APPROVAL / HUMAN ESCALATION:** Event $\rightarrow$ Case $\rightarrow$ proposed Action $\rightarrow$ PolicyDecision WAITING_APPROVAL/ESCALATE $\rightarrow$ Audit (with no completed execution or verification record)

The seed must create histories that are truthful to the scenario and render correctly through the existing P16 timeline.
It uses domain repositories exclusively, keeping test/demo scenarios fully isolated from production request paths. It is deterministic, idempotent/resettable, and produces no fabricated aggregate metrics.

---

## 3. P19-B — END-TO-END & FAILURE TESTING

### 3.1 Testing Levels
*   **Unit:** Existing component tests (Frozen).
*   **Integration:** Real local components, with external provider boundaries replaced by the smallest compatible native test doubles (using existing transport abstractions; NO forced `httpx` dependencies unless standard).
*   **E2E:** Real local components connected across package boundaries.
*   **Razorpay Test Mode E2E:** Live Razorpay Test Mode, used selectively to prove the actual financial boundary.
*   **Failure Injection:** Controlled external boundary failures.
*   **Restartability:** Actual process/restart behavior using persistent SQLite truth.

### 3.2 Failure Matrix & Business Outcome Assertions
*   **Invalid/Duplicate webhook:** No case mutation. `SECURITY_EVENT` logged.
*   **LLM failure (Provider Fallback):** Safe fallback (Gemini $\rightarrow$ Groq $\rightarrow$ Deterministic). Case proceeds. *(Note: LLM fallback is distinct from financial retry).*
*   **Policy DENY/SUPPRESS:** P08 transport NOT called. Action does not execute. Domain state consistent (`SUPPRESSED`).
*   **Provider rejection:** P08 semantics applied. Correct ActionStatus.
*   **Provider timeout:** State = `EXECUTION_UNKNOWN`. NO blind financial retry. Reconciliation path exists.
*   **Amount/Currency mismatch:** Caught by P09. No false recovery.
*   **Backend restart:** Persistent state reconstructed safely via startup routines.

### 3.3 Recovery Metric Semantics
P19 produces authoritative application facts (revenue at risk, verified recovery, failure). P14 remains entirely responsible for evaluation semantics (SyntheticScenario, observed outcome, baselines). P19 will not redefine recovery-rate formulas.

---

## 4. IMPLEMENTATION FILES
*Only modifying/creating files genuinely required by the architecture boundaries.*

### Modify
*   `recoverai/ingestion/webhook.py`: Delegate successfully persisted events to `RecoveryCaseManager`. (Owned by Ingestion/Case Management).
*   `recoverai/mcp/handlers.py`: Delegate mocked tools to `RevenueIntelligenceAnalyzer` and `RecoveryActionService`. (Owned by MCP Adapter).
*   `workflows/n8n/*.json`: Configure Webhook nodes with existing P17 `N8N_API_KEY` for backend orchestration handoffs. (Owned by Workflow Orchestrator).
*   `recoverai/api/main.py`: Inject startup hooks for event/UNKNOWN reconciliation. (Owned by Application Config).

### Create
*   `recoverai/application/action_service.py` (or similar existing conductor): The application-level conductor (`RecoveryActionService`) responsible for tying MCP $\rightarrow$ Policy $\rightarrow$ Razorpay $\rightarrow$ n8n.
*   `scripts/seed_demo_data.py`: Isolated deterministic data seeder.
*   `tests/integration/test_golden_path.py`: Integration proof of the Golden Path.
*   `tests/integration/test_failure_matrix.py`: Proof of NO BLIND RETRY and policy safety.

### Frozen (Do Not Modify)
*   P01–P03 domain, P05 state machine, P06 Intelligence internals, P07 Policy Engine, P08 Razorpay Adapter, P09 Verification Engine rules, P10 LLM Gateway, P13 Audit Model, P14 Evaluation Model, P16 Warm Premium Frontend, P17 Security, P18 Native Windows Deployment.

---

## 5. FINAL DEFINITION OF DONE & SEQUENCE

**Dependency-Aware Sequence:**
1. Establish Case Creation.
2. Establish the application-level recovery progression (`RecoveryActionService`).
3. Connect P06 intelligence.
4. Connect MCP adapters.
5. Establish ONE canonical execution path.
6. Establish n8n start/resume semantics.
7. Establish verification invocation.
8. Add integration-level audit events where required.
9. Establish coherent deterministic demo seed data.
10. Prove Golden Path.
11. Prove policy/safety failures.
12. Prove provider failures.
13. Prove UNKNOWN behavior.
14. Prove duplicate/concurrency behavior.
15. Prove restartability.
16. Prove P17 security remains intact.
17. Run full regression.
18. Freeze P19.

**Done When:**
The loop safely executes from `RevenueEvent` to `VerificationRecord` strictly bound by Policy. The canonical execution path is unique. No blind retries occur on timeouts. Concurrent verification converges safely. P16 displays meaningful state. Tests pass. All original architectures remain preserved and frozen.
