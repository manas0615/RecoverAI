# Closed-Loop Recovery Architecture

The closed-loop architecture handles what happens when a recovery attempt (such as a Payment Link) fails. 

## The Conceptual Flow

```
Razorpay payment failure
        ↓
case ingestion
        ↓
case classification
        ↓
AI analysis
        ↓
deterministic policy
        ↓
authorized action
        ↓
Razorpay execution
        ↓
provider evidence
        ↓
independent verification
        ↓
SUCCESS ───────→ close case
        │
        ↓
FAILURE
        ↓
correlate recovery action
        ↓
persist failure evidence
        ↓
bounded attempt state
        ↓
automatic replanning
        ↓
prior-action context
        ↓
new AI proposal
        ↓
policy re-evaluation
        ↓
next bounded action / stop
```

## The Trust Boundary

- **AI proposes**: The LLM interprets the failure context, generates the likely cause, and proposes candidate interventions.
- **Policy constrains**: The deterministic `PolicyEngine` restricts actions, enforces the `max_attempts_per_case` limits, and halts execution if thresholds are exceeded.
- **Provider executes**: The Razorpay Test Mode adapter interacts with the financial boundary.
- **Verification proves**: The `VerificationEngine` independently reads signed Razorpay webhooks to confirm outcome, explicitly checking for correct currency and exact amount matching before declaring success.
- **Failure becomes context**: Failed recoveries are safely appended to the action history and supplied to the next AI analysis phase.
- **Stopping rules control repetition**: Deterministic max attempt counters prevent runaway retry loops.
