# RecoverAI — Problem & Scope

**Project:** RecoverAI
**Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery
**Document:** Problem Definition, Scope, Differentiation & Boundaries
**Status:** Architecture Foundation — Proposed for Freeze
**Version:** 1.0
**Last Updated:** 2026-08-26

---

## 1. Purpose

This document defines the exact problem RecoverAI is solving, the boundaries of that problem, the product thesis, the MVP scope, the differentiation strategy, and the capabilities that are explicitly excluded.

It exists to prevent scope drift and to ensure that implementation remains aligned with the official Track 03 requirements and with the capabilities Razorpay already provides.

The core principle is:

> **RecoverAI must solve a meaningful revenue-recovery problem that is broader and more decision-oriented than simply retrying a failed payment.**

---

# 2. Official Problem Context

Razorpay's AI Buildathon Track 03 is titled:

> **AI Revenue Recovery — Find revenue that's slipping away and win it back.**

The official brief asks builders to:

1. Detect revenue at risk.
2. Determine the right intervention.
3. Execute a bounded recovery workflow.
4. Demonstrate measured money recovered across a batch.
5. Provide compliant escalation.
6. Implement stopping rules.
7. Maintain an audit trail.

The official brief explicitly identifies several forms of revenue leakage:

* payment degradation,
* checkout abandonment,
* subscription failure,
* overdue receivables.

It also provides example directions including payment-degradation root-cause analysis, checkout recovery, failed-subscription recovery, B2B receivables, mandate retry sequencing, Hinglish voice recovery, and promise-to-pay tracking.

**Source:** Razorpay AI Buildathon, Track 03
https://razorpay.com/buildathon/

---

# 3. The Existing-Product Constraint

RecoverAI must explicitly acknowledge that payment recovery is **not an empty problem space**.

Razorpay already provides products and capabilities related to failed-payment recovery.

Razorpay's own published material describes:

* **Failed Payment Recovery**, which can automatically send payment links to customers after failed payments and use customer re-engagement to recover lost sales.
* **Intelligent Payment Retry**, which uses a next-best-action approach based on indicators including user preferences, error messages, merchant categories, offers, platforms, devices, and instrument downtimes.
* **Subscription payment retries**, where Razorpay automatically retries failed recurring payments according to its subscription retry mechanisms and notifies customers about payment failures.

Therefore, RecoverAI must **not** position itself as:

> "A better failed-payment retry mechanism."

That would create an unnecessary direct comparison with capabilities Razorpay already operates.

### Architectural consequence

The core problem must be moved one level upward:

> **How should a merchant decide which revenue-recovery action to take across different revenue-loss conditions, when to intervene, when to wait, and when to suppress intervention entirely?**

Razorpay's existing systems provide important recovery mechanisms. RecoverAI is intended to provide an **agentic decision and orchestration layer around revenue leakage**, rather than reproduce those mechanisms.

**Sources:**

Razorpay — Failed Payment Recovery
https://razorpay.com/blog/razorpay-failed-payment-recovery/

Razorpay — Intelligent Payment Retry
https://razorpay.com/blog/razorpay-intelligent-payment-retry/

Razorpay — Subscription Payment Retries
https://razorpay.com/docs/payments/subscriptions/payment-retries/

---

# 4. Problem Statement

## 4.1 Core Problem

Revenue loss can occur through multiple stages of a merchant's revenue lifecycle.

A merchant may encounter:

```text
Customer intent
      |
      v
Checkout
      |
      +---- abandonment
      |
      v
Payment attempt
      |
      +---- failure
      |
      +---- degradation / system issue
      |
      v
Successful payment
      |
      v
Recurring billing
      |
      +---- subscription failure
      |
      v
Invoice / receivable
      |
      +---- overdue
```

The correct recovery strategy is not identical for every event.

For example:

* a transient payment failure may justify waiting and retrying or redirecting the customer to a supported payment flow;
* an expired payment credential may justify a customer-facing recovery action;
* a merchant-wide payment degradation may justify suppressing individual interventions and escalating the underlying issue;
* a high-value overdue receivable may justify human escalation instead of an automated reminder sequence.

Therefore:

> **Revenue recovery is a contextual decision problem, not merely an action-execution problem.**

---

# 5. The RecoverAI Problem

RecoverAI addresses this specific problem:

> **Given a revenue-loss event and the available merchant/customer/payment context, determine the expected value of intervention, identify the likely cause, choose an appropriate bounded recovery strategy, execute only an authorized action, and verify whether revenue was actually recovered.**

This produces a complete closed loop:

```text
REVENUE EVENT
     |
     v
DETECT
     |
     v
ASSESS
     |
     v
DIAGNOSE
     |
     v
PREDICT
     |
     v
CHOOSE INTERVENTION
     |
     v
AUTHORIZE
     |
     v
EXECUTE
     |
     v
VERIFY
     |
     v
RECOVER / SUPPRESS / ESCALATE
```

---

# 6. Core Product Thesis

RecoverAI is based on five observations.

## 6.1 Not every revenue-loss event deserves intervention

The highest-value action can sometimes be:

> **Do nothing yet.**

This is particularly relevant when multiple payment failures indicate systemic degradation.

A recovery system that blindly acts on every failure can increase customer friction and operational load without increasing recovered revenue.

---

## 6.2 Intervention should be revenue-aware

A ₹500 payment and a ₹5,00,000 receivable should not necessarily receive the same recovery treatment.

RecoverAI therefore evaluates:

```text
amount at risk
×
probability of recovery
×
intervention economics
```

subject to policy and safety constraints.

The exact economic model will be formally specified and validated in `06_REVENUE_INTELLIGENCE.md`.

---

## 6.3 Root cause matters

The same observable symptom can have different causes.

For example:

```text
payment.failed
```

can represent very different situations.

RecoverAI therefore separates:

```text
EVENT
  |
  v
OBSERVATION
  |
  v
CAUSE / CAUSE HYPOTHESIS
  |
  v
INTERVENTION
```

The system must preserve the distinction between:

* confirmed fact,
* model prediction,
* inferred hypothesis,
* and unresolved cause.

---

## 6.4 Revenue recovery is sequential

A recovery process may involve:

```text
detect
  ->
intervene
  ->
wait
  ->
observe
  ->
reassess
  ->
intervene again OR stop
```

The system therefore needs explicit workflow state and stopping rules.

It cannot assume that a single model prediction or single API call represents the complete recovery process.

---

## 6.5 Recovery success must be externally verified

The system must not declare:

> "Revenue recovered"

merely because it successfully created a payment link or sent a notification.

Recovery is only counted when the authoritative financial state establishes that the expected payment occurred.

Razorpay's webhook documentation explicitly recommends using webhooks for automation and supplementing them with API verification for critical status confirmation when required. Razorpay also documents late authorization scenarios in which a payment may appear failed and later become authorized.

**Source:** Razorpay Webhooks
https://razorpay.com/docs/webhooks/

---

# 7. Primary Differentiation

RecoverAI's differentiation is **not** a new payment-collection mechanism.

The differentiation is a **revenue-recovery decision layer**.

The system attempts to answer:

> **What should happen next, given the revenue at risk, the cause, the context, the expected recovery value, the cost/friction of intervention, and the merchant's policies?**

This produces three important classes of behavior:

### Recover

Take a bounded action because intervention is justified.

### Suppress

Do not intervene because the evidence suggests intervention is currently ineffective, unsafe, redundant, or likely to create unnecessary friction.

### Escalate

Require human involvement because the value, uncertainty, policy, or failure state exceeds the system's authorized operating boundary.

---

# 8. Primary Differentiating Capability: Systemic Degradation Awareness

One of RecoverAI's central differentiators will be distinguishing:

### Individual failure

from:

### Systemic degradation.

Example:

```text
Payment A fails
Payment B fails
Payment C fails
...
Payment N fails

        |
        v

same payment method
same bank / route
same short time window
failure rate above baseline

        |
        v

SYSTEMIC DEGRADATION HYPOTHESIS
```

Instead of creating individual recovery actions for every customer, RecoverAI can:

```text
SUPPRESS INDIVIDUAL RECOVERY
        |
        v
ESCALATE / ALERT MERCHANT
        |
        v
WAIT FOR RECOVERY SIGNAL
```

The purpose is not merely to detect an anomaly.

It is to connect the anomaly to a **different revenue-recovery decision**.

This directly aligns with the official Track 03 example:

> Payment degradation → root cause → recovery action.

---

# 9. Primary Differentiating Capability: Intervention Economics

RecoverAI will not treat every possible intervention as equivalent.

Possible actions may have different:

* probability of success,
* customer friction,
* operational cost,
* monetary cost,
* delay,
* escalation burden,
* and policy requirements.

Therefore the system should estimate an intervention's expected value rather than selecting an action purely by classification.

Conceptually:

```text
Expected Recovery Value
        =
Amount at Risk
×
Probability of Recovery
```

A more complete form may consider:

```text
Net Expected Recovery Value
=
Expected Recovered Revenue
-
Intervention Cost
-
Expected Margin Loss
-
Expected Friction / Operational Cost
```

The exact formula is deliberately left open until the evaluation model is defined.

No numerical coefficient will be invented without a documented basis.

---

# 10. Primary Differentiating Capability: Recovery Suppression

RecoverAI must explicitly model:

> **No action**

as a valid intervention decision.

Possible reasons include:

* systemic payment degradation,
* low recovery probability,
* repeated unsuccessful actions,
* cooldown period,
* customer communication limits,
* policy restrictions,
* uncertain external state,
* or insufficient evidence.

This is important because an autonomous system should optimize **recovery quality**, not simply maximize the number of actions it executes.

---

# 11. Secondary Generalization

The architecture should support multiple sources of revenue leakage.

The official Track 03 brief explicitly mentions:

* payment failures,
* checkout abandonment,
* subscription failures,
* overdue receivables.

RecoverAI will therefore define a common revenue-loss abstraction:

```text
Revenue Event
      |
      v
Recovery Case
      |
      +--> Payment failure
      |
      +--> Checkout abandonment
      |
      +--> Subscription failure
      |
      +--> Overdue receivable
      |
      +--> Systemic payment degradation
```

However:

> **General support at the domain/architecture level does not imply equal implementation depth for every source.**

The initial implementation will prioritize payment-related recovery.

---

# 12. MVP Scope

## 12.1 Primary MVP

The MVP must implement one complete, robust golden path:

> **Payment-related revenue loss → recovery decision → bounded execution → verification → outcome.**

The live Razorpay integration will use capabilities actually supported by Razorpay Test Mode.

Payment Links are an important supported recovery mechanism and can be created through the Payment Links API.

Razorpay documents:

```text
POST /v1/payment_links
```

for creating Standard Payment Links.

Razorpay also documents that Payment Links can be fetched, updated, cancelled, and used for notifications.

**Sources:**

Razorpay Payment Links API
https://razorpay.com/docs/api/payments/payment-links/

Razorpay Create Standard Payment Link API
https://razorpay.com/docs/api/payments/payment-links/create-standard/

---

# 13. MVP Components

The mandatory MVP components are:

### Event ingestion

Receive, validate, deduplicate, normalize, and persist revenue events.

### Recovery Case

Represent the recoverable revenue opportunity and its lifecycle.

### Recovery intelligence

Estimate recovery probability and relevant contextual signals.

### Degradation detection

Identify patterns indicating potential systemic payment degradation.

### Root-cause engine

Construct evidence-backed cause or cause hypotheses.

### Intervention planner

Generate and rank eligible recovery strategies.

### Policy engine

Authorize, reject, suppress, or escalate proposed actions.

### Execution layer

Execute only supported, authorized recovery actions.

### Verification layer

Determine whether the intended financial outcome actually occurred.

### Audit system

Record the complete decision and execution chain.

### Evaluation harness

Measure recovery performance across a reproducible synthetic batch.

---

# 14. Live Razorpay Scope

The live/Test Mode system will intentionally be narrow.

The project will use Razorpay Test Mode to demonstrate:

1. A payment-related event.
2. RecoverAI detection and analysis.
3. Recovery decision.
4. A supported Razorpay recovery action.
5. Resulting payment event/status.
6. Verification.
7. Audit trail.

Razorpay currently documents that Test Mode allows up to **30 Payment Links per business**. Therefore, the live demo must use a small, controlled number of Payment Link scenarios.

Large-scale batch evaluation will be performed synthetically.

**Source:** Razorpay Create Standard Payment Link API
https://razorpay.com/docs/api/payments/payment-links/create-standard/

---

# 15. Synthetic Evaluation Scope

The synthetic environment will contain a much larger batch than the live Razorpay environment.

It should model combinations of:

* payment amount,
* customer history,
* payment method,
* failure reason,
* temporal behavior,
* previous recovery attempts,
* payment degradation,
* intervention eligibility,
* and recovery outcome.

The exact dataset size and distribution will be specified in `14_EVALUATION.md`.

The initial benchmark target is conceptually:

```text
Many synthetic revenue-loss cases
        |
        +--> Baseline: no intervention
        |
        +--> Baseline: naive recovery
        |
        +--> Baseline: rule-based recovery
        |
        +--> RecoverAI
        |
        v
Compare:
₹ recovered
recovery efficiency
unnecessary interventions
safety
escalations
```

The final result must use the actual executed dataset and actual measured outcomes.

---

# 16. Explicit Non-Goals

RecoverAI will **not** attempt to build:

### A replacement for Razorpay Failed Payment Recovery

Razorpay already provides failed-payment recovery functionality.

### A replacement for Razorpay Intelligent Payment Retry

Razorpay already has an intelligent retry capability.

### A new payment gateway

Razorpay remains the payment infrastructure.

### A generic fraud engine

Fraud detection is outside the primary Track 03 problem.

### A generic CRM

Customer communication is only part of a recovery workflow.

### A universal collections platform

B2B receivables are a possible extension, not the MVP.

### A generic AI chatbot

Natural-language interaction is not the core product.

### A generic workflow automation platform

n8n is an implementation component, not the product being submitted.

---

# 17. Unsupported or Dangerous Product Claims

RecoverAI must not claim:

> "We recover payments better than Razorpay."

We do not have Razorpay's proprietary production datasets or production recovery performance.

It must not claim:

> "Our AI is more accurate than Razorpay's production models."

We do not have the evidence to make that comparison.

It must not claim:

> "We recovered ₹X of real merchant revenue."

unless the result genuinely came from a real merchant environment and we have the evidence to support the claim.

Synthetic results must always be labelled as synthetic.

---

# 18. What RecoverAI Will Actually Claim

The appropriate claim is:

> **RecoverAI is an agentic revenue-recovery decision and orchestration system evaluated against reproducible baselines on a controlled synthetic revenue environment and integrated with Razorpay Test Mode for end-to-end demonstration.**

The submission can then make a stronger quantitative claim only after executing the benchmark:

> **RecoverAI recovered ₹X across N synthetic revenue-loss cases, compared with ₹Y for the selected baseline, while maintaining Z safety/operational metrics.**

The exact values will be determined experimentally.

---

# 19. Scope Priority

Features are prioritized using the following order:

## P0 — Must be excellent

* Payment revenue-loss detection
* Recovery Case
* Recovery state machine
* Recovery probability
* Root-cause analysis
* Intervention selection
* Policy gate
* Supported Razorpay action
* Verification
* Audit trail
* Golden-path tests

## P1 — Major differentiation

* Systemic degradation detection
* Recovery suppression
* Intervention economics
* Batch evaluation
* Baseline comparison
* Failure injection

## P2 — Architecture generalization

* Checkout abandonment
* Subscription recovery
* Overdue receivables
* Additional workflow playbooks

## P3 — Optional polish

* Voice
* Hinglish
* additional communication channels
* advanced merchant analytics
* additional LLM provider routing sophistication

P3 features must not delay or compromise P0/P1.

---

# 20. Scope Expansion Gate

A proposed feature may enter the implementation plan only if it passes all of the following questions:

### Relevance

Does it directly contribute to Track 03?

### Differentiation

Does it strengthen RecoverAI's unique value rather than reproduce an existing Razorpay capability?

### Evidence

Can its usefulness be measured?

### Feasibility

Can it be implemented and demonstrated reliably within the project constraints?

### Safety

Can its behavior be bounded and audited?

### Engineering value

Does it demonstrate meaningful engineering or AI judgment?

If the answer to multiple questions is "no", the feature should be rejected.

---

# 21. Problem-to-Product Mapping

| Track 03 requirement     | RecoverAI response                                   |
| ------------------------ | ---------------------------------------------------- |
| Detect revenue at risk   | Revenue event ingestion + risk model                 |
| Determine intervention   | Root-cause engine + intervention planner             |
| Execute bounded workflow | Policy gate + MCP/action layer + n8n                 |
| Payment failures         | Primary MVP                                          |
| Payment degradation      | Systemic degradation detector                        |
| Checkout abandonment     | Supported in domain model / secondary implementation |
| Subscription failure     | Secondary implementation                             |
| Overdue receivables      | Secondary implementation                             |
| Measured money recovered | Synthetic benchmark + live Test Mode demonstration   |
| Compliant escalation     | Policy engine + human escalation                     |
| Stopping rules           | Recovery state machine + policy engine               |
| Audit trail              | Append-oriented audit system                         |
| Failure handling         | Explicit failure states + verification               |

---

# 22. Success Definition

RecoverAI is successful only if all of the following are demonstrated:

### Functional success

The golden path works end-to-end.

### Financial-state correctness

The system verifies actual payment state rather than assuming it.

### Decision quality

The agent's selected interventions demonstrate measurable value against the benchmark baselines.

### Safety

Unauthorized or prohibited actions are prevented.

### Reliability

Duplicate, delayed, invalid, and uncertain events do not cause unsafe behavior.

### Evaluation

The batch benchmark produces reproducible metrics.

### Explainability

Each material action can be reconstructed from the audit trail.

---

# 23. Failure Definition

The project should consider the following outcomes unacceptable:

* duplicate financial action caused by duplicate webhook processing,
* treating an ambiguous external state as a confirmed failure,
* LLM output bypassing policy,
* an unsupported Razorpay API action being presented as functional,
* benchmark results that cannot be reproduced,
* synthetic results presented as real merchant results,
* fabricated performance numbers,
* unexplained financial mutations,
* or an implementation that exists only for the cinematic demo while the evaluation path is non-functional.

---

# 24. Core Product Boundary

The complete RecoverAI product boundary is:

```text
                REVENUE EVENT
                      |
                      v
             REVENUE INTELLIGENCE
                      |
                      v
               RECOVERY CASE
                      |
                      v
              AGENTIC DECISION
                      |
                      v
              POLICY / SAFETY
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
     RECOVER       SUPPRESS      ESCALATE
        |
        v
     EXECUTE
        |
        v
     VERIFY
        |
        v
      RESULT
        |
        v
     AUDIT + MEASURE
```

The core product is therefore:

> **A bounded decision-and-orchestration layer for revenue recovery.**

Not a payment gateway.

Not a retry engine.

Not a chatbot.

Not a CRM.

Not a generic automation platform.

---

# 25. Boundary for Future Documents

This document defines **what problem we are solving**.

The next documents will define **how the system solves it**:

```text
02_SYSTEM_ARCHITECTURE.md
        |
        v
03_DOMAIN_MODEL.md
        |
        v
04_EVENT_MODEL.md
        |
        v
05_RECOVERY_STATE_MACHINE.md
        |
        v
06_REVENUE_INTELLIGENCE.md
        |
        v
07_AI_JUDGMENT.md
        |
        v
08_POLICY_AND_SAFETY.md
        |
        v
09_RAZORPAY_INTEGRATION.md
        |
        v
...
```

Any future architecture decision must remain consistent with the scope and non-goals established here unless an explicit Architecture Decision Record changes them.

---

# 26. External Evidence Used

## Razorpay Buildathon

Razorpay AI Buildathon — official brief and Track 03 requirements
https://razorpay.com/buildathon/

## Razorpay Failed Payment Recovery

Razorpay — Introducing Failed Payment Recovery
https://razorpay.com/blog/razorpay-failed-payment-recovery/

## Razorpay Intelligent Payment Retry

Razorpay — Introducing Intelligent Payment Retry
https://razorpay.com/blog/razorpay-intelligent-payment-retry/

## Razorpay Subscription Payment Retries

Razorpay — Payment Retries
https://razorpay.com/docs/payments/subscriptions/payment-retries/

## Razorpay Payment Links

Razorpay — Payment Links APIs
https://razorpay.com/docs/api/payments/payment-links/

Razorpay — Create Standard Payment Link
https://razorpay.com/docs/api/payments/payment-links/create-standard/

## Razorpay Webhooks

Razorpay — About Webhooks
https://razorpay.com/docs/webhooks/

Razorpay — Validate and Test Webhooks
https://razorpay.com/docs/webhooks/validate-test/

---

# 27. Verification Notes

The following external facts used in this document were verified against current Razorpay documentation on 2026-08-26:

* Track 03 requires detection, intervention selection, bounded execution, measured batch recovery, escalation, stopping rules, and auditability.
* Razorpay already provides Failed Payment Recovery.
* Razorpay already provides Intelligent Payment Retry.
* Razorpay Subscriptions have built-in retry behavior for failed recurring payments.
* Payment Links are an available Razorpay payment-collection mechanism.
* Standard Payment Links can be created using `POST /v1/payment_links`.
* Test Mode currently limits Payment Link creation to 30 per business.
* Razorpay recommends webhooks for automation and API verification for critical status confirmation when required.
* Razorpay documents late authorization behavior and the need to account for asynchronous payment state.

All external capabilities must be re-verified immediately before their implementation package is started because vendor APIs, product behavior, and limits can change.

---

# 28. Freeze Statement

This document freezes the following strategic decision:

> **RecoverAI will compete on intelligent revenue-recovery decisioning and orchestration, not on reproducing Razorpay's existing payment-recovery mechanisms.**

The P0 implementation will focus deeply on payment-related revenue recovery.

Systemic payment-degradation detection, intervention economics, suppression, measurable batch evaluation, verification, safety, and failure recovery are the principal differentiating engineering capabilities.

Broader revenue-loss sources will be treated as extensions of the same Recovery Case architecture rather than as separate products.

**Status:** Proposed for architecture freeze.
