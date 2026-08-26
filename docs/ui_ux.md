# RecoverAI — UI/UX Specification

**Project:** RecoverAI  
**Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery  
**Document:** Production UI/UX System, Stitch Design Source of Truth & Antigravity Frontend Implementation Contract  
**Status:** Architecture Foundation — Proposed for Freeze  
**Version:** 1.0  
**Last Updated:** 2026-08-26

---

# 1. Purpose

This document defines the complete UI/UX direction for RecoverAI.

It exists because the frontend is not a decorative layer placed on top of the backend.

The frontend is the judge-facing proof surface for:

- revenue at risk,
- recovery decisions,
- policy boundaries,
- financial actions,
- verification,
- failure recovery,
- auditability,
- evaluation results,
- and AI judgment.

The frontend must therefore communicate the engineering quality of the system.

The core requirement is:

> **A judge should be able to understand what RecoverAI is doing, why it is doing it, what it actually did, and whether the money was recovered — without opening the source code.**

---

# 2. Stitch + Antigravity Strategy

RecoverAI will use Google Stitch as the visual design source of truth and the Stitch MCP inside Antigravity to transfer that design intent into the frontend implementation.

Google's current official design-to-code Codelab documents this workflow:

```text
Google Stitch
    ↓
high-fidelity visual design
    ↓
Stitch MCP
    ↓
Antigravity
    ↓
fetch Design DNA / design context
    ↓
generate DESIGN.md
    ↓
React + Tailwind implementation
    ↓
integrated browser verification
    ↓
visual refinement
```

Google explicitly describes Stitch as a high-fidelity UI design tool and documents using the Stitch MCP to connect designs to Antigravity, extract design tokens/design context, scaffold React/Tailwind, and visually compare the implementation against the Stitch design. citeturn749763search0turn749763search4

This is the intended workflow for RecoverAI.

---

# 3. Critical Distinction

Stitch owns:

- visual language,
- layout,
- typography,
- color,
- spacing,
- component appearance,
- interaction presentation,
- visual hierarchy.

RecoverAI backend owns:

- business state,
- financial truth,
- policy decisions,
- recovery amounts,
- workflow state,
- audit records,
- evaluation results.

The frontend must never invent backend truth to make the interface look complete.

---

# 4. Frontend Architecture

The final frontend should conceptually be:

```text
                    RECOVERAI FRONTEND

                         Browser
                            |
                            v
                    React Application
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
        API Client     UI State      Realtime /
                                   Polling Events
              |             |             |
              +-------------+-------------+
                            |
                            v
                     RecoverAI API
                            |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
   Recovery API        Audit API          Evaluation API
        |                   |                   |
        +-------------------+-------------------+
                            |
                            v
                         Backend
```

The browser must never directly access:

- Razorpay secret credentials,
- LLM provider credentials,
- database,
- n8n admin API,
- internal MCP server,
- evaluator hidden ground truth.

---

# 5. Frontend Implementation Target

The intended implementation target is:

```text
React
+
TypeScript
+
Tailwind CSS
+
component architecture
+
typed API client
```

The exact versions must be verified against the repository during Package 16.

Stitch should inform the visual implementation; it must not dictate unsafe or unnecessarily complex application architecture.

---

# 6. Design Objective

The UI should feel like:

> **A modern financial operations command center with AI decision transparency.**

It should not feel like:

- a generic SaaS dashboard template,
- a neon AI demo,
- a cryptocurrency dashboard,
- a chatbot wrapped around payments,
- or a visually overloaded admin panel.

The visual personality should communicate:

```text
Trust
Precision
Clarity
Control
Speed
Financial seriousness
```

---

# 7. Design Principles

The complete interface follows:

## 7.1 Explain the Important Things

Important financial decisions should be visually understandable.

## 7.2 Keep the Primary Action Obvious

The user should immediately know:

- what needs attention,
- what happened,
- what is being recovered,
- and what is blocked.

## 7.3 Make State Visible

Never hide:

- pending,
- verifying,
- unknown,
- suppressed,
- escalated,
- recovered.

## 7.4 Make AI Inspectable

The UI should show:

- recommendation,
- evidence,
- confidence where appropriate,
- policy decision,
- final action.

## 7.5 Never Create False Certainty

An `UNKNOWN` financial state must visually remain unknown.

Do not use a green success style until backend verification confirms success.

---

# 8. Primary Users

The MVP primarily serves:

### Merchant / Operator

Needs to know:

- how much revenue is at risk,
- what RecoverAI is doing,
- which cases require attention,
- how much has been recovered,
- where intervention is blocked.

### Reviewer / Judge

Needs to understand:

- why AI is useful,
- whether execution is bounded,
- how failures are handled,
- how results were measured,
- whether the architecture is trustworthy.

The UI should work for both without creating separate products.

---

# 9. Application Navigation

Primary navigation:

```text
RECOVERAI

Overview
Recovery Cases
Revenue Intelligence
Activity / Audit
Evaluation

SYSTEM
Providers
Workflows
System Health
```

The exact navigation labels may be refined after Stitch exploration.

Keep navigation compact.

Do not create pages that exist only because a backend component exists.

---

# 10. Global Layout

Recommended layout:

```text
┌──────────────────────────────────────────────────────────────┐
│ Logo / Product         Merchant / Demo Mode        Status ● │
├──────────────┬───────────────────────────────────────────────┤
│              │                                               │
│ Navigation   │               Main Content                    │
│              │                                               │
│ Overview     │                                               │
│ Cases        │                                               │
│ Intelligence │                                               │
│ Activity     │                                               │
│ Evaluation   │                                               │
│              │                                               │
│ ───────────  │                                               │
│ System       │                                               │
│ Providers    │                                               │
│ Workflows    │                                               │
│ Health       │                                               │
└──────────────┴───────────────────────────────────────────────┘
```

Desktop should be the primary target because the Buildathon demo will be performed on desktop.

Responsive behavior remains mandatory.

---

# 11. Visual Direction

The visual direction should be:

- dark-first but not purely black,
- high-contrast content areas,
- restrained accent color,
- strong typography,
- generous spacing,
- clear borders,
- subtle elevation,
- compact financial data presentation,
- minimal decorative effects.

Avoid:

- excessive gradients,
- glowing cards everywhere,
- huge animated numbers,
- glassmorphism on every panel,
- excessive rounded containers,
- unnecessary illustrations,
- stock AI imagery.

The dashboard should look like software that controls money.

---

# 12. Color System

Stitch should generate the final palette after exploring the intended design direction.

However, the semantic roles are frozen:

```text
Background
Surface
Surface Elevated
Border
Text Primary
Text Secondary
Text Muted

Success
Warning
Danger
Info

AI / Intelligence Accent
Action Accent
```

Semantic meaning must remain consistent.

For example:

```text
GREEN
= verified success

AMBER
= attention / waiting / degraded

RED
= failure / blocked / dangerous

BLUE/ACCENT
= informational / AI recommendation

NEUTRAL
= inactive / unknown
```

Do not use green to mean "AI recommendation."

Green means verified/healthy success.

---

# 13. Financial Number Styling

Monetary amounts must have high visual prominence.

Example:

```text
₹4,82,500
Verified recovered
```

should visually dominate:

```text
1,204 cases
```

Use:

- tabular numerals where available,
- consistent currency formatting,
- explicit currency,
- no excessive decimal noise for INR display.

Backend values remain integer minor units.

Frontend formats them for presentation.

---

# 14. Typography

Typography should prioritize:

1. number readability,
2. concise operational labels,
3. clear hierarchy.

Recommended hierarchy:

```text
H1
Page title

H2
Major section

H3
Card/section heading

Body
Operational text

Label
Metadata

Micro
Status/helper text
```

The final font selection should be determined through Stitch's design system exploration and then frozen in `DESIGN.md`.

Do not load unnecessary third-party fonts purely for decoration.

---

# 15. Design Tokens

The final Stitch design must produce a reusable design system.

Antigravity should extract or derive:

```text
color tokens
type tokens
spacing tokens
radius tokens
shadow/elevation tokens
motion tokens
component variants
```

Google's Stitch documentation specifically describes `DESIGN.md` as an agent-friendly design-system artifact and the Antigravity Codelab demonstrates extracting the design context into `DESIGN.md`. citeturn749763search0turn749763search4

The generated `DESIGN.md` becomes the implementation-side visual contract.

---

# 16. Design System Rule

No component should independently invent:

```text
color
font
border radius
shadow
spacing
```

when an existing token exists.

The frontend must consume shared tokens.

This prevents the "every card looks different" problem.

---

# 17. Component Architecture

Recommended component categories:

```text
components/
├── layout/
├── navigation/
├── typography/
├── data-display/
├── status/
├── financial/
├── recovery/
├── policy/
├── audit/
├── evaluation/
├── system/
└── feedback/
```

The exact implementation folder structure may vary.

---

# 18. Core Components

The design system should include:

```text
AppShell
Sidebar
TopBar
PageHeader
MetricCard
StatusBadge
SeverityIndicator
MoneyValue
DataTable
Timeline
EvidenceChip
PolicyDecisionCard
RecoveryActionCard
ProviderStatus
WorkflowStatus
AuditEvent
EmptyState
LoadingState
ErrorState
ConfirmDialog
Drawer / SidePanel
Toast
Tooltip
```

These should be reusable rather than page-specific duplicates.

---

# 19. Component State Requirement

Every reusable component that displays dynamic data must define:

```text
default
loading
success/data
empty
error
disabled
unknown
```

where applicable.

For example:

```text
ProviderStatus
    HEALTHY
    DEGRADED
    RATE_LIMITED
    UNAVAILABLE
    UNKNOWN
```

The UI must not accidentally treat `UNKNOWN` as `ERROR` or `SUCCESS`.

---

# 20. Dashboard — Overview

The Overview page is the main judge-facing screen.

Recommended structure:

```text
Overview

[ Revenue at Risk ] [ Verified Recovered ] [ Recovery Rate ] [ Active Cases ]

[ Revenue Recovery Trend ------------------------------ ]

[ Attention Required ]        [ System Health ]

[ Recent Recovery Cases -------------------------------------- ]
```

---

# 21. Overview — Hero Metrics

Primary metrics:

```text
Revenue at Risk
Verified Revenue Recovered
Incremental Recovery
Recovery Rate
```

Secondary metrics:

```text
Active Cases
Escalated
Suppressed
Unknown
```

Do not create ten equal-sized metric cards.

The first four metrics should dominate.

---

# 22. Revenue at Risk Card

Display:

```text
Revenue at Risk
₹X
N eligible cases
```

Optional:

```text
↑ / ↓ vs previous evaluation period
```

only if a meaningful comparison exists.

Do not invent comparison percentages.

---

# 23. Verified Recovery Card

Display:

```text
Verified Recovered
₹X
N cases
```

The word:

```text
VERIFIED
```

is important.

The UI must make clear that this is not:

```text
payment link created
```

but:

```text
financial outcome independently verified
```

---

# 24. Recovery Rate Card

Display:

```text
Recovery Rate
XX.X%
```

with a subtle definition:

```text
Verified recovered amount / eligible amount at risk
```

The exact formula should come from the evaluation/business metric contract.

Do not define a separate UI-only formula.

---

# 25. Attention Panel

Show cases requiring operator attention:

```text
Attention Required

2 High-value approvals
1 Verification unknown
3 Escalated cases
```

Clicking should navigate to filtered Recovery Cases.

---

# 26. System Health Panel

Show compact status:

```text
Razorpay       ● Healthy
LLM Gateway    ● Healthy
n8n            ● Healthy
MCP            ● Healthy
Database       ● Healthy
```

Statuses should come from backend health endpoints.

Do not hardcode them.

---

# 27. Recovery Trend

Use one high-value chart.

Recommended:

```text
Revenue at Risk
vs
Verified Recovered Revenue
```

over a relevant synthetic/test timeline.

Avoid a dashboard containing seven charts.

The chart exists to answer:

> "Is RecoverAI actually recovering more money?"

---

# 28. Recovery Cases Page

The cases page is the operational heart.

Recommended table:

```text
Case
Customer
Amount at Risk
Cause
Recovery Probability
Action
Status
Last Updated
```

Example:

```text
REC-1024
Customer #418
₹5,000
Customer-specific
81%
Payment Link
Verifying
2 min ago
```

---

# 29. Case Filters

Filters:

```text
Status
Cause
Action
Risk Level
Amount Range
Date
Systemic/Customer-specific
```

Do not implement filters that cannot be supported by backend query parameters.

---

# 30. Case Statuses

Visual status vocabulary:

```text
Detected
Assessing
Planning
Awaiting Approval
Executing
Verifying
Recovered
Not Recovered
Suppressed
Escalated
Expired
Unknown
```

Color and icon semantics must remain consistent.

---

# 31. Case Detail Page

The Case Detail view is the most important screen in the product.

Recommended:

```text
┌──────────────────────────────────────────────────────────┐
│ Recovery Case #REC-1024                    [Recovered]   │
│ ₹5,000 at risk                                          │
├───────────────────────┬──────────────────────────────────┤
│ Case Summary          │ Recovery Decision                │
│                       │                                  │
│ failure               │ Recommended Action              │
│ customer context      │ CREATE_PAYMENT_LINK             │
│ system health         │                                  │
│ recovery window       │ Policy: APPROVED                │
├───────────────────────┴──────────────────────────────────┤
│ Timeline / Audit                                         │
├──────────────────────────────────────────────────────────┤
│ Evidence                                                  │
└──────────────────────────────────────────────────────────┘
```

---

# 32. Case Summary

Show:

```text
Amount at Risk
Failure Type
Payment Method
Customer History Summary
Recovery Window
Attempt Count
System Health
Current State
```

Do not expose unnecessary personal data.

---

# 33. Recovery Decision Card

This component must separate:

```text
AI Recommendation
```

from:

```text
Policy Decision
```

Example:

```text
AI Recommendation
CREATE_PAYMENT_LINK

Reason
Customer-specific payment failure with strong historical recovery signal.

Policy
APPROVED

Reason Codes
NO_SYSTEMIC_DEGRADATION
WITHIN_ATTEMPT_LIMIT
WITHIN_RECOVERY_WINDOW
```

This is one of the most important components in the entire UI.

---

# 34. Recommendation vs Authorization

Visual layout:

```text
AI RECOMMENDATION
       ↓
VALIDATED
       ↓
POLICY
       ↓
AUTHORIZED
       ↓
EXECUTED
```

Never present:

```text
AI → EXECUTED
```

as though those are one step.

---

# 35. Evidence Panel

Evidence should be visible but compact.

Example:

```text
Evidence

PAYMENT_FAILED
evt_001

Customer success history
12 / 13 successful payments

System health
No active degradation

Risk assessment
0.81
```

Clicking an evidence item can open its details.

---

# 36. Audit Timeline

The timeline should show:

```text
12:31:04
Payment failed

12:31:05
Recovery case created

12:31:06
Risk assessed

12:31:06
Cause identified

12:31:07
AI recommendation generated

12:31:07
Policy approved

12:31:08
Payment Link created

12:31:16
Payment Link paid

12:31:17
Payment verified

12:31:17
Recovery confirmed
```

Use compact visual nodes and clear actor labels.

---

# 37. Timeline Actor Labels

Examples:

```text
RAZORPAY
REVENUE INTELLIGENCE
LLM
POLICY
N8N
SYSTEM
HUMAN
VERIFICATION
```

This gives the judge immediate understanding of which subsystem acted.

---

# 38. Failure Timeline

A failure should be visually obvious.

Example:

```text
Razorpay Request
      ↓
TIMEOUT ⚠
      ↓
Execution Unknown
      ↓
Reconciliation
      ↓
Payment Link Found
      ↓
Verified
```

Do not make a recovered-after-failure flow look identical to a normal happy path.

The failure and subsequent recovery are part of the engineering story.

---

# 39. Unknown State UI

`UNKNOWN` requires its own visual language.

Example:

```text
⚠ External execution state unknown

We cannot currently establish whether the recovery action completed.

Automatic duplicate execution is blocked.

Next:
Reconciliation / Verification
```

Do not display:

```text
❌ Failed
```

until failure is actually established.

---

# 40. Suppression UI

Example:

```text
Recovery Suppressed

Reason
Active systemic payment degradation

Action
CREATE_PAYMENT_LINK

Decision
SUPPRESS

Why
Intervention is currently unlikely to recover revenue while the payment system is degraded.

Next
Reassess after degradation clears.
```

This is an important trust feature.

---

# 41. Escalation UI

Example:

```text
Human Review Required

Reason
High-value case with ambiguous external state.

Amount
₹75,000

System recommendation
Hold

Policy
WAITING_APPROVAL
```

The user must be able to understand what is blocking progress.

---

# 42. Approval UI

Approval should show:

```text
Amount
Cause
Evidence
Recommended Action
Policy conditions
Potential impact
```

The reviewer should not approve a vague:

```text
"AI wants to take action."
```

Instead:

```text
Approve:
CREATE_PAYMENT_LINK
for ₹X
on Recovery Case REC-1024
```

---

# 43. Evaluation Page

The Evaluation page is for proving the system.

Recommended:

```text
Evaluation Run #001

Dataset
synthetic-v1.0

Cases
1,000

Revenue at Risk
₹X

Verified Recovered Revenue
₹Y

Incremental Recovery
₹Z

vs Rule-Based
+X%

Safety Violations
0
```

---

# 44. Evaluation Comparison

A prominent table:

```text
Strategy          Recovered Revenue     Actions

No Intervention   ₹X                    0
Naive             ₹Y                    N
Rule-Based        ₹Z                    N
RecoverAI         ₹W                    N
```

The exact columns depend on the final evaluator.

---

# 45. Evaluation Scenario Breakdown

Show:

```text
Recoverable Customer Failure
Systemic Degradation
Natural Recovery
High Value
Ambiguous State
Expiry
```

with:

```text
cases
recovered
suppressed
escalated
```

This demonstrates robustness rather than cherry-picked cases.

---

# 46. AI Evaluation

Show only meaningful AI metrics:

```text
Risk Model
PR-AUC
Calibration

Degradation Detector
Precision
Recall

LLM
Structured-output validity
Evidence-grounding rate
Fallback rate
```

Do not display a random "AI Accuracy" number unless its definition is obvious.

---

# 47. Provider Health Page

Show:

```text
Gemini
Healthy
Requests
Fallbacks
Latency

Groq
Healthy
Requests
Fallbacks
Latency

Hugging Face
Available / Degraded
Requests
```

This page supports both operational use and Buildathon proof.

---

# 48. Workflow Page

Show compact n8n workflow status:

```text
Payment Recovery
ACTIVE / IDLE

Payment Verification
ACTIVE / IDLE

Human Approval
3 waiting

Error Handler
Healthy
```

Do not embed the entire n8n editor into the frontend.

The dashboard shows normalized business workflow state.

---

# 49. Audit / Activity Page

Global audit table:

```text
Timestamp
Event
Case
Actor
Status
Reference
```

Examples:

```text
20:14:02
POLICY_APPROVED
REC-1024
POLICY_ENGINE
pd_001

20:14:05
PAYMENT_LINK_CREATED
REC-1024
RAZORPAY
plink_001
```

---

# 50. System Health Page

Show:

```text
Application
Database
Razorpay
Webhook Ingestion
LLM Gateway
MCP
n8n
Evaluation
```

Each should have:

```text
Healthy
Degraded
Unavailable
Unknown
```

and relevant diagnostic information.

---

# 51. Global Status Indicator

Top-right:

```text
SYSTEM ● HEALTHY
```

When degraded:

```text
SYSTEM ● DEGRADED
```

Clicking opens System Health.

This should be subtle and persistent.

---

# 52. Toast Notifications

Use toasts for:

- successful configuration changes,
- copied IDs,
- non-critical state updates.

Do not use toasts as the only presentation for:

- financial failures,
- policy denial,
- verification unknown,
- high-value approval.

Those require persistent page-level state.

---

# 53. Loading States

Every page must have intentional loading states.

Prefer:

```text
skeletons
```

for data-heavy sections.

Avoid:

```text
Loading...
```

centered on an otherwise empty screen for normal page transitions.

---

# 54. Empty States

Example:

```text
No active recovery cases

RecoverAI will surface cases here when revenue is detected at risk.
```

Not:

```text
No data.
```

Empty states should teach the user what the page is for.

---

# 55. Error States

Example:

```text
Unable to load Recovery Cases

The backend could not be reached.

Retry
View System Health
```

Do not display raw stack traces.

---

# 56. Partial Failure

If one widget fails but the page can still render:

```text
Overview

Revenue Metrics     ✓
Recovery Cases      ✓
System Health       ⚠ unavailable
```

Do not blank the entire dashboard because one non-critical endpoint failed.

---

# 57. Backend/API Wiring

The frontend must use a centralized typed API client.

Example conceptual structure:

```text
src/api/
    client
    cases
    metrics
    audit
    evaluation
    health
    approvals
```

Do not scatter `fetch()` calls across arbitrary components.

---

# 58. API Contract Rule

Frontend types should correspond to backend API schemas.

Preferred:

```text
Backend schema
     ↓
generated/centralized TypeScript type
     ↓
frontend component
```

Do not manually redefine the same domain object in five places.

---

# 59. No Hardcoded Backend URLs

Use configuration:

```text
VITE_API_BASE_URL
```

or the equivalent chosen by the actual frontend stack.

Do not hardcode:

```text
http://localhost:8000
```

into components.

---

# 60. No Mock Data in Production Components

Stitch may visually prototype using fake data.

The production implementation must replace that with real API data.

Explicit rule:

> **A finished frontend screen may not use placeholder/demo data unless the data is deliberately seeded through the backend.**

Examples of prohibited final code:

```ts
const recoveredRevenue = 482500;
```

inside a dashboard component.

Correct:

```text
dashboard API
    ↓
real backend response
    ↓
UI
```

---

# 61. Demo Data Rule

The demo can use deterministic seeded data.

That is different from hardcoded frontend values.

Correct:

```text
seed-demo.ps1
    ↓
database
    ↓
API
    ↓
frontend
```

The frontend remains fully wired.

---

# 62. API Loading Contract

Every API call should support:

```text
idle
loading
success
error
```

For long-running operations:

```text
pending
running
completed
failed
```

where appropriate.

---

# 63. Polling / Refresh

The frontend should not poll everything continuously.

Use:

```text
manual refresh
bounded polling
event-driven refresh
```

only where appropriate.

For recovery case execution:

```text
case detail
    ↓
refresh status while active
    ↓
stop polling when terminal
```

The frontend should not create its own infinite polling loops.

---

# 64. Realtime Strategy

The exact implementation may use:

- polling,
- Server-Sent Events,
- WebSockets,

based on actual backend support.

For the MVP, simple bounded polling is acceptable if it gives a reliable demo.

Do not introduce WebSockets merely to appear sophisticated.

---

# 65. Case Detail Refresh

Recommended behavior:

```text
RECOVERED
    ↓
stop active polling

EXECUTING
    ↓
refresh periodically

VERIFYING
    ↓
refresh periodically

UNKNOWN
    ↓
refresh/reconciliation status

TERMINAL
    ↓
stop polling
```

---

# 66. Financial Action Confirmation

For high-impact manual operations, provide a confirmation step.

Example:

```text
Approve Recovery Action

CREATE_PAYMENT_LINK

Amount
₹25,000

Customer
Customer #184

Reason
...

[Cancel] [Approve]
```

No ambiguous "Continue" button.

---

# 67. Destructive Actions

Actions such as:

```text
cancel payment link
suppress recovery
reject approval
```

should have clear confirmation where necessary.

The frontend must never imply that cancellation reverses already-completed financial state.

---

# 68. Accessibility

The frontend must support:

- keyboard navigation,
- visible focus,
- semantic buttons,
- accessible labels,
- adequate contrast,
- non-color-only status communication,
- screen-reader-friendly labels for icons.

Example:

Do not encode status only by:

```text
green dot
```

Use:

```text
● Healthy
```

with accessible text.

---

# 69. Responsive Design

Desktop is primary.

Required responsive breakpoints:

```text
desktop
tablet
mobile
```

On narrow screens:

```text
sidebar
    ↓
collapsible navigation
```

Tables should become:

```text
horizontal scroll
or
stacked cards
```

rather than overflow outside the viewport.

---

# 70. Browser Support

The Buildathon target browser should be:

```text
modern Chromium-based browser
```

The exact browser/version can be confirmed during implementation.

Do not optimize for legacy browsers.

---

# 71. Motion

Motion should be:

- purposeful,
- fast,
- subtle.

Allowed:

```text
page transitions
status changes
drawer opening
chart entrance
loading skeleton shimmer
```

Avoid:

```text
constant background animation
large particle systems
scroll-jacking
excessive spring physics
```

This is financial operations software, not a game.

---

# 72. AI Visual Language

AI-related content should use a subtle dedicated visual cue.

For example:

```text
AI Recommendation
```

with a small accent/icon.

Do not use:

```text
neon purple glow
```

on every AI field.

The visual language should reinforce trust rather than hype.

---

# 73. Policy Visual Language

Policy should look deterministic.

Example:

```text
POLICY APPROVED
v1.2
```

with rule chips:

```text
✓ within recovery window
✓ attempt limit
✓ no systemic degradation
```

This visually communicates that policy is a separate control layer.

---

# 74. Verified Financial State

Verified outcomes should have the strongest success treatment.

Example:

```text
✓ RECOVERED

₹5,000
verified revenue recovered
```

with:

```text
Verification
payment.captured
Razorpay reference
...
```

The UI should connect the amount to evidence.

---

# 75. Unknown Financial State

Unknown should never visually resemble success.

Use:

```text
⚠ UNKNOWN

External execution state has not been established.

Automatic duplicate execution is blocked.
```

The user should understand that the system is intentionally cautious.

---

# 76. Failure Visual Language

Failures should communicate:

```text
what failed
what is currently safe
what happens next
```

Example:

```text
Razorpay timeout

Status
EXECUTION_UNKNOWN

Automatic retry
BLOCKED

Next
Reconcile external state
```

This is much more useful than:

```text
Something went wrong.
```

---

# 77. Dashboard Demo Mode Indicator

During the Buildathon presentation, the UI should visibly indicate:

```text
TEST MODE
```

or:

```text
RAZORPAY TEST MODE
```

This prevents the audience from confusing simulated financial outcomes with live money.

It is also consistent with our honest-results principle.

---

# 78. Evaluation Mode Indicator

When viewing synthetic evaluation:

```text
SYNTHETIC EVALUATION
```

should be prominently visible.

Do not make:

```text
₹4.82L recovered
```

look like a live merchant transaction.

---

# 79. Live Test vs Synthetic

Use clear mode badges:

```text
TEST MODE
SYNTHETIC
DEMO
```

as appropriate.

The application must never silently mix data from these modes.

---

# 80. Data Freshness

Data-heavy views may display:

```text
Updated 12 sec ago
```

where useful.

The exact freshness should come from the API.

Do not display fake timestamps.

---

# 81. Error Recovery UX

When a backend/API call fails:

```text
1. Explain the problem.
2. Preserve already-loaded information.
3. Provide Retry.
4. Provide relevant navigation.
```

Example:

```text
System Health could not be refreshed.

Last known state:
8 seconds ago

[Retry]
```

This is especially important during the live demo.

---

# 82. Network Disconnection UX

If the browser loses connectivity:

```text
Connection lost

The dashboard is showing the last known state.

Reconnecting...
```

Do not silently mutate data based on stale state.

---

# 83. Stale Data Protection

When a user attempts a high-impact action from stale data:

```text
This case changed while you were viewing it.

Refresh before approving the action.
```

This prevents approval based on stale RecoveryCase state.

---

# 84. Optimistic Updates

Do not use optimistic UI for financial state.

For example, after:

```text
Approve
```

do not immediately display:

```text
ACTION EXECUTING
```

unless the backend has actually accepted the command.

Prefer:

```text
request
 ↓
backend response
 ↓
actual state
```

Financial state must be server-authoritative.

---

# 85. Frontend Security Boundary

The frontend must assume:

```text
browser = untrusted client
```

Any UI button can be:

```text
manually invoked
modified
replayed
bypassed
```

Therefore the backend must enforce all authorization and policy.

The frontend is a convenience and observability layer.

---

# 86. UI Does Not Enforce Policy

A hidden/disabled button is not a policy control.

Example:

```text
Approve button hidden
```

does not mean:

```text
action unauthorized
```

The backend must still reject unauthorized requests.

---

# 87. UI Does Not Validate Financial Amount as Authority

A user-visible:

```text
₹5,000
```

is presentation.

The backend's:

```text
amount_at_risk_minor
```

is authoritative.

The API endpoint must not trust the amount sent by the browser.

---

# 88. Frontend State Model

Recommended top-level client state:

```text
session
merchant
systemHealth
dashboardMetrics
cases
activeCase
audit
evaluation
```

Do not create global state for every small component.

Use local component state where appropriate.

---

# 89. Query/Data Layer

The final implementation should centralize server-state fetching and caching.

Possible approaches include:

```text
React Query / TanStack Query
```

or an equivalent typed data-fetching layer.

The final dependency must be selected based on the actual project stack.

Do not add a state-management library simply because it is common.

---

# 90. Form Validation

Forms should validate:

```text
required
type
range
enum
```

client-side for UX.

But the backend must perform the authoritative validation.

---

# 91. Demo-Specific Quick Navigation

Because the Buildathon demo is time-constrained, include a fast route to:

```text
Demo Case 01
Demo Case 02
Failure Case
Evaluation Run
```

This can be through:

```text
Demo Mode
```

or seeded searchable IDs.

Do not build a fake demo-only frontend.

The routes should invoke the same backend system.

---

# 92. Demo Mode Rule

Demo Mode may:

- seed known data,
- highlight relevant cases,
- simplify navigation.

Demo Mode must not:

- bypass policy,
- bypass verification,
- fake outcomes,
- inject frontend-only recovery results.

---

# 93. Visual Verification Loop

The UI implementation must use:

```text
Stitch design
    ↓
Antigravity implementation
    ↓
run frontend
    ↓
integrated browser
    ↓
compare
    ↓
fix
```

Google's current Stitch/Antigravity Codelab explicitly demonstrates this "vibe check" comparison and refinement loop. citeturn749763search0

---

# 94. Visual Verification Checklist

For each major screen compare:

```text
[ ] layout
[ ] spacing
[ ] typography
[ ] color
[ ] border/radius
[ ] iconography
[ ] table density
[ ] button hierarchy
[ ] responsive behavior
[ ] empty state
[ ] loading state
[ ] error state
```

---

# 95. Pixel Accuracy Rule

"Pixel perfect" does not mean:

> hardcoding dimensions everywhere until one screenshot matches.

It means:

```text
design tokens
+
component consistency
+
responsive layout
+
correct spacing
+
correct visual hierarchy
```

The implementation should use semantic/layout primitives rather than screenshot-specific hacks.

---

# 96. Stitch Workflow — Phase 1

Before coding frontend:

### Create Stitch project

Project:

```text
RecoverAI
```

Start with the visual design brief from this document.

Stitch should explore:

```text
dashboard
case detail
evaluation
system health
```

before the entire application is implemented.

---

# 97. Stitch Workflow — Phase 2

Create the design system.

The design system should establish:

```text
palette
type
spacing
radius
elevation
status colors
buttons
inputs
tables
cards
timeline
badges
```

Then apply it consistently.

---

# 98. Stitch Workflow — Phase 3

Create screen designs.

Minimum required screens:

```text
01 Overview
02 Recovery Cases
03 Recovery Case Detail
04 Evaluation
05 Activity / Audit
06 System Health
07 Approval / Review
```

The screens should share one design system.

Do not generate each screen as a separate unrelated aesthetic.

---

# 99. Stitch Workflow — Phase 4

Create interaction flows:

```text
Overview
   ↓
Case
   ↓
Case Detail
   ↓
Recommendation
   ↓
Policy
   ↓
Execution
   ↓
Verification
```

And:

```text
Case
   ↓
Systemic Degradation
   ↓
Suppressed
```

And:

```text
Action
   ↓
Timeout
   ↓
Unknown
   ↓
Reconciliation
```

Stitch supports interactive prototypes and logical screen flows, which should be used to validate the experience before implementation. citeturn749763search4

---

# 100. Stitch Workflow — Phase 5

Connect Stitch to Antigravity using Stitch MCP.

Google's current Codelab documents:

1. create Stitch API key,
2. install Stitch MCP in Antigravity,
3. authenticate/configure it,
4. verify the connection by listing projects,
5. fetch design context,
6. generate `DESIGN.md`. citeturn749763search0

The final exact MCP configuration should follow the current Stitch/Antigravity setup rather than a stale manually copied configuration.

---

# 101. Stitch API Key Security

The Stitch API key must be treated as a secret.

Do not:

```text
commit it
place it in frontend
place it in DESIGN.md
place it in public repo
```

Antigravity's MCP configuration supports authenticated connections and custom headers for remote MCP servers, and access is governed by its MCP permission system. citeturn987678search0turn987678search9

---

# 102. `DESIGN.md`

After connecting Stitch MCP, instruct Antigravity to generate:

```text
DESIGN.md
```

containing:

```text
Design philosophy
Color system
Typography
Spacing
Components
Radius
Elevation
Motion
Layout rules
Responsive rules
Status semantics
```

This file becomes the visual contract for frontend implementation.

Google's current Stitch documentation explicitly describes `DESIGN.md` as an agent-friendly design-system format. citeturn749763search4

---

# 103. Stitch-to-Code Prompt Direction

The Antigravity frontend implementation prompt should say conceptually:

```text
Use the Stitch MCP to fetch the RecoverAI project.

Read the generated DESIGN.md.

Implement the existing RecoverAI frontend architecture using
the Stitch design as the visual source of truth.

Do not create mock business logic.

Wire all dynamic UI to the existing RecoverAI APIs.

Preserve the backend/domain contracts.

Run the application.

Use the integrated browser to compare the implementation to Stitch.

Fix visual discrepancies.

Then run frontend tests.
```

The actual package prompt will be generated later.

---

# 104. Critical Frontend Rule

Do not tell Antigravity:

```text
"Build the frontend from scratch based on this description."
```

while the Stitch project exists.

Instead:

```text
Stitch
=
visual source of truth

Repository
=
functional source of truth

Backend API
=
business truth

DESIGN.md
=
design implementation contract
```

---

# 105. Functional Wiring

The frontend implementation must connect:

```text
Dashboard
     ↓
GET /metrics/overview

Cases
     ↓
GET /recovery-cases

Case Detail
     ↓
GET /recovery-cases/{id}

Audit
     ↓
GET /recovery-cases/{id}/timeline

Evaluation
     ↓
GET /evaluation/runs/{id}

System Health
     ↓
GET /health
```

Exact endpoint names are intentionally placeholders until Package 15 defines the API contract.

The frontend must use the actual implemented API schema.

---

# 106. Frontend/API Contract Freeze

Once Package 15 produces the backend API:

```text
backend API schema
        ↓
frontend API client
        ↓
UI
```

Any API change that breaks frontend integration must be treated as a contract change.

Do not patch around incompatible APIs inside random components.

---

# 107. Mutation Wiring

For user-initiated commands:

```text
Approve Action
    ↓
POST /...
    ↓
backend policy validation
    ↓
actual server state
    ↓
frontend refresh
```

The UI never performs the actual financial operation.

---

# 108. Case Action Wiring

The UI may send:

```text
case_id
action_id
command
```

where appropriate.

It must not send:

```text
Razorpay key
API credentials
authoritative amount override
policy override
```

---

# 109. Frontend Audit Integration

After a mutation:

```text
frontend
    ↓
backend
    ↓
action
    ↓
audit
```

The UI should refresh the case timeline from the backend.

Do not append a fake timeline entry client-side.

---

# 110. Frontend Failure Wiring

Example:

```text
Approve
 ↓
API timeout
```

UI must show:

```text
Command outcome unknown.

Refresh case state before attempting again.
```

It must not show:

```text
Action failed.
```

unless the backend actually established failure.

---

# 111. Unknown Command UX

If a command's result is ambiguous:

```text
Command Status
UNKNOWN

The server has not confirmed whether this operation completed.

You cannot safely retry it yet.

[Refresh]
```

This directly reflects the `EXECUTION_UNKNOWN` architecture.

---

# 112. n8n UI Boundary

The frontend should not implement its own workflow engine.

It may display:

```text
workflow status
next scheduled step
execution reference
```

but the actual workflow remains in n8n.

---

# 113. Provider UI Boundary

The frontend can display:

```text
Gemini
Groq
Hugging Face
```

status and usage.

It must not call provider APIs directly.

---

# 114. MCP UI Boundary

The frontend can display agent/tool activity as audit information.

It must not invoke raw MCP tools from arbitrary browser code.

Browser requests go through RecoverAI backend authorization.

---

# 115. Evaluation Data Safety

The frontend evaluation page can show:

```text
aggregate metrics
scenario breakdown
baseline comparison
```

It should not expose:

```text
hidden ground truth for individual cases
```

unless that result is specifically intended for a finished benchmark report.

The evaluator remains isolated.

---

# 116. Accessibility of Charts

Charts must have:

- accessible labels,
- textual summaries,
- readable axes,
- sufficient contrast,
- non-color-only distinctions.

A chart should have an equivalent summary such as:

```text
RecoverAI recovered ₹X compared with ₹Y for the rule-based baseline.
```

---

# 117. Tables

Tables should:

- support sorting only where useful,
- avoid horizontal clutter,
- use compact row height,
- preserve readable number alignment,
- support keyboard navigation.

Don't make every table infinitely configurable.

---

# 118. Search

Global search is optional.

For MVP, case search should support:

```text
case_id
customer/reference
payment/reference
```

only if these are actual backend query capabilities.

Do not build a universal search engine unnecessarily.

---

# 119. Notifications / Activity

Use an Activity panel for:

```text
new recovered case
approval required
verification unknown
system degraded
```

These should originate from backend state.

---

# 120. Frontend Observability

The frontend should include:

```text
route
API request timing
request failure
frontend error boundary
```

in structured telemetry where appropriate.

Do not log:

```text
API keys
customer secrets
raw payment data
```

---

# 121. Error Boundary

The React application must have an error boundary around major app sections.

If one component crashes:

```text
System Health
```

should remain usable where possible.

The frontend should display:

```text
This section failed to render.

Reload / Retry
```

not a blank white page.

---

# 122. Error Boundary and Audit

Frontend crashes must never alter backend financial state.

A browser failure is:

```text
UI failure
```

not:

```text
financial failure
```

The backend remains the authority.

---

# 123. Performance

The dashboard should:

- avoid huge bundle sizes,
- avoid unnecessary rerenders,
- lazy-load secondary pages,
- avoid rendering thousands of audit events at once.

For large timelines:

```text
pagination
or
virtualization
```

can be used if actually needed.

---

# 124. Performance Rule

Do not optimize before profiling.

The Buildathon priority is:

```text
correctness
+
clarity
+
reliability
```

then performance.

---

# 125. UI/UX Testing

The frontend testing strategy should include:

```text
component tests
API integration tests
critical route tests
accessibility checks
visual/browser verification
```

At minimum, test:

```text
dashboard loads
case list loads
case detail loads
audit timeline renders
evaluation renders
error state renders
unknown state renders
approval flow renders
```

---

# 126. Browser Verification

After implementation, Antigravity should run the frontend and inspect it using its integrated browser capability.

Google's current Antigravity IDE emphasizes browser-based verification and visual iteration as part of its agentic development workflow. citeturn987678search8turn749763search0

The review must compare:

```text
Stitch
vs
actual rendered frontend
```

not:

```text
source code
vs
source code
```

---

# 127. Visual Regression Checklist

For every major screen:

```text
[ ] container width
[ ] sidebar width
[ ] header height
[ ] typography
[ ] color
[ ] spacing
[ ] card density
[ ] table density
[ ] icon sizing
[ ] buttons
[ ] badges
[ ] timeline
[ ] responsive behavior
```

---

# 128. Frontend "No Garbage" Rule

Before accepting the frontend package, reject:

```text
generic dashboard template
random gradients
mismatched components
inconsistent spacing
different border radii
hardcoded demo values
placeholder lorem ipsum
dead buttons
fake loading states
fake metrics
unwired filters
unwired navigation
```

The frontend must feel like one coherent product.

---

# 129. No Dead Interactions

Every visible interactive control must either:

```text
work
```

or:

```text
not exist
```

Do not leave:

```text
<button>Export</button>
```

with no implementation simply because it looks good.

---

# 130. No Fake AI

Do not display:

```text
AI analyzing...
```

just to make the UI feel intelligent.

Only display AI processing state when the backend actually has an active AI operation.

Similarly:

```text
AI confidence 93%
```

must correspond to an actual model output.

---

# 131. No Fake System Health

Do not hardcode:

```text
Razorpay = Healthy
n8n = Healthy
```

The UI must obtain status from backend health.

For demo convenience, deterministic local health is acceptable only if it reflects actual subsystem health.

---

# 132. No Fake Recovery

Do not animate:

```text
₹5,000 recovered
```

until backend verification returns the recovered state.

The financial result must originate from verified backend data.

---

# 133. UI and Audit Trust

The frontend is trustworthy only when:

```text
displayed claim
    =
backend data
    =
audit/evidence
```

The UI should never reinterpret or invent financial state.

---

# 134. Stitch MCP Configuration Boundary

Antigravity's current MCP documentation describes MCP configuration through its MCP manager and workspace/global configuration, with permissions available at tool/server level. citeturn987678search0turn987678search9

For Stitch:

```text
Stitch MCP
    ↓
Design access
```

must be separate from:

```text
RecoverAI runtime MCP
    ↓
Business tools
```

Do not confuse these two MCP servers.

---

# 135. Two MCP Contexts

RecoverAI development uses two conceptually different MCP integrations:

```text
1. STITCH MCP
   Design generation / design context

2. RECOVERAI MCP
   Application tools / agent capabilities
```

They serve completely different purposes.

Their credentials, tools, permissions and responsibilities must remain separate.

---

# 136. Stitch MCP Is Development Tooling

The Stitch MCP is used by Antigravity during frontend design/implementation.

It is not part of the deployed RecoverAI product.

The deployed application does not need a Stitch API key.

This distinction must remain clear.

---

# 137. RecoverAI MCP Is Product Runtime

Our RecoverAI MCP server is part of the agent architecture and may be used by the RecoverAI runtime agent.

It must not receive Stitch credentials.

The two systems are unrelated at runtime.

---

# 138. Frontend Package Implementation Sequence

When Package 16 begins:

```text
1. Inspect current frontend scaffold.
2. Connect/verify Stitch MCP.
3. Create/import RecoverAI Stitch project.
4. Generate design system.
5. Generate DESIGN.md.
6. Generate core screens.
7. Review design.
8. Scaffold/align React components.
9. Wire API client.
10. Implement real data states.
11. Implement loading/error/unknown states.
12. Run browser.
13. Compare to Stitch.
14. Iterate.
15. Test.
16. Verify.
```

Do not start with arbitrary React components before establishing the visual source of truth.

---

# 139. Package 16 Acceptance Criteria

Frontend is complete only when:

```text
1. Stitch project exists.
2. Design system exists.
3. DESIGN.md exists.
4. Core screens are designed.
5. React implementation follows DESIGN.md.
6. Backend APIs are wired.
7. No critical screen uses hardcoded fake data.
8. Loading/empty/error/unknown states exist.
9. Recovery Case timeline works.
10. Policy decision is visibly separated from AI recommendation.
11. Evaluation dashboard uses backend data.
12. System health uses backend data.
13. Responsive layout works.
14. Accessibility basics pass.
15. Browser verification is complete.
16. Visual discrepancies are documented/fixed.
17. Frontend tests exist.
```

---

# 140. Final UI/UX Invariants

```text
UI-001
Frontend never owns financial truth.

UI-002
Frontend never contains provider secrets.

UI-003
AI recommendation and policy authorization remain visually distinct.

UI-004
UNKNOWN is never presented as FAILED or SUCCESS.

UI-005
RECOVERED is only shown after backend verification.

UI-006
Synthetic results are visibly labelled SYNTHETIC.

UI-007
Razorpay integration is visibly labelled TEST MODE during demo.

UI-008
Frontend never bypasses application authorization.

UI-009
Interactive controls do not exist without real behavior.

UI-010
Displayed metrics originate from backend/evaluation data.

UI-011
Stitch design tokens are shared across screens.

UI-012
Visual design remains coherent across all pages.

UI-013
Failure states explain what happened and what happens next.

UI-014
High-impact actions require explicit confirmation/authorization where policy requires it.

UI-015
The UI must remain useful when optional services are degraded.
```

---

# 141. Freeze Decisions

The following are frozen:

1. Google Stitch is the visual design source of truth.
2. Stitch MCP is used by Antigravity to transfer design context.
3. Antigravity generates/maintains `DESIGN.md` from the Stitch design.
4. The frontend is implemented using the project's chosen React/TypeScript/Tailwind stack.
5. Backend APIs remain the source of business truth.
6. No frontend component may invent financial state.
7. No provider credential reaches the frontend.
8. AI recommendations and deterministic policy decisions are visually separate.
9. `UNKNOWN` receives a distinct visual state.
10. `RECOVERED` requires backend verification.
11. Synthetic evaluation is visibly labelled.
12. Razorpay Test Mode is visibly labelled during demo.
13. n8n is represented through normalized workflow state, not embedded as the application's business engine.
14. RecoverAI MCP and Stitch MCP remain separate concerns.
15. The final UI must be browser-verified against Stitch.
16. Hardcoded demo metrics are forbidden in production components.
17. Dead interactive elements are forbidden.
18. The dashboard prioritizes revenue, decisions, safety, system health and auditability over decorative content.
19. The frontend should feel like a financial operations product, not a generic AI dashboard.
20. Package 16 cannot be considered complete until real backend wiring and visual verification both pass.

---

# 142. External References

## Google Stitch

### Official Google Labs — Stitch updates
https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-updates/

Google's May 19, 2026 update describes Stitch's real-time design workflow, collaborative design agent, and export from Stitch into Google Antigravity. citeturn749763search1

### Official Google Labs — Stitch design
https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-ai-ui-design/

Google describes Stitch as an AI-native design canvas for high-fidelity UI, its design agent, `DESIGN.md`, interactive prototyping, and design-to-code workflows using MCP and developer tools. citeturn749763search4

### Google Codelab — Design-to-Code with Antigravity and Stitch MCP
https://codelabs.developers.google.com/design-to-code-with-antigravity-stitch

This is the primary implementation reference for RecoverAI's frontend process. It explicitly demonstrates:

- high-fidelity UI generation in Stitch,
- Stitch MCP installation/configuration in Antigravity,
- fetching Stitch design context,
- generating `DESIGN.md`,
- implementing a React/Tailwind application,
- and browser-based visual verification/refinement. citeturn749763search0

---

## Google Antigravity

### MCP
https://antigravity.google/docs/mcp

Current Antigravity MCP documentation describes MCP server installation/configuration, permissions, local/workspace configuration, and tool access. citeturn987678search0

### IDE Overview
https://antigravity.google/docs/ide/overview/

Current Antigravity documentation describes agentic end-to-end development including UI iteration, implementation, browser verification and higher-level artifacts. citeturn987678search8

### Permissions
https://antigravity.google/docs/cli-permissions

Current Antigravity documentation describes per-MCP-server/tool permissions and default Ask-mode behavior. citeturn987678search9

---

# 143. Verification Status

## VERIFIED

- Current Stitch → Antigravity MCP workflow.
- Current Stitch `DESIGN.md` design-system workflow.
- Current Stitch high-fidelity design/prototyping capabilities.
- Current Stitch-to-React/Tailwind implementation workflow.
- Current Antigravity MCP configuration/permission model.
- Current Antigravity browser-based development/verification workflow.

## PROPOSED

- Exact frontend framework/version.
- Exact Tailwind version.
- Exact font selection.
- Exact color palette.
- Exact final Stitch design system.
- Exact API endpoint names.
- Exact frontend state-management library.
- Exact realtime/polling mechanism.
- Exact screen routing structure.

## NOT YET IMPLEMENTED

The Stitch project, final Stitch design system, `DESIGN.md`, frontend scaffold, components, API wiring, and visual verification.

## CRITICAL

The frontend must be implemented from **two sources of truth**:

```text
STITCH
=
visual truth

RECOVERAI BACKEND
=
functional/business truth
```

Neither may replace the other.

A beautiful Stitch-generated interface with fake data is not a completed frontend.

A fully wired frontend that ignores the Stitch design is also not a completed frontend.

The Package 16 goal is:

> **A visually exceptional, coherent, responsive, judge-friendly React application whose every important number, state, action, failure and audit event comes from the real RecoverAI backend.**
