# Package 08 Implementation Report

## Provider Transport

The P08 implementation leverages Python's built-in `urllib.request` library as the narrow provider abstraction for communicating with the Razorpay API. This adheres to the boundary requirement of strictly relying on natively available tooling instead of broad third-party dependencies (`requests`, `httpx`).

## Authorization Gate

Before dispatching any payload to the Razorpay network boundary, the adapter actively verifies:

- **Policy**: `decision == PolicyDecisionValue.APPROVE`
- **Case Alignment**: `decision.case_id == action.case_id`
- **Action Semantics**: `action.action_type == ActionType.CREATE_PAYMENT_LINK`
- **Test Mode Security**: `config.mode == "test"`

Any failure at this boundary fails closed, rendering a `FAILED_BEFORE_SEND` response and guaranteeing un-authorized operations never hit the network. P08 strictly validates these authorization contracts and intentionally avoids recomputing policy engine rules (e.g., attempt limits, duplicates, terminal states), which are strictly P07's responsibility.

## Correlation & Uniqueness Strategy

The Razorpay API documentation for creating Payment Links specifies that `reference_id` must be unique per link and carries a maximum length of 40 characters. 

**This is NOT provider-level HTTP idempotency**, and we explicitly avoid inventing an `X-Razorpay-Idempotency-Key` or similar header that is undocumented for this endpoint.

Our terminology and correlation constraints are:
- **`reference_id`**: Acts purely as a provider correlation and uniqueness constraint (collision-resistant hash of `action_id` capped at 40 chars).
- **RecoverAI Action Identity**: Internal logical action state maintained within P05 and P03.
- **P07 Duplicate Protection**: Safely prevents repeating execution logically before generation reaches P08.

## Execution and Timeout Semantics

When `urllib.request` reaches the provider transport but a network timeout occurs (or a connection is severed post-transmission), P08 designates the attempt as `TIMEOUT_UNKNOWN` (or `NETWORK_UNKNOWN`). 

- P08 intentionally **does not automatically retry** network executions.
- The outcome forces the action into `EXECUTION_UNKNOWN` through P05's domain transition boundary (`action.record_verification`).
- True recovery validation (e.g., distinguishing between a Payment Link actually created by a timed-out request vs. completely unreceived) remains strictly the responsibility of P09's Reconciliation engine. P08 simply asserts the network status is unknown.

## Response Semantics

A returned result of `SUCCESSFUL_REQUEST` solely implies Razorpay accepted the request and provisioned the Payment Link correctly. It **does NOT** denote recovery execution has succeeded or that the transaction holds economic value. P09 handles this evaluation.
