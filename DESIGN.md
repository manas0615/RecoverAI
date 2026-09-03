# Engineering Design

RecoverAI is architected around a strict separation of concerns between AI-driven intelligence and deterministic financial execution. It is fundamentally a state machine that orchestrates untrusted AI proposals through a rigid financial trust boundary.

## System Boundaries

The system is organized into distinct domain boundaries:

1. **Ingestion & Correlation**: Ingests incoming webhooks, cryptographically verifies them, and correlates them to the correct `RecoveryCase` and `RecoveryAction`.
2. **Intelligence (AI Boundary)**: Analyzes failure context, extracts features, and generates an `InterventionPlan`. This layer has **no authority**.
3. **Policy (Trust Boundary)**: The `PolicyEngine` evaluates the `InterventionPlan` against hard-coded deterministic rules (e.g., attempt limits, financial thresholds, systemic degradation states).
4. **Execution (Provider Boundary)**: The `RecoveryActionService` safely locks the case, executes the authorized action via the `RazorpayAdapter`, and captures the resulting provider reference.
5. **Verification**: The `VerificationEngine` independently verifies incoming `payment_link.paid` (or similar) webhooks to determine actual recovery success, relying solely on provider evidence.

## Data & Event Flow

### Request Flow
1. An operator or background task requests case analysis.
2. The `CaseManager` fetches the `RecoveryCase` and its associated `Event` and `RecoveryAction` history.
3. The history is passed to the `RevenueIntelligenceAnalyzer`.
4. The LLM generates a proposed `ActionType`.
5. The `PolicyEngine` authorizes or suppresses the action.
6. The `RecoveryActionService` applies the action to the provider.

### Closed-Loop Webhook Flow
1. Razorpay issues a `payment.failed` webhook.
2. The payload is checked for a `RecoveryActionId` inside its description/metadata.
3. If found, this is a **closed-loop failure**: a previous recovery attempt failed. The action is marked `VERIFIED_FAILURE`.
4. The failure context is persisted.
5. The system automatically replans (if within attempt limits).

## Financial Authority Boundary

The core engineering invariant is that **AI does not move money**. 

Gemini generates an `InterventionPlan`. This plan is treated as untrusted input. The `PolicyEngine` evaluates the plan. If the plan proposes `CREATE_PAYMENT_LINK`, but the case exceeds `max_attempts_per_case`, the `PolicyEngine` overrides the AI and returns `SUPPRESS`.

## State Ownership & Persistence

All state mutations occur within atomic SQLite database transactions using row-level locking to prevent race conditions during concurrent webhook deliveries. 

- `RecoveryCase`: The root aggregate. Tracks `amount_at_risk`, `status`, and `workflow_state`.
- `Event`: Immutable append-only log of all provider interactions and system decisions.
- `RecoveryAction`: The mutable execution attempt. Tracks the state transition from `PROPOSED` → `AUTHORIZED` → `EXECUTING` → `VERIFICATION_PENDING` → `VERIFIED_SUCCESS` (or `FAILURE`).

## Execution Safety Mechanisms

- **Idempotency**: Every `Event` is keyed by `(source_type, source_event_id)` to drop duplicate webhooks natively at the database level.
- **Attempt Accounting**: Every `RecoveryAction` increments the attempt counter for its parent case.
- **High-Value Policy**: Any case where `amount_at_risk` exceeds the `high_value_threshold` (e.g., ₹40,000) is deterministically routed to `ESCALATE` for human review, ignoring AI proposals for automated execution.
- **Systemic Degradation**: (Design Principle) If global failure rates spike, the `PolicyEngine` can suspend aggressive automation to protect gateway health.

## MCP / n8n Role

RecoverAI supports external interaction via the Model Context Protocol (MCP). Tools like `analyze_case` and `execute_recovery` are exposed. This allows automation platforms like n8n to orchestrate human-in-the-loop approvals for `ESCALATED` cases, while still forcing all execution through the deterministic backend constraints.
